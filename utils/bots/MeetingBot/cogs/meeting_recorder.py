import discord
from discord.ext import commands
from core.checks import is_botAdmin
from google.cloud import speech_v1p1beta1 as speech

doc_id = "1u_Ab5ZkKxHLlkOWAAXW8Ht_vgv9T-3PBA_Lj-KWc-G0"
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]


async def finished_callback(sink, channel: discord.TextChannel, *args):
    client = speech.SpeechClient()
    recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
    await sink.vc.disconnect()

    files = [
        discord.File(audio.file, f"{user_id}.{sink.encoding}")
        for user_id, audio in sink.audio_data.items()
    ]
    await channel.send(
        f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files
    )


class MTGBOT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.connections = {}

    @commands.command()
    async def record(self, ctx):
        voice = ctx.author.voice

        if ctx.guild.id in self.bot.connections:
            vc = self.bot.connections[ctx.guild.id]
            vc.stop_recording()
            del self.bot.connections[ctx.guild.id]
            await ctx.delete()
        else:
            if not voice:
                return await ctx.respond("You're not in a vc right now")

            vc = await voice.channel.connect()
            self.bot.connections.update({ctx.guild.id: vc})
            sink = discord.sinks.MP4Sink()
            vc.start_recording(
                sink,
                finished_callback,
                ctx.channel,
            )

            await ctx.respond("The recording has started!")


def setup(bot):
    bot.add_cog(MTGBOT(bot))
