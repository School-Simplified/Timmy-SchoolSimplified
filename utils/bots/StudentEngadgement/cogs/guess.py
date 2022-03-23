import discord
from discord import slash_command
from discord.ext import commands
from core.common import MAIN_ID, SET_ID


class Engagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="acceptance_letter", guild_ids=[MAIN_ID.g_main])
    async def __college_accept(self, interaction, file: discord.Attachment):
        embed = discord.Embed(
            title="College Acceptance Letter",
            color=0xa4d1de,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=interaction.author, icon_url=interaction.author.avatar.url)
        embed.set_image(url=file.url)
        await interaction.respond("Submitted! Congrats!!")
        channel = self.bot.fetch_channel(SET_ID.ch_college_acceptance)
        await channel.send(embed=embed)

    @slash_command(name="puzzle_guess", guild_ids=[MAIN_ID.g_main])
    async def _guess(self, interaction, guess: str):
        embed = discord.Embed(
            color=0xC387FF,
            title="Puzzle Guess",
            description=f"{guess}",
            timestamp=discord.utils.utcnow(),
        )

        embed.set_author(name=interaction.author, icon_url=interaction.author.avatar.url)
        await interaction.respond("Your guess has been submitted!", ephemeral=True)
        guess_channel = self.bot.fetch_channel(952402735167320084)
        await guess_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Engagement(bot))
