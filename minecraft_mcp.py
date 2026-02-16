from javascript import require, On
from mcp.server.fastmcp import Context, FastMCP
import asyncio

def MakeBot(name: str):
    global bot
    bot = mineflayer.createBot({
    	'host': '152.228.198.208', # minecraft server ip
    	'username': name,
    	'auth': 'offline',
    	'port': '22239',
    })

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')

mcData = None

MakeBot("chatter")

message_list = ["this is a test message"]

mcp = FastMCP(name="Minecraft chat helper")



@On(bot, 'spawn')
def handle(*args):
	print("I spawned 👋")

'''@On(bot, 'message')
def handleGlobalMessage(jsonMsg, position, sender, verified, *args):
    print(jsonMsg)
    message_list.append(jsonMsg)
    print(jsonMsg)
'''
def find_block(block_name):
    global mcData
    # Load minecraft data for block IDs
    mcData = require('minecraft-data')(bot.version)
    
    """Find nearest block of given type using block ID"""
    print(f"Searching for {block_name}...")
    
    # Get the block type from minecraft-data
    blockType = mcData.blocksByName[block_name]
    
    if not blockType:
        print(f"Unknown block: {block_name}")
        bot.chat(f"Don't know block {block_name}")
        return None
    
    bot_pos = bot.entity.position
    
    # Use numeric ID for matching
    positions = bot.findBlocks({
        'matching': blockType.id,
        'maxDistance': 64,
        'count': 5
    })
    
    if positions and positions.length > 0:
        print(f"Found {positions.length} {block_name} blocks:")
        
        for i in range(min(5, positions.length)):
            pos = positions[i]
            distance = bot_pos.distanceTo(pos)
            print(f"  [{i}] x={pos.x}, y={pos.y}, z={pos.z} (distance: {distance:.1f})")
        
        pos = positions[0]
        bot.chat(f"Found {block_name} at {pos.x}, {pos.y}, {pos.z}!")
        return bot.blockAt(pos)
    else:
        print(f"No {block_name} found")
        bot.chat(f"No {block_name} found!")
        return None

@On(bot, 'chat')
def handleMsg(this, sender, message, *args):
    message_list.append(message)
    if len(message_list) > 5:
        _ = message_list.pop(0)
    
    print ("got", message, "from", sender)

@On(bot, 'end')
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
