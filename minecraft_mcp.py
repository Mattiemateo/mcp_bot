from turtle import pos

from javascript import require, On
from mcp.server.fastmcp import Context, FastMCP
import asyncio
import time

def MakeBot(name: str):
    global bot
    bot = mineflayer.createBot({
    	'host': '152.228.198.208', # minecraft server ip
    	'username': name,
    	'auth': 'offline',
    	'port': '22239',
    })

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder-mai')

mcData = None
global movements

MakeBot("chopper")

message_list = ["this is a test message"]

mcp = FastMCP(name="Minecraft chat helper")
bot.loadPlugin(pathfinder.pathfinder)

@On(bot, 'spawn')
def handle(*args):
    print("I spawned 👋")
    
    global mcData
    print("I spawned 👋")
    
    # Load minecraft data for block IDs
    mcData = require('minecraft-data')(bot.version)
    # Print oak_log info
    oak_item = mcData.itemsByName['oak_log']
    print(f"Oak log item ID: {oak_item.id}")
    print(f"Oak log name: {oak_item.name}")
    print(f"Oak log display name: {oak_item.displayName}")
    
    bot.waitForChunksToLoad()
    print("Chunks loaded!")

    movements = pathfinder.Movements(bot)
    
    @On(bot, 'chat')
    def handleMsg(this, sender, message, *args):
        message_list.append(message)
        if len(message_list) > 5:
            _ = message_list.pop(0)

        print ("got", message, "from", sender)

        if sender != bot.username and sender:
            if "come here" == message:
                movements = pathfinder.Movements(bot)
                player = bot.players[sender]
                target = player.entity
                pos = target.position
                bot.pathfinder.setMovements(movements)
                try :
                    goto(pos.x, pos.y, pos.z, 1)
                except:
                    print("fuckkkkkk")
                    bot.chat("fuckkkkk")
            elif 'find tree' == message:
                tree = get_tree(('oak'))
                mine_tree(tree)
                #pickup_block()
            elif 'find dirt' == message:
                find_block('dirt')
            elif 'find stone' == message:
                find_block('stone')
            elif 'goto tree' == message:
                find_block('tree')
            elif "#inventory drop" in message:
                item_to_drop = message.replace('#inventory drop ', '').strip()
                bot.toss(885)
                #bot.toss(134)
            elif message == '#inventory list':
                # List all items in inventory
                print("\n=== INVENTORY ===")
                bot.chat("=== INVENTORY ===")
                items = bot.inventory.items()
                for item in items:
                    print(f"  - {item.name} x{item.count}")
                    bot.chat(f"  - {item.name} x{item.count}")
                    time.sleep(1)
                bot.chat("=================")
                print("=================\n")
            elif 'open chest' in message:
                goto(-329, 63, -376, 1)
                #time.sleep(10)
                deposit_chest_at_coords(-329, 63, -376)
            elif message == 'loop tree':
                mine_amount_trees(100)
            elif 'pickup' in message:
                pickup()

def deposit_chest_at_coords(x, y, z):
    """Open chest at specific coordinates."""
    # Find blocks matching chest nearby
    
    # Find the chest block at those exact coordinates
    chest_blocks = bot.findBlocks({
        'matching': mcData.blocksByName['chest'].id,
        'maxDistance': 64,
        'count': 100
    })
    
    # Find the one at our target coordinates
    chest_block = None
    for i in range(chest_blocks.length):
        pos = chest_blocks[i]
        if pos.x == x and pos.y == y and pos.z == z:
            chest_block = bot.blockAt(pos)
            break
    
    if not chest_block:
        print(f"No chest found at {x}, {y}, {z}")
        bot.chat("No chest there!")
        return None
    
    print(f"Found chest: {chest_block.name}")
    
    # Open it
    try:
        container = bot.openContainer(chest_block)
        print("Chest opened!")
        bot.chat("Chest opened!")
    except Exception as e:
        print(f"Failed to open: {e}")
        return None
    if container:
        # Deposit all items except tools
        for item in bot.inventory.items():
            if item and item.name == 'oak_log':
                try:
                    container.deposit(item.type, None, item.count)
                    print(f"Deposited {item.count} of {item.name}")
                except Exception as e:
                    print(f"Failed to deposit {item.name}: {e}")
        container.close()
        print("Finished depositing!")

def get_best_axe():
	# Weapon priority order
	axes = ['netherite_axe', 'diamond_axe', 'iron_axe', 'stone_axe', 'wooden_axe']
	
	items = bot.inventory.items()
	
	# Find best weapon
	for axe in axes:
		for item in items:
			if item.name == axe:
				print(f"Found best weapon: {axe}")
				return item
	
	print("No weapon found")
	return None

def find_block(block_name, max_distance=64, count=10):

    global mcData
    
    # Load minecraft data for block IDs
    if not mcData:
        mcData = require('minecraft-data')(bot.version)
    
    print(f"Searching for {block_name}...")
    
    # Get the block type from minecraft-data
    blockType = mcData.blocksByName[block_name]
    
    if not blockType:
        print(f"Unknown block: {block_name}")
        return []
    
    bot_pos = bot.entity.position
    
    # Use numeric ID for matching
    positions = bot.findBlocks({
        'matching': blockType.id,
        'maxDistance': max_distance,
        'count': count
    })
    
    if not positions or positions.length == 0:
        print(f"No {block_name} found")
        return []
    
    # Build result list
    results = []
    print(f"Found {positions.length} {block_name} blocks:")
    
    for i in range(positions.length):
        pos = positions[i]
        distance = bot_pos.distanceTo(pos)
        block = bot.blockAt(pos)
        
        result = {
            'x': pos.x,
            'y': pos.y,
            'z': pos.z,
            'distance': distance,
            'block': block
        }
        results.append(result)
        
        if i < 5:  # Only print first 5
            print(f"  [{i}] x={pos.x}, y={pos.y}, z={pos.z} (distance: {distance:.1f})")
    
    return results

def goto(x, y, z, radius=0.5):
    #movements = pathfinder.Movements(bot)
    #bot.pathfinder.setMovements(movements)
    #movements.scafoldingBlocks = (bot.registry.itemsByName['dirt'].id, bot.registry.itemsByName['netherrack'].id)
    while True:
        try:
            movements = pathfinder.Movements(bot)
            bot.pathfinder.setMovements(movements)
            movements.scafoldingBlocks = (bot.registry.itemsByName['dirt'].id, bot.registry.itemsByName['netherrack'].id)
            bot.pathfinder.setGoal(pathfinder.goals.GoalNear(x, y, z, radius))
            break  # worked, move on
        except:
            print("fuckkkk")
            bot.chat("fuckkkkk")
            pass  # failed, try again
        
def get_tree(type = 'oak'):
    tree = []
    logs = find_block(f'{type}_log', max_distance=32, count=10)
    if not logs:
        print(f"No {type} trees found nearby")
        logs = find_block(f'{type}_log', max_distance=64, count=10)
        if not logs:
            return None
    
    tree = [logs[0]]  # Start with closest log
    
    for log in logs[1:]:
        dx = abs(log['x'] - logs[0]['x'])
        dy = abs(log['y'] - logs[0]['y'])
        dz = abs(log['z'] - logs[0]['z'])
        
        if dx <= 1.5 and dy <= 10 and dz <= 1.5:
            tree.append(log)
        
    print(f"Found {len(tree)} logs for {type} tree")
    tree.sort(key=lambda log: log['y'])  # Sort by height (y) descending
    print(tree)
    return tree

def mine_tree(tree):
    best_weapon = get_best_axe()
    try:
        bot.equip(best_weapon, 'hand')
        print(f'Equipped {best_weapon.name}!')
    except Exception as e:
        print(f"Failed to equip weapon: {e}")
    if not tree:
        print("No tree to mine")
        return
    for log in tree:
        goto(log['x'], log['y'], log['z'], 4)
        time.sleep(1)
        if not bot.pathfinder.isMoving():
            print("Arrived at log, mining...")

            try:
                bot.equip(best_weapon, 'hand')
                print(f'Equipped {best_weapon.name}!')
            except Exception as e:
                print(f"Failed to equip weapon: {e}")

            try:
                t = bot.digTime(log['block'])
                bot.dig(log['block'])
                time.sleep(t/1000 + 1)  # Wait for mining to finish
            except Exception as e:
                print(f"Failed to mine block: {e}")
        print("mining log")
        #time.sleep(10)

def pickup():
    print("pickup")
    item = bot.nearestEntity(
        lambda entity: entity.name == 'item' and entity.metadata and entity.metadata[7] and entity.metsadata[7].itemId == 68
    )
    print(item)
    if item:
        goto(item.position.x, item.position.y, item.position.z)
    else:
        bot.chat("no items found")

'''def pickup():
    print("pickup")
    item = bot.nearestEntity(
        lambda entity: entity.name == 'item',
        lambda item: item.metadata.itemId == "28"
        )
    print(item)
    if item:
        #print(str(item))  # or however you access the name
        goto(item.position.x, item.position.y, item.position.z)
    else:
        bot.chat("no items found")

    # const cow = bot.nearestEntity(entity => entity.name.toLowerCase() === 'cow') // we use .toLowercase() because in 1.8 cow was capitalized, for newer versions that can be omitted
    # cow = bot.nearestEntity(lambda entity: entity.name.lower() == 'cow')
    # item = bot.nearestEntity(lambda entity: entity.name == 'item')
'''
    
def mine_amount_trees(amount:int = 5, type: str ='oak'):
    loop_amount_shit_fuckkkkkkk = amount
    while loop_amount_shit_fuckkkkkkk:
        tree = get_tree(('oak'))
        mine_tree(tree)
        time.sleep(1)
        pickup()
        time.sleep(2)
        loop_amount_shit_fuckkkkkkk -= 1 
        
@On(bot,'end')
def OnEnd(reason, *args):
    print('kicked')
    #print("kicked for" + str(reason))
    #MakeBot('choppah')

@mcp.tool()
async def send_message(message: str, ctx: Context) -> str:
    bot.chat(message)
    await ctx.info(f"sending message")
    out = f"message {message} has been sent"
    return out

@mcp.tool()
async def read_messages(ctx: Context) -> list:
    await ctx.info(f"reading messages")
    return message_list
    

if __name__ == "__main__":
    mcp.run(transport="sse")
