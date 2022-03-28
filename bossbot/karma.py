from bossbot.bot import BossBot
from bossbot.db import KarmaDB


@BossBot.on_command('karma')
async def check_karma(bot, message):
    db = KarmaDB()
    user = message.mentions[1]
    karma = db.get_user_karma(user.id)
    print('fetch:  {}: {}'.format(user.id, karma))
    await message.channel.send('<@{user}> has {karma} karma'.format(user=user.id, karma=karma))


@BossBot.on_command('++')
async def increase_karma(bot, message):
    # print('mentioned user {}'.format(message.mentions[1]))
    user = message.mentions[1]
    db = KarmaDB()
    karma = db.get_user_karma(user.id)
    db.set_user_karma(user.id, karma + 1)
    karma = db.get_user_karma(user.id)
    print('update: {}: {}'.format(user.id, karma))
    await message.channel.send('<@{user}> has {karma} karma'.format(user=user.id, karma=karma))
