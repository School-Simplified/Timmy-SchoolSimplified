from discord.ext import commands

from core.common import Emoji


class MGMTickets(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.__cog_name__ = "MGM Commissions"

    @property
    def display_emoji(self) -> str:
        return Emoji.pythonLogo

    @commands.command()
    async def send_mgm_embed(self, ctx):
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(MGMTickets(bot))
