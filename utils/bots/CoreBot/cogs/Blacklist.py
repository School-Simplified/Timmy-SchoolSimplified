import discord
from core import database
from core.checks import slash_is_bot_admin_4, slash_is_bot_admin_3
from discord.ext import commands
from dotenv import load_dotenv
from discord.app_commands import Group, command

load_dotenv()


class BlacklistCMD(commands.Cog, Group):
    def __init__(self, bot):
        super().__init__(
            name="blacklist",
            description="Manage the bot's blacklist"
        )
        self.bot = bot

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
            await interaction.respond(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid User!",
                description="Invalid Provided: (No Record Found)",
                color=discord.Color.brand_red(),
            )
            await interaction.respond(embed=embed)

        database.db.close()

    @command()
    @slash_is_bot_admin_3()
    async def list(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        empty_list = []
        for p in database.Blacklist:
            try:
                user = self.bot.get_user(p.id)
                empty_list.append(f"`{user.name}` -> `{user.id}`")
            except:
                empty_list.append(f"`{p}`")

        blacklist_list = "\n".join(empty_list)

        embed = discord.Embed(
            title="Current Blacklist",
            description=blacklist_list,
            color=discord.Color.brand_red(),
        )
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BlacklistCMD(bot))
