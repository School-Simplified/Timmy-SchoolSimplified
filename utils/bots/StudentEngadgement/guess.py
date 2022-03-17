from typing import Any

import discord
from discord import AppCommandOptionType, File
from discord.app_commands import command, guilds, Transformer, Transform
from discord.ext import commands
from core.common import MAIN_ID


class Attachment(Transformer):

    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: Any) -> Any:

class Engagement(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        ...

    @command(name="puzzle_guess", description="Use this to guess the weekly puzzle solution!")
    @guilds(763119924385939498)
    async def _guess(self, interaction: discord.Interaction, guess: str):
        """
        :param guess: The guess you are making to the weekly puzzle
        """
        embed = discord.Embed(
            color=0xc387ff,
            title="Puzzle Guess",
            description=f"```{guess}```",
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        ssd: discord.Guild = self.bot.get_guild(778406166735880202)
        guess_channel: discord.TextChannel = ssd.get_channel(950083341967843398)
        await guess_channel.send(embed=embed)
        await interaction.response.send_message("Your guess has been submitted!", ephemeral=True)

    @command(name="college_accept", description="Send a picture of your college acceptance!")
    @guilds(763119924385939498)
    async def _college_accept(
            self, interaction: discord.Interaction, photo: Transform[discord.Attachment, ]
    ):
        embed = discord.Embed(
            color=0xc387ff,
            title="Puzzle Guess",
            timestamp=discord.utils.utcnow()
        )

        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        ssd: discord.Guild = self.bot.get_guild(778406166735880202)
        guess_channel: discord.TextChannel = ssd.get_channel()  # TODO FIX THIS
        await guess_channel.send(embed=embed)
        await interaction.response.send_message("Your guess has been submitted!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Engagement(bot))
