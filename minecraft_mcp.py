from javascript import require, On
from mcp.server.fastmcp import Context, FastMCP
import asyncio

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')

bot = mineflayer.createBot({
	'host': '152.228.198.208', # minecraft server ip
	'username': 'chatter',
	'auth': 'offline',
	'port': '22239',
})

message_list = []

mcp = FastMCP(name="Minecraft chat helper")

@On(bot, 'spawn')
def handle(*args):
	print("I spawned 👋")

@On(bot, 'chat')
def handleMsg(this, sender, message, *args):
    message_list.append(message)

    print ("got", message, "from", sender)

@mcp.tool()
async def send_message(message: str, ctx: Context) -> str:
    bot.chat(message)
    await ctx.info(f"adding  and ")
    out = f"message {message} has been sent"
    return out

@mcp.tool()
async def read_messages(ctx = Context) -> str:
    await ctx.info(f"reading messages")
    return message_list


if __name__ == "__main__":
    mcp.run(transport="sse")