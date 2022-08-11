from discord.ext import commands


class GSuiteLogin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pasteGSuiteButton(self, ctx):
        return


async def setup(bot):
    await bot.add_cog(GSuiteLogin(bot))
