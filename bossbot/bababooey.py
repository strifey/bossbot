from time import sleep

from discord import FFmpegPCMAudio

from bossbot.bot import BossBot


@BossBot.on_command('bababooey')
async def bababooey(bot, message):
    author_voice_status = message.author.voice
    if author_voice_status is not None and author_voice_status.channel is not None:
        bababooey_audio_stream = FFmpegPCMAudio(
            'bossbot/resources/bababooey.mp3'
            )
        voice_client = await author_voice_status.channel.connect()
        voice_client.play(bababooey_audio_stream)
        while voice_client.is_playing():
            sleep(1)
        bababooey_audio_stream.cleanup()
        await voice_client.disconnect()
    else:
        await message.channel.send('https://www.youtube.com/watch?v=U_cPir6MwLM')
