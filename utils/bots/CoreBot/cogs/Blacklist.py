import discord
from core import database
from core.checks import is_botAdmin3, is_botAdmin4, predicate_LV4, predicate_LV3
from discord.ext import commands
from dotenv import load_dotenv
from discord import SlashCommandGroup, CommandPermission

load_dotenv()


class BlacklistCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.group(aliases=["bl"])
    # async def blacklist(self, ctx):
    #     pass
    blacklist = SlashCommandGroup(
        "blacklist",
        "Commands managing the bot's blacklist",
        permissions=[
            CommandPermission(
                id=866373953001619507,  # STAFF ROLE IN MAIN
                type=1,
                permission=True,
                guild_id=763119924385939498,  # MAIN SERVER ID
            ),
            CommandPermission(
                id=891521033700540457,  # BOT DEV TEAM ROLE IN IT
                type=1,
                permission=True,
                guild_id=932066545117585428,  # IT SERVER
            ),
            CommandPermission(
                id=891521034333880410,  # IT DEPARTMENT ROLE
                type=1,
                permission=True,
                guild_id=891521033700540457,  # SS STAFF SERVER
            ),
        ],
        guild_ids=[
            763119924385939498,  # MAIN
            932066545117585428,  # IT
            891521033700540457,  # SS STAFF
        ],
    )

    @blacklist.command()
    async def add(self, ctx, user: str):
        if not predicate_LV4(ctx):
            return await ctx.respond(
                "You do not have the required permissions to run this command!"
            )
        user = self.bot.get_user(int(user))

        database.db.connect(reuse_if_open=True)
        q: database.Blacklist = database.Blacklist.create(discordID=user.id)
        q.save()

        embed = discord.Embed(
            title="Successfully Blacklisted User!",
            description=f"{user.mention} has been added to the blacklist.",
            color=discord.Color.gold(),
        )
        await ctx.respond(embed=embed)

        database.db.close()

    @blacklist.command()
    async def remove(self, ctx, user: str):
        if not predicate_LV4(ctx):
            return await ctx.respond(
                "You do not have the required permissions to run this command!"
            )

        user = self.bot.get_user(int(user))
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
                color=discord.Color.green(),
            )
            await ctx.respond(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid User!",
                description="Invalid Provided: (No Record Found)",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed)

        database.db.close()

    @blacklist.command()
    async def list(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        if not predicate_LV3(ctx):
            return await ctx.respond(
                "You do not have the required permissions to run this command!"
            )
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
            color=discord.Color.red(),
        )
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(BlacklistCMD(bot))
