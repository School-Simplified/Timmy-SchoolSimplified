from discord.ext import commands, tasks
from core.logging_module import get_log

_log = get_log(__name__)


class DropdownTickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def close(self, ctx: commands.Context):
        return

    @commands.command()
    async def sendCHTKTView(self, ctx):
        return


async def setup(bot):
    await bot.add_cog(DropdownTickets(bot))
