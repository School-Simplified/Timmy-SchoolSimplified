import discord
from discord.ext import commands

from core import database


class StudyToDo(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.group(aliaseS=["study-todo"])
    async def studytodo(self, ctx):
        print("STUDYTODO")

    @studytodo.command()
    async def add(self, ctx: commands.Context, *, item):
        """
        Adds an item to the study to-do list of the author/owner.
        """

        query: database.StudyToDo = database.StudyToDo.create(discordID=ctx.author.id, item=item)
        query.save()

        embed = discord.Embed(
            title="Successfully Added Item!",
            description=f"{item} has been added successfully with the id `{str(q.id)}`.",
            color=discord.Color.gold(),
        )
        embed.set_footer(text="StudyBot")
        await ctx.send(embed=embed)

    @studytodo.command()
    async def remove(self, ctx, todo_id: int):
        """
        Removes an item from the study to-do list of the author/owner.
        """

        query = database.StudyToDo.select().where(database.ToDo.id == todo_id)

        if query.exists():
            query = query.get()
            query.delete_instance()

            embed = discord.Embed(
                title="Successfully Removed Item!",
                description=f"'{query.item}'\nhas been removed from the database!",
                color=discord.Color.green(),
            )
            embed.set_footer(text="StudyBot")
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid Item!",
                description="Invalid Input Provided: (No Record Found)",
                color=discord.Color.red(),
            )
            embed.set_footer(text="StudyBot")
            await ctx.send(embed=embed)

    @studytodo.command()
    async def list(self, ctx):
        todoList = []
        query = database.ToDo.select().where(database.ToDo.discordID == ctx.author.id)
        for todo in query:
            todoList.append(f"{str(todo.id)}) {todo.item}")

        todoFinal = "\n".join(todoList)

        embed = discord.Embed(
            title="Your Study-ToDo List!", description=todoFinal, color=discord.Color.green()
        )
        embed.set_footer(
            text="You can use +studytodo add (item)/+studytodo remove (item id) to modify this!"
        )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(StudyToDo(bot))