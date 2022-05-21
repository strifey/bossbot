from argparse import ArgumentParser
import importlib

from bossbot.bot import BossBot
from bossbot.config import read_config


# A module must be listed here to be imported and its registration decorators to be run
REGISTERED_MODULES = [
    'bossbot.bababooey',
    'bossbot.basic',
    'bossbot.cfb',
    # 'bossbot.goodreads', # rip goodreads API
    'bossbot.letterboxd',
    'bossbot.listening',
    'bossbot.roll',
    'bossbot.stonks',
    'bossbot.karma',
]


def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file path', default='bossbot.ini')
    parser.add_argument('-t', '--testing', help='Testing Mode', default=False, action='store_true')
    args = parser.parse_args()
    config = read_config(args.config)
    # Find and register all the bossbot commands
    for module in REGISTERED_MODULES:
        importlib.import_module(module)
    # Actually create and run the bot
    bot = BossBot(config, args.testing)
    bot.run(config['discord']['API_TOKEN'])


if __name__ == '__main__':
    main()
