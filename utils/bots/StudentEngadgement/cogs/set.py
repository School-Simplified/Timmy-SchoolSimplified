from discord.ext import commands
from discord.app_commands import command, guilds
import discord
from core.common import MAIN_ID, SET_ID


class Engagement(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @property
    def display_group(self) -> str:
        return "Student Engagement"

    @property
    def display_emoji(self) -> str:
        return "Student Engagement"

    @command(name="acceptance_letter")
    @guilds(discord.Object(MAIN_ID.g_main))
    async def __college_accept(self, interaction: discord.Interaction, file: discord.Attachment):
        embed = discord.Embed(
            title="College Acceptance Letter",
            color=0xa4d1de,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.set_image(url=file.url)
        await interaction.response.send_message("Submitted! Congrats!!")
        channel = self.bot.get_channel(SET_ID.ch_college_acceptance)
        await channel.send(embed=embed)

    @command(name="puzzle_guess")
    @guilds(discord.Object(MAIN_ID.g_main))
    async def _guess(self, interaction: discord.Interaction, guess: str):
        """
        :param guess: The guess you are making to the weekly puzzle
        """
        embed = discord.Embed(
            color=0xC387FF,
            title="Puzzle Guess",
            description=f"```{guess}```",
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message("Your guess has been submitted!", ephemeral=True)
        guess_channel = self.bot.get_channel(952402735167320084)
        await guess_channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Engagement(bot))
