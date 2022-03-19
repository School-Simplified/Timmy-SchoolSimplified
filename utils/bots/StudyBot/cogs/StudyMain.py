from datetime import datetime

import discord
import pytz
from core import database
from core.common import hexColors
from discord.ext import commands

EST = pytz.timezone("US/Eastern")

def showTotalMinutes(dateObj: datetime):
    now = datetime.now(EST)

    deltaTime = now - dateObj

    totalmin = deltaTime.total_seconds() // 60

    return totalmin, now

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
    async def set(self, ctx: commands.Context, *, item):
        """
        Adds an item to the study to-do list of the author/owner.
        """

        query: database.StudyVCDB = database.StudyVCDB.select().where(database.StudyVCDB.discordID==ctx.author.id)
        if query.exists():
            query = query.get()
            query.studyTodo = item
            query.save()
            embed = discord.Embed(
                title="Successfully Added Item!",
                description=f"`{item}` has been added successfully with the id `{str(query.id)}`.",
                color=hexColors.green_confirm,
            )
            embed.set_footer(text="StudyBot")
            await ctx.send(embed=embed)
        else:
            return await ctx.send(f"You don't have a study session yet! Make one by joining any StudyVC!")


    @studytodo.command()
    async def end(self, ctx: commands.Context, todo_id: int):
        """
        Removes an item from the study to-do list of the author/owner.
        """
        console: discord.TextChannel = await self.bot.fetch_channel(954516809577533530)

        StudySessionQ = database.StudyVCDB.select().where(database.StudyVCDB.discordID == ctx.author.id)
        if StudySessionQ.exists():
            StudySessionQ = StudySessionQ.get()
            totalmin, now = showTotalMinutes(StudySessionQ.startTime)
            leaderboardQuery = database.StudyVCLeaderboard.select().where(database.StudyVCLeaderboard.discordID == ctx.author.id)
            if leaderboardQuery.exists():
                leaderboardQuery = leaderboardQuery.get()
                leaderboardQuery.totalMinutes = int(totalmin) + leaderboardQuery.totalMinutes
                leaderboardQuery.totalSession = leaderboardQuery.totalSession + 1
                leaderboardQuery.save()

            else:
                q = database.StudyVCLeaderboard.create(
                    discordID=ctx.author.id,
                    totalMinutes=int(totalmin),
                    totalSessions=1,
                )
                q.save()
        else:
            return await ctx.send(f"You don't have a study session yet! Make one by joining any StudyVC!")

        StudySessionQ = StudySessionQ.get()
        StudySessionQ.startTime = datetime.now(EST)
        StudySessionQ.Paused = True
        StudySessionQ.save()
        await console.send(
            f"{ctx.author.mention} has left the channel, saved your current progress!"
        )

    @studytodo.command()
    async def list(self, ctx):
        query = database.StudyToDo.select().where(
            database.StudyToDo.discordID == ctx.author.id
        )
        if query.exists():
            query = query.get()
            embed = discord.Embed(
                title="Study To-Do List",
                description=f"Your current goal: {query.studyTodo}",
                color=hexColors.blue_main,
            )
            embed.set_footer(
                text="You can use +studytodo set (item) to modify this!"
            )
            await ctx.send(embed=embed)

        else:
            return await ctx.send(f"You don't have a study session yet! Make one by joining any StudyVC!")
    
    @studytodo.command()
    async def leaderboard(self, ctx):
        l = []
        for t in database.StudyVCLeaderboard.select().order_by(database.StudyVCLeaderboard.TTS.desc()):
            i = 1
            totalmin, now = showTotalMinutes(t.startTime)
            if totalmin > 60:
                totalmin = totalmin // 60
                totalmin = f"{totalmin} hour(s)"
            else:
                totalmin = f"{totalmin} minute(s)"
            user = await self.bot.fetch_user(t.discordID)
            l.append(f"{str(i)}. {user.name} -> {totalmin}")
            i += 1
        FormattedList = "\n".join(l)
        embed = discord.Embed(
            title="Study Leaderboard",
            description=f"```\n{FormattedList}\n```",
            color=hexColors.ss_blurple,
        )
        embed.set_footer(
            text="StudyBot"
        )
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(StudyToDo(bot))
