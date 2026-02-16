from javascript import require, On
mineflayer = require('mineflayer')

bot = mineflayer.createBot({
    'host': '152.228.198.208',
    'username': 'Bot',
    'auth': 'offline',
    'port': '22239',
})

print("Started mineflayer")

mcData = None

@On(bot, 'spawn')
def handle(*args):
    global mcData
    print("I spawned 👋")
    
    # Load minecraft data for block IDs
    mcData = require('minecraft-data')(bot.version)
    
    bot.waitForChunksToLoad()
    print("Chunks loaded!")
    
    @On(bot, 'chat')
    def handleMsg(this, sender, message, *args):
        if sender and (sender != bot.username):
            if 'find tree' in message:
                find_block('oak_log')
            elif 'find dirt' in message:
                find_block('dirt')
            elif 'find stone' in message:
                find_block('stone')

def find_block(block_name):
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

@On(bot, "end")
def handle(*args):
    print("Bot ended!", args)