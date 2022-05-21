"""
TODO:
* Track increments and decrements separately
* Print the total karma and breakdown
* Handle emoji reactions to messages :++: and :--:
"""

from bossbot.bot import BossBot
from bossbot.db import KarmaDB

async def get_target_user(message):
    if len(message.mentions) < 2:
        await message.channel.send('No valid user mentioned in the command! Format is `@bossbot [karma|++|--] @user`')
        raise ValueError('No user mentioned in karma command.')
    return message.mentions[1]

async def notify_karma(user_id, plus_karma, minus_karma, message):
    karma = plus_karma - minus_karma
    await message.channel.send(
            '<@{user}> has {karma} karma ({plus_karma} - {minus_karma})'.format(
                user=user_id,
                karma=karma,
                plus_karma=plus_karma,
                minus_karma=minus_karma))

@BossBot.on_command('karma')
async def check_karma(bot, message):
    user = await get_target_user(message)
    db = KarmaDB(testing=bot.testing)
    plus_karma, minus_karma = db.get_user_karma(user.id)
    await notify_karma(user.id, plus_karma, minus_karma, message)

@BossBot.on_command('++')
async def increment_karma(bot, message):
    user = await get_target_user(message)
    db = KarmaDB(testing=bot.testing)
    db.increment_user_karma(user.id)
    # post update notification
    plus_karma, minus_karma = db.get_user_karma(user.id)
    karma = plus_karma - minus_karma
    await notify_karma(user.id, plus_karma, minus_karma, message)

@BossBot.on_command('--')
async def decrement_karma(bot, message):
    user = await get_target_user(message)
    db = KarmaDB(testing=bot.testing)
    db.decrement_user_karma(user.id)
    # post update notification
    plus_karma, minus_karma = db.get_user_karma(user.id)
    karma = plus_karma - minus_karma
    await notify_karma(user.id, plus_karma, minus_karma, message)
