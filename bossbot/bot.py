import random
import re
from functools import wraps

from discord import Client
from discord import DMChannel
from discord import Embed
import requests

from bossbot.goodreads import gr_reading
from bossbot.goodreads import start_gr_oauth
from bossbot.goodreads import finish_gr_oauth


class BossBot(Client):
    bot_commands = []
    dm_commands = []

    def __init__(self, config, *args, **kwargs):
        self.config = config
        super().__init__(*args, **kwargs)

    def _is_ping(self, message: str, only_start: bool = True) -> bool:
        ping = f'<@!{self.user.id}>'
        if only_start:
            first_word = message.split()[0]
            return first_word == ping
        else:
            return ping in message

    def _is_dm(self, message):
        return isinstance(message.channel, DMChannel)

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            # Here be dragons
            return
        elif not message.content:
            # No command, we sleep
            return

        try:
            if self._is_dm(message):
                dm_words = message.content.split()
                command = dm_words[0]
                for registered_dm_cmds, func in self.dm_commands:
                    if registered_dm_cmds == command:
                        await func(self, message)


            elif self._is_ping(message.content):
                if (message.author.id == 97558918720389120 and random.randint(1, 20) == 20):
                    await message.channel.send("go fuck yourself")
                    return

                msg_words = message.content.split()
                if len(msg_words) > 1:
                    command = msg_words[1]

                for cmd_match, func in self.bot_commands:
                    if command == cmd_match:
                        await func(self, message)

        except Exception as e:
            await message.add_reaction('💢')
            raise


def on_command(command_pattern):
    def decorator_on_command(func):
        BossBot.bot_commands.append((command_pattern, func))

        @wraps(func)
        def on_command_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return on_command_wrapper

    return decorator_on_command


def on_dm(dm_pattern):
    def decorator_on_dm(func):
        BossBot.dm_commands.append((dm_pattern, func))

        @wraps(func)
        def on_dm_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return on_dm_wrapper

    return decorator_on_dm


@on_command('ping')
async def pingpong(bot, message):
    await message.channel.send('pong')


@on_command('pizza')
async def pizza(bot, message):
    await message.channel.send('https://i.imgur.com/Ayg3naa.gif')

@on_command('bababooey')
async def bababooey(bot, message):
    await message.channel.send('https://www.youtube.com/watch?v=U_cPir6MwLM')


@on_command('help')
async def help(bot, message):
    embed = Embed(title='Commands', description='Currently registered commands')
    direct_cmds = '\n'.join(f'• `@bossbot {cmd}`' for cmd, _ in bot.bot_commands)
    if direct_cmds:
        embed.add_field(name='Direct commands', value=direct_cmds, inline=True)

    dm_cmds = '\n'.join(f'• `{cmd}`' for cmd, _ in bot.dm_commands)
    if dm_cmds:
        dm_cmds = '_(these only work in DMs to the bot)_\n' + dm_cmds
        embed.add_field(name='DM commands', value=dm_cmds, inline=True)
    await message.channel.send(
        '`bossbot` is your friendly, neighborhood, bossy chatbot. Check out my code at https://github.com/strifey/bossbot',
        embed=embed,
    )


@on_command('choose')
async def choose(bot, message):
    split_msg = message.content.split(maxsplit=2)
    if len(split_msg) == 3:
        choosen = split_msg[2].split(',')
        await message.channel.send(random.choice(choosen))
    else:
        await message.channel.send('Give me something to choose from!')


@on_command('8ball')
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


@on_dm('gr-oauth')
async def start_register_goodreads_user(bot, message):
    await start_gr_oauth(bot, message)

@on_dm('finish-gr-oauth')
async def finish_register_goodreads_user(bot, message):
    await finish_gr_oauth(bot, message)

@on_command('reading')
async def goodreads(bot, message):
    await gr_reading(bot, message)


@on_command('roll')
async def roll(bot, message):
    split_message = message.content.split(maxsplit=2)
    if len(split_message) < 3:
        await message.channel.send('🐕')
        return

    totals = []
    results_embed = Embed(title='Results')
    rolls = split_message[2].split(',')
    for roll in rolls:
        roll_components = roll.strip().split('d')
        if len(roll_components) != 2:
            await message.channel.send('Improper format. Format rolls like `@bossbot roll 1d20`')
            return
        try:
            die_count = int(roll_components[0])
            die_size = int(roll_components[1])
        except ValueError:
            await message.channel.send('Improper format. Format rolls like `@bossbot roll 1d20`')
            return
        if die_count <= 0 or die_size <= 0:
            results_embed.add_field(name=roll, value='No rolls.', inline=False)
            continue
        die_count = min(100, die_count)

        results = []
        for _ in range(die_count):
            results.append(random.randint(1, die_size))
        total = sum(results)
        totals.append(total)

        if die_count > 1:
            results_str = '{0} = {1}'.format(
                ' + '.join(list(map(str, results))), total)
        else:
            results_str = str(results[0])
        results_embed.add_field(name=roll, value=results_str, inline=False)

    if len(totals) > 1:
        results_embed.add_field(name='Total', value='{0} = {1}'.format(
            ' + '.join(list(map(str, totals))), sum(totals)))
    await message.channel.send(embed=results_embed)


@on_command('inspire')
async def inspire(bot, message):
    inspired_url = requests.get('https://inspirobot.me/api?generate=true').text
    await message.channel.send(inspired_url)
