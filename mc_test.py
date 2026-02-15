from javascript import require, On
import time
mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')

bot = mineflayer.createBot({
	'host': '152.228.198.208',
	'username': 'Bot',
	'auth': 'offline',
	'port': '22239',
})

bot.loadPlugin(pathfinder.pathfinder)
print("Started mineflayer")

movements = None
last_attack_time = 0
attacking = False
last_health_check = 0

@On(bot, 'spawn')
def handle(*args):
	global movements
	print("I spawned 👋")
	movements = pathfinder.Movements(bot)
	
	@On(bot, 'chat')
	def handleMsg(this, sender, message, *args):
		print("Got message", sender, message)
		if sender and (sender != bot.username):
			bot.chat('Hi, you said ' + message)
			if 'come' in message:
				player = bot.players[sender]
				print("Target", player)
				target = player.entity
				if not target:
					bot.chat("I don't see you !")
					return
				pos = target.position
				bot.pathfinder.setMovements(movements)
				try: bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, 5))
				except: 
					print("I couldn't reach you")
					bot.chat("I couldn't reach you")
			elif 'attack me' in message:
				attackplayer2(sender)
			elif 'stop' in message:
				stop_attacking()
			elif 'nearby' in message:
				list_nearby_entities()

# Detect when bot takes damage
@On(bot, 'health')
def on_health(*args):
	global last_health_check
	current_time = time.time()
	
	# Only check for attackers every 2 seconds to avoid spam
	if current_time - last_health_check < 2:
		print(f"Health changed! HP: {bot.health}, Food: {bot.food} (cooldown active)")
		return
	
	print(f"Health changed! HP: {bot.health}, Food: {bot.food}")
	last_health_check = current_time
	
	# Find who attacked us
	attacker = find_attacker()
	if attacker:
		# Get username if it's a player
		username = get_entity_username(attacker)
		
		# Don't attack yourself!
		if username == bot.username:
			print("Ignoring self as attacker")
			return
		
		print(f"⚠️ Being attacked by: {username} (type: {attacker.type}, ID: {attacker.id})")
		bot.chat(f"I'm being attacked by {username}!")
		
		# Auto attack back if not already attacking
		if not attacking and username:
			print(f"Fighting back against {username}!")
			attackplayer2(username)

def get_entity_username(entity):
	"""Get the username of a player entity"""
	if entity.type != 'player':
		return entity.type
	
	# Search through bot.players to find matching entity
	for username in bot.players:
		player = bot.players[username]
		if player.entity and player.entity.id == entity.id:
			return username
	
	return entity.username or entity.name or 'Unknown Player'

def find_attacker():
	"""Find the entity that's attacking the bot"""
	if not bot.entity or not bot.entity.position:
		return None
	
	# Get bot's ID safely
	bot_id = bot.entity.id if bot.entity and hasattr(bot.entity, 'id') else None
	
	# Get all nearby entities
	entities = bot.entities
	if not entities:
		return None
	
	closest_hostile = None
	min_distance = 10  # Only check entities within 10 blocks
	
	for entity_id in entities:
		entity = entities[entity_id]
		
		# Skip if entity is None
		if not entity:
			continue
		
		# Skip if it's the bot itself
		if entity == bot.entity:
			continue
		
		# Check entity ID if both exist
		if bot_id and hasattr(entity, 'id') and entity.id and entity.id == bot_id:
			continue
		
		# Check if entity has position
		if not hasattr(entity, 'position') or not entity.position or not bot.entity.position:
			continue
		
		# Additional check before distanceTo
		try:
			distance = bot.entity.position.distanceTo(entity.position)
		except:
			continue
		
		# Check if it's close and potentially hostile
		entity_type = entity.type if hasattr(entity, 'type') else None
		if not entity_type:
			continue
			
		# Hostile mobs or players
		if entity_type in ['player', 'zombie', 'skeleton', 'creeper', 'spider', 'enderman', 'witch', 'slime']:
			if not closest_hostile or distance < min_distance:
				closest_hostile = entity
				min_distance = distance
	
	return closest_hostile

def list_nearby_entities():
	"""List all entities near the bot"""
	if not bot.entity or not bot.entity.position:
		bot.chat("Can't detect position!")
		return
	
	print("\n=== NEARBY ENTITIES ===")
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
		
		if distance <= 20:  # Within 20 blocks
			name = entity.name or entity.displayName or entity.type
			nearby.append((name, entity.type, distance))
	
	# Sort by distance
	nearby.sort(key=lambda x: x[2])
	
	for name, entity_type, dist in nearby:
		print(f"  - {name} ({entity_type}) - {dist:.1f} blocks away")
	
	print("========================\n")
	bot.chat(f"Found {len(nearby)} entities nearby!")

def get_best_weapon():
	# Weapon priority order
	weapons = ['netherite_sword', 'diamond_sword', 'iron_sword', 'stone_sword', 'wooden_sword', 
	           'netherite_axe', 'diamond_axe', 'iron_axe', 'stone_axe', 'wooden_axe']
	
	# List all items in inventory
	print("\n=== INVENTORY ===")
	items = bot.inventory.items()
	for item in items:
		print(f"  - {item.name} x{item.count}")
	print("=================\n")
	
	# Find best weapon
	for weapon in weapons:
		for item in items:
			if item.name == weapon:
				print(f"Found best weapon: {weapon}")
				return item
	
	print("No weapon found")
	return None

def stop_attacking():
	global attacking
	attacking = False
	bot.pathfinder.setGoal(None)
	bot.chat("Stopped attacking!")
	print("Stopped attacking")

def attackplayer2(sender):
	global last_attack_time, attacking
	
	if not bot.pathfinder:
		print("Pathfinder not available!")
		bot.chat("I can't pathfind right now!")
		return
	
	player = bot.players[sender]
	if not player:
		bot.chat(f"Can't find player {sender}")
		return
		
	target = player.entity
	if not player.entity:
		bot.chat('I can\'t see you')
		return
	
	# Equip best weapon
	best_weapon = get_best_weapon()
	if best_weapon:
		try:
			bot.equip(best_weapon, 'hand')
			print(f'Equipped {best_weapon.name}!')
		except Exception as e:
			print(f"Failed to equip weapon: {e}")
	
	print(f'Attacking {player.username}!')
	attacking = True
	
	# Use GoalFollow to chase the player
	bot.pathfinder.setMovements(movements)
	bot.pathfinder.setGoal(pathfinder.goals.GoalFollow(target, 2), True)
	
	# Use physicsTick event to keep attacking while following
	@On(bot, 'physicsTick')
	def keep_attacking(*args):
		global last_attack_time, attacking
		
		if not attacking:
			return
		
		player = bot.players[sender]
		if not player or not player.entity:
			print(f"{sender} died or left!")
			stop_attacking()
			return
		
		target = player.entity
		
		# Check if bot.entity and positions exist
		if not bot.entity or not bot.entity.position:
			return
		
		# Store position in variable to avoid it becoming undefined
		target_pos = target.position
		if not target_pos:
			print(f"{sender} position unavailable, probably died!")
			stop_attacking()
			return
		
		try:
			distance = bot.entity.position.distanceTo(target_pos)
		except:
			return
		
		# Only attack if close enough
		if distance <= 4:
			eye_pos = target_pos.offset(0, target.height, 0)
			bot.lookAt(eye_pos)
			
			# Attack with cooldown (500ms = 0.5 seconds)
			current_time = time.time()
			if current_time - last_attack_time >= 0.5:
				bot.attack(target)
				last_attack_time = current_time

@On(bot, "end")
def handle(*args):
	print("Bot ended!", args)