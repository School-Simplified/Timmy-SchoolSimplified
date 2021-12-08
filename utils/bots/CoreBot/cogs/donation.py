import discord
from discord.ext import commands
from core.common import hexColors

class Donation(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["donation"])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def donate(self, ctx: commands.Context):
        if ctx.author.id == 305354423801217025:
            embedDonate = discord.Embed(
                color=hexColors.ss_blurple,
                title=f"Donate",
                description=f"We do not charge anything for our services, so we rely on your donations! Please consider donating to us."
                            f"\n\n**Donate here: https://schoolsimplified.org/donate**"
            )
            embedDonate.set_footer(text="Great thanks to all our donors!")
            await ctx.send(embed=embedDonate)

def setup(bot):
    bot.add_cog(Donation(bot))