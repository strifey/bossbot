import random
import re
from functools import wraps

from discord import Client


class BossBot(Client):
    bot_commands = []
    msg_patterns = []

    def _is_ping(self, message: str, only_start: bool = True) -> bool:
        ping = f'<@!{self.user.id}>'

        if only_start:
            first_word = message.split()[0]
            return first_word == ping
        else:
            return ping in message

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            # Here be dragons
            return

        if self._is_ping(message.content):
            msg_words = message.content.split()
            if len(msg_words) > 1:
                command = msg_words[1]

            for cmd_match, func in self.bot_commands:
                if command == cmd_match:
                    await func(self, message)


def on_command(command_pattern):
    def decorator_on_command(func):
        BossBot.bot_commands.append((command_pattern, func))

        @wraps(func)
        def on_command_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return on_command_wrapper

    return decorator_on_command


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
