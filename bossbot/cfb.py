from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

import requests
from discord import Colour
from discord import Embed
from pytz import timezone

from bossbot.bot import BossBot

WEEKLY_SCORES = 'https://data.ncaa.com/casablanca/scoreboard/football/fbs/{year}/{week:02}/scoreboard.json'
LIVE_SCORES = 'https://data.ncaa.com/casablanca/live-today.json'
TEAMS = ['GATECH', 'AUBURN', 'CLEM', 'FLA', 'ALA', 'OHIOST']
CONFERENCES = ['ACC', 'SEC', 'Big Ten', 'Big 12', 'Pac-12', 'Top 25']
HELP_TEXT = f'Bad format. Try `@bossbot cfb` or include a conference from: {CONFERENCES}'
TRACKED_TEAMS_DESC = 'Showing tracked teams scores for the latest week with played games'
CONF_TEAMS_DESC = 'Showing scores for teams in the {conference} for the latest week with played games'


@dataclass
class TeamGameInfo:
    char6: str
    short: str
    conferences: list
    rank: str
    record: str
    score: str
    winner: bool

    @classmethod
    def from_json(cls, d):
        conferences = [c['conferenceName'] for c in d['conferences']]
        return cls(
            char6=d['names']['char6'],
            short=d['names']['short'],
            conferences=conferences,
            rank=d['rank'],
            record=d['description'],
            score=d['score'],
            winner=d['winner'],
        )


@dataclass
class GameInfo:
    away: TeamGameInfo
    home: TeamGameInfo
    winner: TeamGameInfo
    state: str
    start_time: str
    start_date: datetime

    @classmethod
    def from_json(cls, d):
        away = TeamGameInfo.from_json(d['away'])
        home = TeamGameInfo.from_json(d['home'])
        game_state=d['gameState']
        start_date = datetime.fromtimestamp(
            int(d['startTimeEpoch'])
        ).astimezone(timezone('US/Eastern'))

        if game_state == 'FINAL':
            if home.winner:
                winner = home
            elif away.winner:
                winner = away
        else:
            winner = None

        return cls(
            away=away,
            home=home,
            winner=winner,
            state=game_state,
            start_time=d['startTime'],
            start_date=start_date,
        )


def week_has_played_games(games):
    now = datetime.now().astimezone(timezone('US/Eastern'))
    first_game_of_week = min(
        game.start_date
        for game in games
    )
    if first_game_of_week > now:
        return False
    return True


def all_games_played(games):
    now = datetime.now().astimezone(timezone('US/Eastern'))
    last_game_of_week = max(
        game.start_date
        for game in games
    )
    if last_game_of_week < now:
        return True
    return False


def filter_by_teams(games, teams):
    filtered_games = []
    for game in games:
        if game.away.char6 in teams or game.home.char6 in teams:
            filtered_games.append(game)
    return filtered_games


def filter_by_conference(games, conference):
    filtered_games = []
    for game in games:
        if conference in game.away.conferences or conference in game.home.conferences:
            filtered_games.append(game)
    return filtered_games


def fetch_latest_played_games():
    year = datetime.now().year
    last_week = None
    for week in range(1, 16):
        weekly_data = requests.get(
            WEEKLY_SCORES.format(year=year, week=week)
        ).json()['games']
        # Throw games into class for more structured data
        weekly_data = [
            GameInfo.from_json(g['game'])
            for g in weekly_data
        ]
        if not week_has_played_games(weekly_data):
            week -= 1
            break
        last_week = weekly_data

    return last_week


def add_gameday_field(embed, day):
    game_bullets = []
    for game in day:
        game_info = game.state.upper()
        if game_info in ('PRE', 'POSTPONED'):
            if game_info == 'PRE':
                game_info = game.start_time
            score = 'vs.'
        else:
            score = f'({game.away.score} - {game.home.score})'
        game_bullets.append(
            f'• {game.away.rank} **{game.away.short}** {score} {game.home.rank} **{game.home.short}**⠀--⠀{game_info}'
        )
    games = '\n'.join(game_bullets)

    fmt_date = day[0].start_date.strftime('%A, %B %d, %Y')
    embed.add_field(
        name=f'**{fmt_date}**',
        value=games,
        inline=False,
    )


@BossBot.on_command('cfb')
async def cfb(bot, message):
    split_msg = message.content.split(maxsplit=2)
    conference = None
    if len(split_msg) == 3:
        conference = split_msg[2]
        if conference not in CONFERENCES:
            await message.channel.send(HELP_TEXT)
            return
        else:
            desc = CONF_TEAMS_DESC.format(conference=conference)
    else:
        desc = TRACKED_TEAMS_DESC

    games = fetch_latest_played_games()
    if conference is None:
        games = filter_by_teams(games, TEAMS)
    else:
        games = filter_by_conference(games, conference)

    games_by_day = defaultdict(list)
    for game in games:
        games_by_day[game.start_date.day].append(game)

    embed = Embed(
        title=f'College Football Scores',
        description=desc,
        url='https://www.ncaa.com/scoreboard/football/fbs',
        colour=Colour.from_rgb(0x0A, 0x6F, 0xAC),
    )
    for day in games_by_day.values():
        add_gameday_field(embed, day)

    await message.channel.send('', embed=embed)
