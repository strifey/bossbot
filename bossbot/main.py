from argparse import ArgumentParser

from bossbot.bot import BossBot
from bossbot.config import read_config


def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file path', default='bossbot.ini')
    args = parser.parse_args()

    config = read_config(args.config)

    bot = BossBot(config)
    bot.run(config['discord']['API_TOKEN'])


if __name__ == '__main__':
    main()
