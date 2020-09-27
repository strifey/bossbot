import random

from discord import Client


class BossBot(Client):

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
            if message.content.split()[1] == 'ping':
                await message.channel.send('pong')

            elif message.content.split()[1] == '8ball':
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

            elif message.content.split()[1] == 'choose':
                split_msg = message.content.split(maxsplit=2)
                if len(split_msg) == 3:
                    choosen = split_msg[2].split(',')
                    await message.channel.send(random.choice(choosen))
                else:
                    await message.channel.send('Give me something to choose from!')


def setup_bot():
    bot = BossBot(
        command_prefix='bossbot',
    )

    return bot
