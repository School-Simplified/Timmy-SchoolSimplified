from discord.ext import commands

from core.common import Emoji


class TutorBotStaffCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return Emoji.timmyTutoring

    @commands.command()
    async def ticketdropdown(self, ctx):
        return

    @commands.command(name="schedule")
    async def schedule(self, ctx):
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(TutorBotStaffCMD(bot))