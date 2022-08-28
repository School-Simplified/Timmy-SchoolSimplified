import os
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from core.common import Colors

class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Reference to documentation")
    async def help(self, interaction: discord.Interaction):
        line_count = 0

        for file in Path("utils").glob("**/*.py"):
            if "!" in file.name or "DEV" in file.name:
                continue
            num_lines_cogs = sum(1 for line in open(f"{file}", encoding="utf8"))
            line_count += num_lines_cogs

        num_lines_main = sum(1 for line in open(f"./main.py", encoding="utf8"))
        line_count += num_lines_main
        line_count = f"{line_count:,}"

        embed = discord.Embed(color=Colors.ss_blurple, title="Hey, I'm Timmy, School Simplified’s very own mascot! 👋",
                              description=f"\n`Coded in {line_count} lines`"
                                          f"\n\nRead the documentation here: https://ssimpl.org/bot-docs")
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))