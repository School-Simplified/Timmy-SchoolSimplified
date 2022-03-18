import asyncio

import discord
from discord.ext import commands
from core.common import TECH_ID


class SuggestionCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def suggest(self, ctx, suggestion):
        embed = discord.Embed(
            title="Confirmation",
            description="Are you sure you want to submit this suggestion? Creating irrelevant "
            "suggestions will warrant a blacklist and you will be subject to a "
            "warning/mute.",
            color=discord.Colour.teal(),
        )
        embed.add_field(name="Suggestion Collected", value=suggestion)
        embed.set_footer(
            text="Double check this suggestion || MAKE SURE THIS SUGGESTION IS RELATED TO THE BOT, NOT THE DISCORD "
            "SERVER! "
        )

        message = await ctx.send(embed=embed)
        reactions = ["✅", "❌"]
        for emoji in reactions:
            await message.add_reaction(emoji)

        def check2(reaction, user):
            return user == ctx.author and (
                str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌"
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=150.0, check=check2
            )
            if str(reaction.emoji) == "❌":
                await ctx.send("Okay, I won't send this.")
                await message.delete()
                return
            else:
                await message.delete()
                guild = await self.bot.fetch_guild(TECH_ID.g_tech)
                channel = await guild.fetch_channel(TECH_ID.ch_tracebacks)

                embed = discord.Embed(
                    title="New Suggestion!",
                    description=f"User: {ctx.author.mention}\nChannel: {ctx.channel.mention}",
                    color=discord.Colour.teal(),
                )
                embed.add_field(name="Suggestion", value=suggestion)

                await channel.send(embed=embed)
                await ctx.send(
                    "I have sent in the suggestion! You will get a DM back depending on its status!"
                )

        except asyncio.TimeoutError:
            await ctx.send(
                "Looks like you didn't react in time, please try again later!"
            )

    @suggest.error
    async def suggest_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            msg = "You can't suggest for: `{} minutes and {} seconds`".format(
                round(m), round(s)
            )
            await ctx.send(msg)

        else:
            raise error


def setup(bot):
    bot.add_cog(SuggestionCMD(bot))
