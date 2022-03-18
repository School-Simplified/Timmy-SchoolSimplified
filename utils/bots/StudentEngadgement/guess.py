import discord
from discord import Option, slash_command, SlashCommandGroup
from discord.ext import commands
from core.common import MAIN_ID


class Engagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="puzzle_guess",
        guild_ids=[MAIN_ID.g_main],
    )
    async def _guess(self, ctx: discord.ApplicationContext, guess: str):
        """
        :param guess: The guess you are making to the weekly puzzle
        """
        embed = discord.Embed(
            color=0xc387ff,
            title="Puzzle Guess",
            description=f"```{guess}```",
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        ssd: discord.Guild = self.bot.get_guild(778406166735880202)
        guess_channel: discord.TextChannel = ssd.get_channel(950083341967843398)
        await guess_channel.send(embed=embed)
        await ctx.respond("Your guess has been submitted!", ephemeral=True)

    __suggest = SlashCommandGroup(
        "suggest",
        "Suggest something... ",
        guild_ids=[MAIN_ID.g_main]
    )

    @__suggest.command()
    async def book(
            self,
            ctx: discord.ApplicationContext,
            title: Option(
                str,
                description="Which book are you recommending?"
            ),
            rating: Option(
                int,
                max_value=10,
                min_value=0,
                description="What rating does this book have?"
            ),
            description: Option(
                str,
                description="Give a short description of the book with no spoilers."
            ),
            reason: Option(
                str,
                description="Why do you want to recommend this book?"
            )
    ):
        embed = discord.Embed(
            title=f"Media/Book Suggestion: {title}",
            description=description
        )
        embed.add_field(
            name="Short description of the book",
            value=description[:1024]
        )
        embed.add_field(
            name="Why do you want to recommend this book?",
            value=reason[:1024]
        )
        embed.add_field(
            name="Rating",
            value=f"{rating}"
        )
        await ctx.respond("Sending suggestion...", ephemeral=True)

        channel = self.bot.get_guild(950799439625355294).get_channel(954190487026274344)
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Engagement(bot))
