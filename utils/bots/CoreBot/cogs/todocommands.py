import discord
from core import database
from discord.ext import commands


class TodoCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.interaction = []

    @commands.group()
    async def todo(self, ctx):
        pass

    @todo.command()
    async def add(self, ctx, *, item):
        database.db.connect(reuse_if_open=True)

        q: database.ToDo = database.ToDo.create(discordID=ctx.author.id, item=item)
        q.save()

        embed = discord.Embed(
            title="Successfully Added Item!",
            description=f"{item} has been added successfully with the id `{str(q.id)}`.",
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)

        database.db.close()

    @todo.command()
    async def remove(self, ctx, *, num: int):
        database.db.connect(reuse_if_open=True)

        query = database.ToDo.select().where(database.ToDo.id == num)
        if query.exists():
            query = query.get()

            query.delete_instance()

            embed = discord.Embed(
                title="Successfully Removed Item!",
                description=f"'{query.item}'\nhas been removed from the database!",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid Item!",
                description="Invalid Input Provided: (No Record Found)",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)

        database.db.close()

    @todo.command()
    async def list(self, ctx):
        database.db.connect(reuse_if_open=True)

        todoList = []
        query = database.ToDo.select().where(database.ToDo.discordID == ctx.author.id)
        for todo in query:
            todoList.append(f"{str(todo.id)}) {todo.item}")

        todoFinal = "\n".join(todoList)

        database.db.close()
        embed = discord.Embed(
            title="Your ToDo List!", description=todoFinal, color=discord.Color.green()
        )
        embed.set_footer(
            text="You can use +todo add (item)/+todo remove (item id) to modify this!"
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(TodoCMD(bot))
