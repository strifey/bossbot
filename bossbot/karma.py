"""
TODO:
* Track increments and decrements separately
* Print the total karma and breakdown
* Handle emoji reactions to messages :++: and :--:
"""

from bossbot.bot import BossBot
from bossbot.db import KarmaDB

def get_target_user(message):
    if len(message.mentions) < 2:
        raise ValueError('No user mentioned in karma command.')
    return message.mentions[1]

@BossBot.on_command('karma')
async def check_karma(bot, message):
    user = get_target_user(message)
    db = KarmaDB()
    karma = db.get_user_karma(user.id)
    await message.channel.send('<@{user}> has {karma} karma'.format(user=user.id, karma=karma))

@BossBot.on_command('++')
async def increase_karma(bot, message):
    user = get_target_user(message)
    db = KarmaDB()
    db.increment_user_karma(user.id)
    # post update notification
    karma = db.get_user_karma(user.id)
    await message.channel.send('<@{user}> has {karma} karma'.format(user=user.id, karma=karma))
