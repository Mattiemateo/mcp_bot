from javascript import require, On
from mcp.server.fastmcp import Context, FastMCP
import asyncio

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')

def MakeBot(name: str):
    global bot
    bot = mineflayer.createBot({
    	'host': '152.228.198.208', # minecraft server ip
    	'username': name,
    	'auth': 'offline',
    	'port': '22239',
    })
    bot.loadPlugin(pathfinder.pathfinder)

MakeBot("chopper")

message_list = ["this is a test message"]

mcp = FastMCP(name="Minecraft chat helper")

#movements = pathfinder.Movements(bot)
'''
def find_tree(type = 'oak'):
    ids = [[49], [50], [51], [52], [53], [55]]
    
    for id in ids:
        print("looking for", id)
        blocks = bot.findBlocks(id, 128, 1)
        block = bot.blockAt(bot.findBlocks({'matching': 'oak_log', 'maxDistance': 64}))
        print(f"found {block}")
        bot.chat(f'I found {block} of {id} blocks')
'''        
def find_tree():
    """Find the nearest tree log of any type."""
    
    block = bot.findBlock({
        'matching': lambda block: 'log' in block.name,
        'maxDistance': 64
    })
    
    if block:
        print(f"Found {block.name} at position: x={block.position.x}, y={block.position.y}, z={block.position.z}")
        bot.chat(f"Found tree!")
        return block
    else:
        print("No logs found")
        bot.chat("No trees nearby")
        return None
    


@On(bot, 'spawn')
def handle(*args):
    print("I spawned 👋")
    find_tree()
    movements = pathfinder.Movements(bot)

    @On(bot, 'chat')
    def handleMsg(this, sender, message, *args):
        message_list.append(message)
        if len(message_list) > 5:
            _ = message_list.pop(0)

        print ("got", message, "from", sender)

        if sender != bot.username and sender:
            if "come here" in message:
                player = bot.players[sender]
                target = player.entity
                pos = target.position
                bot.pathfinder.setMovements(movements)
                try :
                    bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, 1))
                except:
                    print("fuckkkkkk")
                    bot.chat("fuckkkkk")

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