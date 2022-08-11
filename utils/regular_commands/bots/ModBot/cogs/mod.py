import discord
from discord.ext import commands

from core.common import Colors, Emoji


class PunishmentTag(commands.Cog):
    """Moderation commands"""

    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = "Moderation"

    @property
    def display_emoji(self) -> str:
        return Emoji.mod_shield

    @commands.command(aliases=["punishment"])
    async def p(self, ctx):
        return

    @commands.command(aliases=["newp"])
    async def pmod(self, ctx):
        return

    @commands.command(aliases=["delp", "dp"])
    async def deletep(self, ctx):
        return

    @commands.command(aliases=["ltag"])
    async def listtag(self, ctx):
        return

    @commands.command(aliases=["find"])
    async def info(self, ctx):
        return


async def setup(bot):
    await bot.add_cog(PunishmentTag(bot))
