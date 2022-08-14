from discord.ext import commands

from core.common import Emoji


class WebCommissionCode(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.__cog_name__ = "Web Commissions"

    @property
    def display_emoji(self) -> str:
        return Emoji.pythonLogo

    @commands.command(name="webcommission", aliases=["wc"])
    async def webcommission(self, ctx):
        return

    @commands.command()
    async def webcommission_list(self, ctx):
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(WebCommissionCode(bot))
