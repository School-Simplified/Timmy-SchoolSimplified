import discord
from discord.ext import commands

from core.logging_module import get_log

_log = get_log(__name__)


class TutorVCCMD(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def startmusic(self, ctx):
        return

    @commands.command()
    async def startgame(self, ctx):
        return

    @commands.command()
    async def startyt(self, ctx):
        return

    @commands.command()
    async def rename(self, ctx):
        return

    @commands.command()
    async def end(self, ctx):
        return

    @commands.command()
    async def forceend(self, ctx):
        return

    @commands.command()
    async def lock(self, ctx):
        return

    @commands.command()
    async def settutor(self, ctx):
        return

    @commands.command()
    async def unlock(self, ctx):
        return

    @commands.command()
    async def permit(self, ctx):
        return

    @commands.command()
    async def voicelimit(self, ctx):
        return

    @commands.command()
    async def disconnect(self, ctx):
        return

    @commands.command(aliases=["start"])
    async def startVC(self, ctx):
        return


async def setup(bot):
    await bot.add_cog(TutorVCCMD(bot))
