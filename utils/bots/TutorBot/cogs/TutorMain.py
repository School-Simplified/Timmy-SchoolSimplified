import discord
from core import database
from discord.ext import commands


class TutorMain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RepeatEmoji = {
            False: "\U00002b1b",
            True: "🔁"
        }

    @commands.command()
    async def view(self, ctx, id = None):
        if id == None:
            query : database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.TutorID == ctx.author.id)

            embed = discord.Embed(title = "Scheduled Tutor Sessions", color = discord.Color.dark_blue())
            embed.add_field(name = "Schedule:", value = f"{ctx.author.name}'s Schedule:")

            if query.count() == 0:
                embed.add_field(name = "List:", value = "You have no tutor sessions yet!", inline = False)
                
            else:
                ListTen = []
                i = 0
                for entry in query:
                    studentUser = await self.bot.fetch_user(entry.StudentID)
                    date = entry.Date.strftime("%m/%d/%Y")
                    amORpm = entry.Date.strftime("%p")
                    ListTen.append(f"{self.RepeatEmoji[entry.Repeat]} `{entry.SessionID}`- - {date} {entry.Time} {amORpm} -> {studentUser.name}")

                embed.add_field(name = "List:", value = "\n".join(ListTen), inline = False)
            embed.set_thumbnail(url = "https://media.discordapp.net/attachments/875233489727922177/877378910214586368/tutoring.png?width=411&height=532")
            await ctx.send(embed = embed)

        else:
            entry = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.SessionID == id)
            if entry.exists():
                entry = entry.get()

                studentUser = await self.bot.fetch_user(entry.StudentID)

                date = entry.Date.strftime("%m/%d/%Y")
                amORpm = entry.Date.strftime("%p")

                embed = discord.Embed(title = "Tutor Session Query", description =f"Here are the query results for {id}")
                embed.add_field(name = "Values", value = f"**Session ID:** `{entry.SessionID}`\n**Student:** `{studentUser.name}`\n**Tutor:** `{ctx.author.name}`\n**Date:** `{date}`\n**Time:** `{entry.Time}`\n**Repeat?:** {self.RepeatEmoji[entry.Repeat]}")
                embed.set_footer(text = f"Subject: {entry.Subject}")
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(title = "Invalid Session", description = "This session does not exist, please check the ID you've provided!", color = discord.Color.red())
                await ctx.send(embed = embed)

    #@commands.command()
    #async def get(self, ctx, id):

    #@commands.command()
    #async def reqtutor(self, ctx, date, time, timezone, id, repeats):

    #@commands.command()
    #async def reqinterview(self, ctx):

def setup(bot):
    bot.add_cog(TutorMain(bot))


