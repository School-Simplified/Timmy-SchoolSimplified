import discord
from core import database
from core.checks import is_botAdmin3, is_botAdmin4
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class BlacklistCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["bl"])
    async def blacklist(self, ctx):
        pass

    @blacklist.command()
    @is_botAdmin4
    async def add(self, ctx, user: discord.User):
        database.db.connect(reuse_if_open=True)

        q: database.Blacklist = database.Blacklist.create(discordID=user.id)
        q.save()

        embed = discord.Embed(
            title="Successfully Blacklisted User!",
            description=f"{user.mention} has been added to the blacklist.",
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)

    database.db.close()

    @blacklist.command()
    @is_botAdmin4
    async def remove(self, ctx, user: discord.User):
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
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid User!",
                description="Invalid Provided: (No Record Found)",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)

        database.db.close()

    @blacklist.command()
    @is_botAdmin3
    async def list(self, ctx):
        emptylist = []

        for p in database.Blacklist:
            user = await self.bot.fetch_user(p.id)
            emptylist.append(f"`{user.name}` -> `{user.id}`")

        blacklistList = "\n".join(emptylist)

        embed = discord.Embed(
            title="Current Blacklist",
            description=blacklistList,
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(BlacklistCMD(bot))
