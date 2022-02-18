import discord
from discord.ext import commands
from core.common import hexColors, Others


class Donation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["donation"])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def donate(self, ctx: commands.Context):
        timmyDonation_png = discord.File(
            Others.timmyDonation_path, filename=Others.timmyDonation_png
        )

        embedDonate = discord.Embed(
            color=hexColors.ss_blurple,
            title=f"Donate",
            description=f"Thank you for your generosity in donating to School Simplified. "
            f"We do not charge anything for our services, and your support helps to further our mission "
            f"to *empower the next generation to revolutionize the future through learning*."
            f"\n\n**Donate here: https://schoolsimplified.org/donate**",
        )
        embedDonate.set_footer(text="Great thanks to all our donors!")
        embedDonate.set_thumbnail(url=f"attachment://{Others.timmyDonation_png}")
        await ctx.send(embed=embedDonate, file=timmyDonation_png)


def setup(bot):
    bot.add_cog(Donation(bot))
