import random
import re
from functools import wraps

from discord import Client
from discord import DMChannel
from discord import Embed


class BossBot(Client):
    bot_commands = []
    dm_commands = []

    def __init__(self, config, *args, **kwargs):
        self.config = config
        super().__init__(*args, **kwargs)

    def _is_ping(self, message: str, only_start: bool = True) -> bool:
        mention = f'<@{self.user.id}>'
        if only_start:
            # Removes !, which usually indicates a mention, but it's weirdly not always there
            first_word = message.split()[0].replace('!', '')
            return first_word == mention or first_word == '@bossbot'
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
                if (message.author.id == 97558918720389120 and random.randint(1, 35) == 35):
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

    @classmethod
    def on_command(cls, command_pattern):
        def decorator_on_command(func):
            BossBot.bot_commands.append((command_pattern, func))

            @wraps(func)
            def on_command_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return on_command_wrapper

        return decorator_on_command

    @classmethod
    def on_dm(cls, dm_pattern):
        def decorator_on_dm(func):
            BossBot.dm_commands.append((dm_pattern, func))

            @wraps(func)
            def on_dm_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return on_dm_wrapper

        return decorator_on_dm


@BossBot.on_command('help')
async def help(bot, message):
    embed = Embed(title='Commands', description='Currently registered commands')
    sorted_cmds = sorted(cmd for cmd, _ in bot.bot_commands)
    direct_cmds = '\n'.join(f'• `@bossbot {cmd}`' for cmd in sorted_cmds)
    if direct_cmds:
        embed.add_field(name='Direct commands', value=direct_cmds, inline=True)

    dm_cmds = '\n'.join(f'• `{cmd}`' for cmd, _ in bot.dm_commands)
    if dm_cmds:
        dm_cmds = '_(these only work in DMs to the bot)_\n' + dm_cmds
        embed.add_field(name='DM commands', value=dm_cmds, inline=True)
    await message.channel.send(
        ('`bossbot` is your ~~sassy~~ friendly, neighborhood chatbot.\n'
        'Check out my code at https://github.com/strifey/bossbot'),
        embed=embed,
    )
