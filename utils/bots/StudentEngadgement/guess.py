import discord
from discord.ext import commands
from discord.app_commands import command, guilds
from core.common import MAIN_ID, SET_ID


class Engagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="puzzle_guess",
        description="Submit a guess for the weekly puzzle!",
    )
    @guilds(MAIN_ID.g_main)
    async def _guess(self, interaction: discord.Interaction, guess: str):
        embed = discord.Embed(
            color=0xc387ff,
            title="Puzzle Guess",
            description=guess,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        guess_channel: discord.TextChannel = self.bot.get_channel(SET_ID.ch_puzzle)
        await guess_channel.send(embed=embed)
        await interaction.response.send_message("Your guess has been submitted!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Engagement(bot))
