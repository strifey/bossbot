from dataclasses import dataclass

import requests
from discord import Colour
from discord import Embed

from bossbot.bot import BossBot
from bossbot.db import GoodReadsDB


@dataclass
class Track:
    name: str
    album: str
    artist: str
    url: str
    image: str
    now_playing: bool

    @classmethod
    def from_json(cls, d):
        track = d['recenttracks']['track'][0]
        return cls(
            name=track['name'],
            album=track['album']['#text'],
            artist=track['artist']['#text'],
            url=track['url'],
            image=[i['#text'] for i in track['image'] if i['size'] == 'extralarge'][0],
            now_playing=bool(track['@attr']['nowplaying']) if track.get('@attr', {}).get('nowplaying') else False,
        )


def fetch_latest_track(api_key, username):
    resp = requests.get(
        'http://ws.audioscrobbler.com/2.0/',
        params={
            'format': 'json',
            'method': 'user.getRecentTracks',
            'limit': 1,
            'api_key': api_key,
            'user': username,
        }
    )
    return Track.from_json(resp.json())


@BossBot.on_command('listening')
async def listening(bot, message):
    api_token = bot.config['lastfm']['API_KEY']

    db = GoodReadsDB()
    username = db.fetch_lastfm_user(message.author.id)
    if username is None:
        await message.channel.send(f'<@!{message.author.id}> has not registered a last.fm username!')
        await message.channel.send('Run `@bossbot lastfm <username>` or dm bossbot the same command first to use this command')
        return

    track = fetch_latest_track(api_token, username)
    if not track.now_playing:
        await message.channel.send(f'<@!{message.author.id}> is not currently listening to anything!')
        return

    embed =  Embed(
        title=f'Now playing - {track.name}', # TODO: mention author
        description=f'<@!{message.author.id}> is currently listening to...',
        colour=Colour.from_rgb(185, 0, 0),
        url=track.url,
    ).add_field(
        name=track.name,
        value=f'by **{track.artist}** from **{track.album}**',
        inline=True,
    ).set_thumbnail(
        url=track.image,
    ).set_footer(
        text='via last.fm',
        icon_url='http://images1.wikia.nocookie.net/__cb20130411230810/logopedia/images/1/1d/Last_fm_logo.png',
    )
    await message.channel.send(' ', embed=embed)


@BossBot.on_dm('lastfm')
async def register_username_dm(bot, message):
    split_msg = message.content.split()
    if len(split_msg) != 2:
        await message.channel.send('Please dm `lastfm USERNAME` to register a username with bossbot')
        return
    db = GoodReadsDB()
    db.store_lastfm_username(message.author.id, split_msg[1])
    await message.channel.send('last.fm username set!')


@BossBot.on_command('lastfm')
async def register_username_cmd(bot, message):
    split_msg = message.content.split()
    if len(split_msg) != 3:
        await message.channel.send('Please try `@bossbot lastfm USERNAME` to register a username with bossbot')
        return
    db = GoodReadsDB()
    db.store_lastfm_username(message.author.id, split_msg[2])
    await message.channel.send('last.fm username set!')
