from dataclasses import dataclass

import arrow
import humanize
import requests
from discord import Colour
from discord import Embed

from bossbot.bot import BossBot

HELP_TEXT = 'Call stonks with company symbol(s), eg. `stonks AAPL GOOG GME`'


@dataclass
class Quote:
    symbol: str
    company_name: str
    latest_price: float
    open_price: float
    close_price: float
    change_pct: float
    volume: int
    market_cap: int
    updated: int

    @classmethod
    def from_json(cls, d):
        return cls(
            symbol=d['symbol'],
            company_name=d['companyName'],
            latest_price=d['latestPrice'],
            open_price=d['iexOpen'],
            close_price=d['iexClose'],
            change_pct=d['changePercent'],
            volume=d['iexVolume'],
            market_cap=d['marketCap'],
            updated=d['latestUpdate'],
        )


def fetch_symbol_quote(symbol, api_token):
    api_url = f'https://cloud.iexapis.com/stable/stock/{symbol}/quote'
    raw_data =  requests.get(api_url, params={'token': api_token}).json()
    return Quote.from_json(raw_data)


def create_symbol_embed(symbol, quote):
    humanized_updated_time = arrow.get(quote.updated).humanize()
    stonk_embed = Embed(
        title=f'The lastest stonk info for {symbol}',
        description=f'**{quote.company_name}**\nLast updated {humanized_updated_time}',
        colour=Colour.from_rgb(255, 0, 129),
        url='https://iexcloud.io',
    )
    stonk_embed.set_thumbnail(url='https://i.imgur.com/hfYsjqR.jpg')
    stonk_embed.add_field(name='Price', value=f'${quote.latest_price:.02f}', inline=True)
    stonk_embed.add_field(name='Percent Change', value=f'{quote.change_pct:.02%}', inline=True)
    stonk_embed.add_field(name='\u200B', value='\u200B')
    stonk_embed.add_field(name='Market Cap', value=f'${humanize.intword(quote.market_cap)}', inline=True)
    stonk_embed.add_field(name='Volume', value=f'{humanize.intword(quote.volume)}', inline=True)
    stonk_embed.add_field(name='\u200B', value='\u200B')
    stonk_embed.add_field(name='Open', value=f'${quote.open_price:.02f}', inline=True)
    stonk_embed.add_field(name='Prev Close', value=f'${quote.close_price:.02f}', inline=True)
    stonk_embed.set_footer(
        text='Data provided by IEX Cloud',
        icon_url='https://i.imgur.com/kro2hN9.png',
    )
    return stonk_embed


@BossBot.on_command('stonks')
async def stonks(bot, message):
    split_msg = message.content.split(maxsplit=2)
    if len(split_msg) < 3:
        await message.channel.send(HELP_TEXT)
        return

    api_token = bot.config['stonk']['API_KEY']
    symbols = split_msg[2].split()
    for symbol in symbols:
        quote = fetch_symbol_quote(symbol, api_token)
        symbol_embed = create_symbol_embed(symbol, quote)
        await message.channel.send(' ', embed=symbol_embed)
