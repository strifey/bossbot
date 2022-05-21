import random
import re
import traceback
from functools import partial
from functools import wraps

import discord.utils
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Client
from discord import DMChannel
from discord import Embed


REACT_PATTERNS = {
    'hwat': 'hwat',
    'hark': 'hark',
    'yikes': 'yikes',
    'french': 'frencharjun',
    'shrug': 'shrug',
    '69': 'nice',
    '420': '420',
}


class BossBot(Client):
    bot_commands = []
    dm_commands = []
    interval_funcs = []
    webhooks = []

    def __init__(self, config, testing, *args, **kwargs):
        self.config = config
        self.testing = testing

        self._setup_jobs()

        super().__init__(*args, **kwargs)

    async def start(self, *args, **kwargs):
        await self.start_webapp()
        await super().start(*args, **kwargs)

    def _setup_jobs(self):
        self.job_scheduler = AsyncIOScheduler()
        for int_args, int_kwargs, func in self.interval_funcs:
            if 'trigger' in int_kwargs:
                trigger = int_kwargs['trigger']
            else:
                # Just assume since this is likely the most common usecase
                trigger = 'interval'

            self.job_scheduler.add_job(func, trigger=trigger, args=(self,), **int_kwargs)
        self.job_scheduler.start()

    async def start_webapp(self):
        self._base_webapp = web.Application()
        self.app = web.Application()
        self.app['bot'] = self

        for method, route, handler in self.webhooks:
            self.app.router.add_route(method, route, handler)

        # We have two applications, one as a subapp, to get /bossbot/ prepended to all routes
        self._base_webapp.add_subapp('/bossbot/', self.app) 

        runner = web.AppRunner(self._base_webapp, handle_signals=True)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.config['webhooks']['PORT'])
        await site.start()
        

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

    async def _autoreact(self, message):
        for word, reaction in REACT_PATTERNS.items():
            if re.search(f'(\W|^){word}(\W|$)', message.content, flags=re.IGNORECASE) is not None:
                emoji = discord.utils.get(self.emojis, name=reaction)
                if emoji is not None:
                    await message.add_reaction(emoji)

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
            await self._autoreact(message)

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

    @classmethod
    def on_interval(cls, *a, **kw):
        def decorator_on_interval(func):
            BossBot.interval_funcs.append((a, kw, func))

            @wraps(func)
            def on_interval_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return on_interval_wrapper

        return decorator_on_interval

    @classmethod
    def on_webhook(cls, route, method='POST'):
        def decorator_on_webhook(func):
            BossBot.webhooks.append((method, route, func))

            @wraps(func)
            def on_webhook_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return on_webhook_wrapper

        return decorator_on_webhook
        

    async def on_error(self, event, *args, **kwargs):
        if self.testing and event == 'on_message':
            tb = traceback.format_exc()
            msg = args[0]
            await msg.channel.send(f'```{tb}```')
        await super().on_error(event, *args, **kwargs)


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
