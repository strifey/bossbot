from argparse import ArgumentParser

from bossbot.bot import setup_bot
from bossbot.config import read_config

def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file path', default='bossbot.ini')
    args = parser.parse_args()

    config = read_config(args.config)

    bot = setup_bot()
    bot.run(config['auth']['API_TOKEN'])

if __name__ == '__main__':
    main()
