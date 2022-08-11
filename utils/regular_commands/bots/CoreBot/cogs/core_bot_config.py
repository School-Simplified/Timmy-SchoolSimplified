from discord.ext import commands
from dotenv import load_dotenv


class CoreBotConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.__cog_name__ = "Core Bot Config"
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return "⚙️"

    @commands.group(aliases=["f"])
    async def filters(self, ctx):
        return

    @commands.command()
    async def Fmodify(self, ctx):
        return

    @commands.group(aliases=["pre"])
    async def prefix(self, ctx):
        return

    @commands.group(aliases=["cog"])
    async def cogs(self, ctx):
        return

    @commands.command(name="gitpull")
    async def _gitpull(self, ctx):
        return

    @commands.group()
    async def w(self, ctx):
        return

async def setup(bot):
    await bot.add_cog(CoreBotConfig(bot))
