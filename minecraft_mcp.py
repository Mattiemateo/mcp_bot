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
