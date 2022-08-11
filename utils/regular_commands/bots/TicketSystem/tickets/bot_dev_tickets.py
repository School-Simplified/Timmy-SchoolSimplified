from discord.ext import commands, tasks


class TechProjectCMD(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leadershipPost(self, ctx):
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(TechProjectCMD(bot))
