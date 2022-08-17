import asyncio

import discord
from discord.ext import commands

from core.logging_module import get_log

_log = get_log(__name__)


class EthanMoo(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener("on_voice_state_update")
    async def ethan_moo(self, member, before, after):
        # If a user with the ID 544724467709116457 joins a voice channel, play ethan_moo.mp3
        if before.channel is None and after.channel is not None:
            if member.id == 998386623593058394:
                voice_channel: discord.VoiceChannel = after.channel
                voice_client = await voice_channel.connect()
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio("./ethan_moo.mp3")
                )
                voice_client.play(
                    source,
                    after=lambda e: _log.error(f"Player error: {e}") if e else None,
                )
                await asyncio.sleep(80)
                await voice_client.disconnect()


async def setup(bot):
    await bot.add_cog(EthanMoo(bot))
