from discord.ext import commands
from discord.app_commands import command, guilds, check
import discord
from core import database
from core.common import MAIN_ID, SET_ID

blacklist = []


def spammer_check():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id not in blacklist

    return check(predicate)


def reload_blacklist():
    blacklist.clear()
    for user_id in database.ResponseSpamBlacklist:
        blacklist.append(user_id)


class Engagement(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        for user_id in database.ResponseSpamBlacklist:
            blacklist.append(user_id)

    @command(name="acceptance_letter")
    @spammer_check()
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
    @spammer_check()
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
        guess_channel = self.bot.get_channel(SET_ID.ch_puzzle)
        await guess_channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Engagement(bot))
