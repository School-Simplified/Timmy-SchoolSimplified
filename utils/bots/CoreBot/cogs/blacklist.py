from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.app_commands import Group, command
from discord.ext import commands
from dotenv import load_dotenv

from core import database
from core.checks import slash_is_bot_admin_4, slash_is_bot_admin_3

if TYPE_CHECKING:
    from main import Timmy

load_dotenv()


class Blacklist(commands.Cog):
    def __init__(self, bot: Timmy):
        self.__cog_app_commands__.append(BlacklistCMD(bot))


class BlacklistCMD(Group):
    def __init__(self, bot: Timmy):
        super().__init__(name="blacklist", description="Manage the bot's blacklist")
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return "🔒"

    @property
    def cog(self) -> commands.Cog:
        return self.bot.get_cog("Blacklist")

    @command()
    @slash_is_bot_admin_4()
    async def add(self, interaction: discord.Interaction, user: discord.User):
        database.db.connect(reuse_if_open=True)
        q: database.Blacklist = database.Blacklist.create(discordID=user.id)
        q.save()

        embed = discord.Embed(
            title="Successfully Blacklisted User!",
            description=f"{user.mention} has been added to the blacklist.",
            color=discord.Color.brand_green(),
        )
        await interaction.response.send_message(embed=embed)

        database.db.close()

    @command()
    @slash_is_bot_admin_4()
    async def remove(self, interaction, user: discord.User):
        database.db.connect(reuse_if_open=True)
        query = database.Blacklist.select().where(
            database.Blacklist.discordID == user.id
        )
        if query.exists():
            query = query.get()

            query.delete_instance()

            embed = discord.Embed(
                title="Successfully Removed User!",
                description=f"{user.mention} has been removed from the blacklist!",
                color=discord.Color.brand_green(),
            )
            await interaction.response.send_message(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid User!",
                description="Invalid Provided: (No Record Found)",
                color=discord.Color.brand_red(),
            )
            await interaction.response.send_message(embed=embed)

        database.db.close()

    @command()
    @slash_is_bot_admin_3()
    async def list(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        empty_list = []
        for p in database.Blacklist:
            user = self.bot.get_user(p.discordID)
            if not user:
                user = await self.bot.fetch_user(p.discordID)
            empty_list.append(f"`{user.name}` -> `{user.id}`")

        blacklist_list = "\n".join(empty_list)

        embed = discord.Embed(
            title="Current Blacklist",
            description=blacklist_list,
            color=discord.Color.brand_red(),
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: Timmy) -> None:
    await bot.add_cog(Blacklist(bot))
