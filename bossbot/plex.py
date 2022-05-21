from io import BytesIO

from aiohttp import hdrs
from bossbot.bot import BossBot
from discord import Embed
from discord import File


async def announce_new_library_entry(bot, payload, thumb_fp):
    if payload['Metadata']['type'] == 'episode':
        episode_name = payload['Metadata']['title']
        show_name = payload['Metadata']['grandparentTitle']
        season_num = payload['Metadata']['parentIndex']
        episode_num = payload['Metadata']['index']

        title = f'{show_name} - {episode_name}'
        desc = f'Season {season_num}, episode {episode_num}'

    elif payload['Metadata']['type'] == 'movie':
        year = payload['Metadata']['year']

        title = payload['Metadata']['title']
        desc = f'{title} ({year})'

    else:
        # ignore music, anything not TV/Movies
        return


    thumb_file = File(thumb_fp, 'thumb.jpg')
    embed = Embed(
        title=title,
        description=f'{desc} just uploaded',
    ).set_thumbnail(
        url='attachment://thumb.jpg',
    )

    channel_ids = bot.config['plex']['CHANNELS'].split(',')
    for channel_id in channel_ids:
        channel = await bot.fetch_channel(channel_id)
        await channel.send(embed=embed, file=thumb_file)


@BossBot.on_webhook('/plex')
async def handle_plex_webhook(request):
    thumb_fp = None

    reader = await request.multipart()
    while not reader.at_eof():
        res = await reader.next()
        if res is None:
            break

        if res.headers and res.headers[hdrs.CONTENT_TYPE] == 'application/json':
            payload = await res.json()
        else:
            thumb_fp = BytesIO(await res.read())

    if payload['event'] == 'library.new':
        if thumb_fp:
            await announce_new_library_entry(request.app['bot'], payload, thumb_fp)
    # Only support new library entries for now
