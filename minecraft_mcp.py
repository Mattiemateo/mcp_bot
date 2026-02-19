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
            if "come here" in message:
                movements = pathfinder.Movements(bot)
                player = bot.players[sender]
                target = player.entity
                pos = target.position
                bot.pathfinder.setMovements(movements)
                try :
                    bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, 1))
                except:
                    print("fuckkkkkk")
                    bot.chat("fuckkkkk")
            elif 'find tree' in message:
                mine_tree(get_tree('oak'))
            elif 'find dirt' in message:
                find_block('dirt')
            elif 'find stone' in message:
                find_block('stone')
            elif 'goto tree' in message:
                find_block('stone')


def get_best_axe():
	# Weapon priority order
	axes = ['netherite_axe', 'diamond_axe', 'iron_axe', 'stone_axe', 'wooden_axe']
	
	# List all items in inventory
	print("\n=== INVENTORY ===")
	items = bot.inventory.items()
	for item in items:
		print(f"  - {item.name} x{item.count}")
	print("=================\n")
	
	# Find best weapon
	for axe in axes:
		for item in items:
			if item.name == axe:
				print(f"Found best weapon: {axe}")
				return item
	
	print("No weapon found")
	return None

def find_block(block_name, max_distance=64, count=10):
    """
    Find blocks of given type.
    
    Args:
        block_name: Name of block to find (e.g., 'oak_log', 'dirt')
        max_distance: How far to search (default: 64)
        count: Maximum number of blocks to find (default: 10)
    
    Returns:
        List of dicts with block info, sorted by distance (closest first):
        [
            {
                'x': -367,
                'y': 66, 
                'z': -413,
                'distance': 7.6,
                'block': Block object
            },
            ...
        ]
        Returns empty list [] if no blocks found.
    """
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
    movements = pathfinder.Movements(bot)
    bot.pathfinder.setMovements(movements)
    try :
        bot.pathfinder.setGoal(pathfinder.goals.GoalNear(x, y, z, radius))
    except:
        print("fuckkkkkk")
        bot.chat("fuckkkkk")
        return
        
def get_tree(type = 'oak'):
    tree = []
    logs = find_block(f'{type}_log', max_distance=32, count=16)
    if not logs:
        print(f"No {type} trees found nearby")
        logs = find_block(f'{type}_log', max_distance=64, count=16)
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
                t = bot.digTime(log['block'])
                bot.dig(log['block'])
                time.sleep(t/1000 + 1)  # Wait for mining to finish
            except Exception as e:
                print(f"Failed to mine block: {e}")
        print("mining log")
        #time.sleep(10)
        
        
        
@On(bot,'end')
def OnEnd(reason, *args):
    print("kicked for" + reason)
    MakeBot('chatter_again')

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
