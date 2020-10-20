import random
import urllib

import requests

from bossbot.bot import BossBot


CALL_RESPONSE = {
    'ping': 'pong',
    'pizza': 'https://i.imgur.com/Ayg3naa.gif',
    'bababooey': 'https://www.youtube.com/watch?v=U_cPir6MwLM',
}


async def call_response(bot, message):
    # static respones to basic, single-word commands
    call = message.content.split()[1]
    await message.channel.send(CALL_RESPONSE[call])


for call in CALL_RESPONSE:
    BossBot.on_command(call)(call_response)


@BossBot.on_command('inspire')
async def inspire(bot, message):
    inspired_url = requests.get('https://inspirobot.me/api?generate=true').text
    await message.channel.send(inspired_url)


@BossBot.on_command('choose')
async def choose(bot, message):
    split_msg = message.content.split(maxsplit=2)
    if len(split_msg) == 3:
        choosen = split_msg[2].split(',')
        await message.channel.send(random.choice(choosen))
    else:
        await message.channel.send('Give me something to choose from!')


@BossBot.on_command('trump')
async def trump(bot, message):
    split_msg = message.content.split(maxsplit=2)
    if len(split_msg) != 3:
        await message.channel.send('Bad format. Use `@bossbot trump something`.')
        return
    response = requests.get(
        'https://api.whatdoestrumpthink.com/api/v1/quotes/personalized?q={}'.format(
            urllib.parse.quote(split_msg[2]),
        )
    )
    response.raise_for_status()
    quote = response.json()['message']
    await message.channel.send(quote)


@BossBot.on_command('8ball')
async def shake_8ball(bot, message):
    await message.channel.send(random.choice([
        'It is decidedly so.',
        'You may rely on it.',
        'Outlook good.',
        'Signs point to yes.',
        'As I see it, yes.',
        'Reply hazy, try again.',
        'Ask again later.',
        'Better not tell you now.',
        'Cannot predict now.',
        'Concentrate and ask again.',
        'Don\'t count on it.',
        'My reply is no.',
        'My sources say no.',
        'Outlook not so good.',
        'Very doubtful.',
    ]))
