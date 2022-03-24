from discord.app_commands import describe, Group, command, guilds
from discord.ext import commands
import discord
from core.common import MAIN_ID, SET_ID
from core import database
from set import reload_blacklist


class SetSuggestBlacklist(commands.Cog, Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name="set_blacklist")
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == 752984497259151370

    @command(name="add")
    @guilds(MAIN_ID.g_main, SET_ID.g_set)
    @describe(user="User ID or mention")
    async def __add(self, interaction: discord.Interaction, user: discord.User):
        """Blacklist a user from suggesting and submitting puzzle guesses"""

        database.db.connect(reuse_if_open=True)
        q: database.Blacklist = database.ResponseSpamBlacklist.create(discordID=user.id)
        q.save()
        reload_blacklist()
        embed = discord.Embed(
            title="Successfully Blacklisted User!",
            description=f"{user.mention} has been added to the blacklist.\n"
                        f"`User ID:` `{user.id}`",
            color=discord.Color.brand_green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @command(name="remove")
    @guilds(MAIN_ID.g_main, SET_ID.g_set)
    @describe(user="User ID or mention")
    async def __remove(self, interaction: discord.Interaction, user: discord.User):
        """Unblacklist a user from suggesting and submitting puzzle guesses"""

        database.db.connect(reuse_if_open=True)
        query = database.ResponseSpamBlacklist.select().where(
            database.ResponseSpamBlacklist.discordID == user.id
        )
        if query.exists():
            query = query.get()
            query.delete_instance()
            reload_blacklist()
            embed = discord.Embed(
                title="Successfully Removed User!",
                description=f"{user.mention} has been removed from the blacklist!"
                            f"`User ID:` `{user.id}`",
                color=discord.Color.brand_green(),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="User Not Found in Blacklist",
                description="Invalid Provided: (No Record Found)",
                color=discord.Color.brand_red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @command(name="reload")
    @guilds(MAIN_ID.g_main, SET_ID.g_set)
    async def __reload(self, interaction: discord.Interaction):
        """Force reload the blacklist"""
        reload_blacklist()
        await interaction.response.send_message("Complete!")


async def setup(bot: commands.Bot):
    await bot.add_cog(SetSuggestBlacklist(bot))
