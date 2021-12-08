import discord
from discord.ext import commands

class Donation(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["donation"])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def donate(self, ctx: commands.Context):
        if ctx.author.id == 305354423801217025:
            await ctx.send("Donation linke here")

def setup(bot):
    bot.add_cog(bot)