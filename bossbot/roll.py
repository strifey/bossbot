import random

from discord import Embed

from bossbot.bot import BossBot


@BossBot.on_command('roll')
async def roll(bot, message):
    split_message = message.content.split(maxsplit=2)
    if len(split_message) < 3:
        await message.channel.send('🐕')
        return

    totals = []
    results_embed = Embed(title='Results')
    rolls = split_message[2].split(',')
    for roll in rolls:
        roll_components = roll.strip().split('d')
        if len(roll_components) != 2:
            await message.channel.send('Improper format. Format rolls like `@bossbot roll 1d20`')
            return
        try:
            die_count = int(roll_components[0])
            die_size = int(roll_components[1])
        except ValueError:
            await message.channel.send('Improper format. Format rolls like `@bossbot roll 1d20`')
            return
        if die_count <= 0 or die_size <= 0:
            results_embed.add_field(name=roll, value='No rolls.', inline=False)
            continue
        die_count = min(100, die_count)

        results = []
        for _ in range(die_count):
            results.append(random.randint(1, die_size))
        total = sum(results)
        totals.append(total)

        if die_count > 1:
            results_str = '{0} = {1}'.format(
                ' + '.join(list(map(str, results))), total)
        else:
            results_str = str(results[0])
        results_embed.add_field(name=roll, value=results_str, inline=False)

    if len(totals) > 1:
        results_embed.add_field(name='Total', value='{0} = {1}'.format(
            ' + '.join(list(map(str, totals))), sum(totals)))
    await message.channel.send(embed=results_embed)
