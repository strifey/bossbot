import random
import re
from functools import wraps

from discord import Client
from discord import DMChannel

from bossbot.goodreads import handle_gr_cmd
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
    await handle_gr_reading(bot, message)
