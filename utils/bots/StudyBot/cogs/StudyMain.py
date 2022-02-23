import discord
from discord.ext import commands

from core import database
from core.common import hexColors


class StudyToDo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(aliaseS=["study-todo"])
    async def studytodo(self, ctx: commands.Context):
        if ctx.message.content == "+studytodo":
            subcommands = "/".join(
                sorted(subcommand.name for subcommand in self.studytodo.commands)
            )
            signature = f"{ctx.prefix}{ctx.command.qualified_name} <{subcommands}>"

            embed = discord.Embed(
                color=hexColors.red_error,
                title="Missing/Extra Required Arguments Passed In!",
                description=f"You have missed one or several arguments in this command"
                f"\n\nUsage:"
                f"\n`{signature}`",
            )
            embed.set_footer(
                text="Consult the Help Command if you are having trouble or call over a Bot Manager!"
            )
            await ctx.send(embed=embed)

    @studytodo.command()
    async def add(self, ctx: commands.Context, *, item):
        """
        Adds an item to the study to-do list of the author/owner.
        """

        query: database.StudyToDo = database.StudyToDo.create(
            discordID=ctx.author.id, item=item
        )
        query.save()

        embed = discord.Embed(
            title="Successfully Added Item!",
            description=f"`{item}` has been added successfully with the id `{str(query.id)}`.",
            color=hexColors.green_confirm,
        )
        embed.set_footer(text="StudyBot")
        await ctx.send(embed=embed)

    @studytodo.command()
    async def remove(self, ctx, todo_id: int):
        """
        Removes an item from the study to-do list of the author/owner.
        """

        query = database.StudyToDo.select().where(database.StudyToDo.id == todo_id)

        if query.exists():
            query = query.get()
            query.delete_instance()

            embed = discord.Embed(
                title="Successfully Removed Item!",
                description=f"`{query.item}` has been removed from the database!",
                color=hexColors.green_confirm,
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
        query = database.StudyToDo.select().where(
            database.StudyToDo.discordID == ctx.author.id
        )
        for todo in query:
            todoList.append(f"{str(todo.id)}) {todo.item}")

        todoFinal = "\n".join(todoList)

        embed = discord.Embed(
            title="Your Study-ToDo List!",
            description=todoFinal,
            color=discord.Color.green(),
        )
        embed.set_footer(
            text="You can use +studytodo add (item)/+studytodo remove (item id) to modify this!"
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(StudyToDo(bot))
