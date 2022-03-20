import asyncio
import datetime
from datetime import datetime, timedelta
import pytz

import discord
from discord.ext import commands, tasks

from core import database
from core.common import Emoji, MAIN_ID, STAFF_ID, TUT_ID, TECH_ID, SandboxConfig, SelectMenuHandler
from utils.bots.StudyBot.cogs.StudyMain import addLeaderboardProgress


time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
EST = pytz.timezone("US/Eastern")
duration = {"25 Minute Study Session": 25, "50 Minute Study Session": 50}
SSTypes = [
    discord.SelectOption(
        label="25 Minute Study Session",
        description="Start a 25 minute study session followed by a 5 minute break.",
        emoji="✍️",
    ),
    discord.SelectOption(
        label="50 Minute Study Session",
        description="Start a 25 minute study session followed by a 10 minute break.",
        emoji="💪",
    ),
]


async def setNewStudyGoal(self, console, member: discord.Member, renew: bool):
    now = datetime.now(EST)
    if renew:
        query = database.StudyVCDB.select().where(database.StudyVCDB.discordID == member.id).get()
    MSV = discord.ui.View()
    var = SelectMenuHandler(
        SSTypes, "temp_view:studybot_st1", "Select a duration for your study session"
    )
    MSV.add_item(var)

    await console.send(
        f"{member.mention} You have joined a study channel. Please choose the duration of your study session!",
        view=MSV
    )
    timeout = await MSV.wait()
    if not timeout:
        selection_str = var.view_response
    else:
        await member.move_to(None)
        return await console.send(f"{member.mention} Timed out, try again later.")
    
    await console.send("Send your goal for this study session!")

    try:
        goal = await self.bot.wait_for(
            "message", check=lambda m: m.author == member, timeout=60
        )
    except asyncio.TimeoutError:
        await console.send(
            f"{member.mention} You took too long to enter a study goal. Please try again."
        )
        if renew:
            query.delete_instance()
        return await member.move_to(None)
    goal = goal.content
    renewal = now + timedelta(minutes=duration[selection_str])

    if not renew:
        now = datetime.now(EST)
        q = database.StudyVCDB.create(discordID = member.id, goal = goal, StartTime = datetime.now(EST), RenewalTime = renewal)
        q.save()
    else:
        await addLeaderboardProgress(member)

        query.goal = goal
        query.RenewalTime = renewal
        query.save()

    await console.send(
        f"{member.mention} Your study goal has been updated to '{goal}'.\n\n**That's it!** Make sure you come back at {renewal.strftime(r'%I:%M %p')} to renew your study session!"
    )
    return goal, renewal



def getConsoleCH(column_id):
    q: database.SandboxConfig = (
        database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
    )
    ColumnDict = {
        0: q.ch_tv_console,
        1: q.ch_tv_startvc,
    }
    return ColumnDict[column_id]



class StudyVCUpdate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.xpPerMinute = 30
        self.StudyVCCategory = [945459539967348787]
        self.StudyVCChannels = [954516833694810152]
        self.StudyVCConsole = 954516809577533530
        self.StudyVCGuild = 932066545117585428


        self.StudyVCChecker.start()
    """
    TODO
    
    - Get lvl roles
    - if user not in db -> add xp, level etc.
    - Special role for top time in current week
        - loop that resets TTSWeek every Monday Midnight
    
    - Leaderboard command
        - Paginator
        - button which shows current TTSWeek top 1
    - Rank command
        - Rankcard like Mee6
    """

    def cog_unload(self):
        self.StudyVCChecker.stop()

    @commands.Cog.listener("on_voice_state_update")
    async def StudyVCModule(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        console: discord.TextChannel = await self.bot.fetch_channel(self.StudyVCConsole)
        if member.guild.id != self.StudyVCGuild:
            return
        if (
            before.channel is not None
            and (
                after.channel is None
                or after.channel.category_id not in self.StudyVCCategory
                or after.channel.id in self.StudyVCChannels
            )
            and not member.bot
        ):
            await addLeaderboardProgress(member)
            await console.send(
                f"{member.mention} has left the channel, saved your current progress!"
            )

        elif (
            after.channel is not None
            and after.channel.id in self.StudyVCChannels
            and not member.bot
        ):
            query = database.StudyVCDB.select().where(database.StudyVCDB.discordID == member.id)
            if not query.exists():
                goal, renewal = await setNewStudyGoal(self, console, member, False)
            else:
                query = query.get()
                query.Paused = False
                query.StartTime = datetime.now(EST)
                query.save()

                dateObj = pytz.timezone("America/New_York").localize(query.RenewalTime)
                val = int((dateObj - datetime.now(EST)).total_seconds())

                if datetime.now(EST) >= dateObj:
                    await console.send(
                        f"{member.mention} Your study session ended, set a new goal!"
                    )
                    goal, renewal = await setNewStudyGoal(self, console, member, True)
                    await console.send(
                        f"{member.mention} Your study goal has been updated to '{goal}'.\n\n**That's it!** Make sure you come back at {renewal.strftime(r'%I:%M %p')} to renew your study session!"
                    )

                elif dateObj - datetime.now(EST) < timedelta(minutes=5):
                    await console.send(
                        f"{member.mention} Your study session is ending in **less than 5 minutes**. (Ends at: {query.RenewalTime.strftime(r'%I:%M %p')})\n\nMaybe renew your study session?"
                    )

                else:
                    await console.send(
                        f"{member.mention} You already have a study session going!\n\nMake sure you come back at {query.RenewalTime.strftime(r'%I:%M %p')} to renew your study session!"
                    )


    @tasks.loop(seconds=10) # TODO: change to 60s due of rate limits
    async def StudyVCChecker(self):
        """Loop through each session and check if a user's study session is about to end"""
        print("loop StudyVCChecker")

        StudyVCGuildObj = await self.bot.fetch_guild(self.StudyVCGuild)
        StudyVCConsoleObj = await StudyVCGuildObj.fetch_channel(self.StudyVCConsole)

        for q in database.StudyVCDB:
            dateObj = pytz.timezone("America/New_York").localize(q.RenewalTime)

            member = await StudyVCGuildObj.fetch_member(q.discordID)
            if datetime.now(EST) >= dateObj:
                if member.voice:
                    await member.move_to(None)
                    await StudyVCConsoleObj.send(
                        f"{member.mention} Your study session has ended, set a new goal!"
                    )
                    goal, renewal = await setNewStudyGoal(self, StudyVCConsoleObj, member, True)
                    await StudyVCConsoleObj.send(
                        f"{member.mention} Your study goal has been updated to '{goal}'.\n\n**That's it!** Make sure you come back at {renewal.strftime(r'%I:%M %p')} to renew your study session!"
                    )

            elif dateObj - datetime.now(EST) < timedelta(minutes=5):
                await StudyVCConsoleObj.send(
                    f"{member.mention} Your study session is ending in **less than 5 minutes**. (Ends at: {dateObj.strftime(r'%I:%M %p')})\n\nMaybe renew your study session?"
                )




    
def setup(bot):
    bot.add_cog(StudyVCUpdate(bot))
