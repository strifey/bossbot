import re
from datetime import datetime
from time import mktime

import feedparser
from discord import Colour
from discord import Embed

from bossbot.bot import BossBot
from bossbot.db import LetterboxdDB
from bossbot.db import AlreadySubbedError


RSS_URL = 'https://letterboxd.com/{user}/rss/'
POSTER_URL_REGEX = r'img src="(?P<url>.+)"'


def format_lbd_entry(entry):
    poster_url = re.search(POSTER_URL_REGEX, entry.summary).group('url')
    return Embed(
        title=entry.title,
        description=f'{entry.author} just logged this movie',
        url=entry.link,
    ).set_thumbnail(
        url=poster_url,
    ).set_footer(
        text='via Letterboxd',
        icon_url='https://a.ltrbxd.com/logos/letterboxd-decal-dots-pos-rgb-500px.png',
    )


@BossBot.on_interval(minutes=1)
async def post_letterboxd_updates(bot):
    run_time = datetime.now()

    db = LetterboxdDB(testing=bot.testing)
    subs = db.get_all_subs()
    for user, channel_id, last_announced in subs:
        user_rss = feedparser.parse(RSS_URL.format(user=user))
        if user_rss.bozo:
            # Bad response
            continue

        for post in user_rss.entries:
            post_publish_time = datetime.fromtimestamp(mktime(post.published_parsed))
            if post_publish_time < last_announced:
                # We've already messaged about the rest
                break

            channel = bot.get_channel(channel_id)
            await channel.send(embed=format_lbd_entry(post))

            db.set_last_announced(user, channel_id, run_time)


@BossBot.on_command('lbd-sub')
async def letterboxd_sub(bot, message):
    split_msg = message.content.split()
    if len(split_msg) != 3:
        await message.channel.send(
            'Try `@bossbot lbd-sub USERNAME` to subscribe to a letterboxd announce with bossbot'
        )
        return

    db = LetterboxdDB(testing=bot.testing)
    lbd_username = split_msg[2]

    try:
        db.sub_letterboxd_user(lbd_username, message.channel.id)
    except AlreadySubbedError:
        await message.channel.send('This letterboxd user is already subscribed in this channel')
    else:
        await message.channel.send(f'This channel will now receive updates from `{lbd_username}` when they log movies on letterboxd')


@BossBot.on_command('lbd-unsub')
async def letterboxd_sub(bot, message):
    split_msg = message.content.split()
    if len(split_msg) != 3:
        await message.channel.send(
            'Try `@bossbot lbd-unsub USERNAME` to unsub to a letterboxd announce with bossbot'
        )
        return

    db = LetterboxdDB(testing=bot.testing)
    lbd_username = split_msg[2]

    db.unsub_letterboxd_user(lbd_username, message.channel.id)

    await message.channel.send(f'This channel will no longer receive updates from `{lbd_username}` when they log movies on letterboxd')
