from javascript import require, On
import time
mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')

# Configuration
NUM_BOTS = 3  # Number of bots to create
SERVER_HOST = '152.228.198.208'
SERVER_PORT = '22239'

# Whitelist - players the bots won't attack
WHITELIST = ['mattiemateo', 'Bot', 'Bot1', 'Bot2', 'chleese_', 'Bot3', 'Bot4', 'Bot5', 'chatter']

# Store all bots
bots = []
bot_data = {}  # Store per-bot data

def create_bot(bot_number):
	"""Create and configure a single bot"""
	bot_name = f"Bot{bot_number}"
	
	bot = mineflayer.createBot({
		'host': SERVER_HOST,
		'username': bot_name,
		'auth': 'offline',
		'port': SERVER_PORT,
	})
	
	bot.loadPlugin(pathfinder.pathfinder)
	print(f"Started {bot_name}")
	
	# Initialize bot-specific data
	bot_data[bot_name] = {
		'movements': None,
		'last_attack_time': 0,
		'attacking': False,
		'last_health_check': 0
	}
	
	@On(bot, 'spawn')
	def handle(*args):
		print(f"{bot_name} spawned 👋")
		bot_data[bot_name]['movements'] = pathfinder.Movements(bot)
		
		@On(bot, 'chat')
		def handleMsg(this, sender, message, *args):
			print(f"{bot_name} got message from {sender}: {message}")
			if sender and (sender != bot.username):
				if 'come' in message:
					player = bot.players[sender]
					target = player.entity
					if not target:
						bot.chat("I don't see you !")
						return
					pos = target.position
					bot.pathfinder.setMovements(bot_data[bot_name]['movements'])
					try: 
						bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, 5))
					except: 
						print(f"{bot_name} couldn't reach you")
						bot.chat("I couldn't reach you")
				elif message.startswith('attack '):
					target_username = message.replace('attack ', '').strip()
					if target_username:
						attackplayer(bot, bot_name, target_username)
					else:
						bot.chat("Who should I attack?")
				elif 'attack me' in message:
					attackplayer(bot, bot_name, sender)
				elif 'stop' in message:
					stop_attacking(bot, bot_name)
				elif 'nearby' in message:
					list_nearby_entities(bot, bot_name)
	
	# Detect when bot takes damage
	@On(bot, 'health')
	def on_health(*args):
		current_time = time.time()
		
		# Only check for attackers every 2 seconds to avoid spam
		if current_time - bot_data[bot_name]['last_health_check'] < 2:
			print(f"{bot_name} health changed! HP: {bot.health}, Food: {bot.food} (cooldown active)")
			return
		
		print(f"{bot_name} health changed! HP: {bot.health}, Food: {bot.food}")
		bot_data[bot_name]['last_health_check'] = current_time
		
		# Find who attacked us
		attacker = find_attacker(bot, bot_name)
		if attacker:
			username = get_entity_username(bot, attacker)
			
			if username == bot.username:
				print(f"{bot_name} ignoring self as attacker")
				return
			
			print(f"{bot_name} ⚠️ Being attacked by: {username} (type: {attacker.type}, ID: {attacker.id})")
			bot.chat(f"I'm being attacked by {username}!")
			
			if not bot_data[bot_name]['attacking'] and username and username not in WHITELIST:
				print(f"{bot_name} fighting back against {username}!")
				attackplayer(bot, bot_name, username)
			elif username in WHITELIST:
				print(f"{bot_name}: {username} is whitelisted, not fighting back")
	
	@On(bot, "end")
	def handle(*args):
		print(f"{bot_name} ended!", args)
	
	return bot

def get_entity_username(bot, entity):
	"""Get the username of a player entity"""
	if entity.type != 'player':
		return entity.type
	
	for username in bot.players:
		player = bot.players[username]
		if player.entity and player.entity.id == entity.id:
			return username
	
	return entity.username or entity.name or 'Unknown Player'

def find_attacker(bot, bot_name):
	"""Find the entity that's attacking the bot"""
	if not bot.entity or not bot.entity.position:
		return None
	
	bot_id = bot.entity.id if bot.entity and hasattr(bot.entity, 'id') else None
	entities = bot.entities
	if not entities:
		return None
	
	closest_hostile = None
	min_distance = 10
	
	for entity_id in entities:
		entity = entities[entity_id]
		
		if not entity:
			continue
		if entity == bot.entity:
			continue
		if bot_id and hasattr(entity, 'id') and entity.id and entity.id == bot_id:
			continue
		if not hasattr(entity, 'position') or not entity.position or not bot.entity.position:
			continue
		
		try:
			distance = bot.entity.position.distanceTo(entity.position)
		except:
			continue
		
		entity_type = entity.type if hasattr(entity, 'type') else None
		if not entity_type:
			continue
			
		if entity_type in ['player', 'zombie', 'skeleton', 'creeper', 'spider', 'enderman', 'witch', 'slime']:
			if not closest_hostile or distance < min_distance:
				closest_hostile = entity
				min_distance = distance
	
	return closest_hostile

def list_nearby_entities(bot, bot_name):
	"""List all entities near the bot"""
	if not bot.entity or not bot.entity.position:
		bot.chat("Can't detect position!")
		return
	
	print(f"\n=== {bot_name} NEARBY ENTITIES ===")
	entities = bot.entities
	nearby = []
	
	for entity_id in entities:
		entity = entities[entity_id]
		if entity == bot.entity:
			continue
		
		if not entity or not entity.position:
			continue
		
		try:
			distance = bot.entity.position.distanceTo(entity.position)
		except:
			continue
		
		if distance <= 20:
			name = entity.name or entity.displayName or entity.type
			nearby.append((name, entity.type, distance))
	
	nearby.sort(key=lambda x: x[2])
	
	for name, entity_type, dist in nearby:
		print(f"  - {name} ({entity_type}) - {dist:.1f} blocks away")
	
	print("========================\n")
	bot.chat(f"Found {len(nearby)} entities nearby!")

def get_best_weapon(bot, bot_name):
	weapons = ['netherite_sword', 'diamond_sword', 'iron_sword', 'stone_sword', 'wooden_sword', 
	           'netherite_axe', 'diamond_axe', 'iron_axe', 'stone_axe', 'wooden_axe']
	
	print(f"\n=== {bot_name} INVENTORY ===")
	items = bot.inventory.items()
	for item in items:
		print(f"  - {item.name} x{item.count}")
	print("=================\n")
	
	for weapon in weapons:
		for item in items:
			if item.name == weapon:
				print(f"{bot_name} found best weapon: {weapon}")
				return item
	
	print(f"{bot_name} no weapon found")
	return None

def stop_attacking(bot, bot_name):
	bot_data[bot_name]['attacking'] = False
	bot.pathfinder.setGoal(None)
	bot.chat("Stopped attacking!")
	print(f"{bot_name} stopped attacking")

def attackplayer(bot, bot_name, target_username):
	if target_username in WHITELIST:
		bot.chat(f"{target_username} is protected!")
		print(f"{bot_name} cannot attack {target_username} - they are whitelisted")
		return
	
	if not bot.pathfinder:
		print(f"{bot_name} pathfinder not available!")
		bot.chat("I can't pathfind right now!")
		return
	
	if not bot_data[bot_name]['movements']:
		print(f"{bot_name} movements not initialized!")
		bot.chat("I'm not ready yet!")
		return
	
	player = bot.players[target_username] if target_username in bot.players else None
	
	if not player:
		bot.chat(f"Can't find player {target_username}")
		print(f"{bot_name} player {target_username} not found")
		return
		
	target = player.entity
	if not player.entity:
		bot.chat(f'I can\'t see {target_username}')
		return
	
	best_weapon = get_best_weapon(bot, bot_name)
	if best_weapon:
		try:
			bot.equip(best_weapon, 'hand')
			print(f'{bot_name} equipped {best_weapon.name}!')
		except Exception as e:
			print(f"{bot_name} failed to equip weapon: {e}")
	
	bot.chat(f'Attacking {target_username}!')
	print(f'{bot_name} attacking {target_username}!')
	bot_data[bot_name]['attacking'] = True
	
	try:
		bot.pathfinder.setMovements(bot_data[bot_name]['movements'])
		bot.pathfinder.setGoal(pathfinder.goals.GoalFollow(target, 2), True)
	except Exception as e:
		print(f"{bot_name} failed to set pathfinding goal: {e}")
		bot.chat("I couldn't start moving!")
		bot_data[bot_name]['attacking'] = False
		return
	
	@On(bot, 'physicsTick')
	def keep_attacking(*args):
		if not bot_data[bot_name]['attacking']:
			return
		
		player = bot.players[target_username] if target_username in bot.players else None
		if not player or not player.entity:
			print(f"{bot_name}: {target_username} died or left!")
			stop_attacking(bot, bot_name)
			return
		
		target = player.entity
		
		if not bot.entity or not bot.entity.position:
			return
		
		target_pos = target.position
		if not target_pos:
			print(f"{bot_name}: {target_username} position unavailable!")
			stop_attacking(bot, bot_name)
			return
		
		try:
			distance = bot.entity.position.distanceTo(target_pos)
		except:
			return
		
		if distance <= 4:
			eye_pos = target_pos.offset(0, target.height, 0)
			bot.lookAt(eye_pos)
			
			current_time = time.time()
			if current_time - bot_data[bot_name]['last_attack_time'] >= 0.5:
				bot.attack(target)
				bot_data[bot_name]['last_attack_time'] = current_time

# Create all bots
print(f"Creating {NUM_BOTS} bots...")
for i in range(1, NUM_BOTS + 1):
	bot = create_bot(i)
	bots.append(bot)

print(f"Army of {NUM_BOTS} bots created!")