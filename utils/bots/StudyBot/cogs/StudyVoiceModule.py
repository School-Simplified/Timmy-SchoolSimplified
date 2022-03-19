import asyncio
import datetime
from datetime import datetime, timedelta

import discord
from core import database
from core.common import Emoji, MAIN_ID, STAFF_ID, TUT_ID, TECH_ID, SandboxConfig, SelectMenuHandler
from discord.ext import commands, tasks
import pytz

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

def convert_time_to_seconds(time):
    try:
        value = int(time[:-1]) * time_convert[time[-1]]
    except:
        value = time
    finally:
        if value < 60:
            return None
        else:
            return value


def showFutureTime(time):
    now = datetime.now(EST)
    output = convert_time_to_seconds(time)
    if output is None:
        return None

    add = timedelta(seconds=int(output))
    now_plus_10 = now + add

    return now_plus_10.strftime(r"%I:%M %p")


def showTotalMinutes(dateObj: datetime):
    now = datetime.now(EST)
    dateObj = pytz.timezone("America/New_York").localize(dateObj)

    deltaTime = now - dateObj

    totalmin = deltaTime.total_seconds() // 60

    return totalmin, now


async def addLeaderboardProgress(self, member: discord.Member):
    print("addLeaderboardProgress called")

    StudySessionQ = database.StudyVCDB.select().where(database.StudyVCDB.discordID == member.id)
    if StudySessionQ.exists():
        StudySessionQ = StudySessionQ.get()
        totalmin, now = showTotalMinutes(StudySessionQ.StartTime)
        leaderboardQuery = database.StudyVCLeaderboard.select().where(database.StudyVCLeaderboard.discordID == member.id)

        isNewLvl = False
        if leaderboardQuery.exists():
            leaderboardQuery = leaderboardQuery.get()
            leaderboardQuery.TTS = totalmin + leaderboardQuery.TTS
            leaderboardQuery.TTSWeek = totalmin + leaderboardQuery.TTSWeek
            leaderboardQuery.totalSessions = leaderboardQuery.totalSessions + 1

            currentLvl = leaderboardQuery.level
            currentXP = leaderboardQuery.xp
            currentTotalXP = leaderboardQuery.totalXP

            xpNeeded = getXPForNextLvl(currentLvl)
            print(f"xpNeeded: {xpNeeded}")
            xpEarned = totalmin * self.xpPerMinute

            newXP = currentXP + xpEarned
            newTotalXP = currentTotalXP + xpEarned
            newLvl = currentLvl

            if newXP >= xpNeeded:

                isNewLvl = True
                newXPNeeded = xpNeeded
                while newXP >= newXPNeeded:
                    newXP -= newXPNeeded
                    newLvl += 1
                    newXpNeeded = getXPForNextLvl(newLvl)

            leaderboardQuery.xp = newXP
            leaderboardQuery.totalXP = newTotalXP
            leaderboardQuery.level = newLvl

            leaderboardQuery.save()

        else:
            currentLvl = 0
            currentXP = 0
            currentTotalXP = 0

            xpNeeded = getXPForNextLvl(currentLvl)
            xpEarned = totalmin * self.xpPerMinute

            newXP = currentXP + xpEarned
            newTotalXP = currentTotalXP + xpEarned
            newLvl = currentLvl

            if newXP >= xpNeeded:

                isNewLvl = True
                newXPNeeded = xpNeeded
                while newXP >= newXPNeeded:
                    newXP -= newXPNeeded
                    newLvl += 1
                    newXpNeeded = getXPForNextLvl(newLvl)

            q = database.StudyVCLeaderboard.create(
                discordID=member.id,
                TTS=totalmin,
                totalSessions=0,
                xp=newXP,
                totalXP=newTotalXP,
                level=newLvl,
                TTSWeek=totalmin
            )
            q.save()


        if isNewLvl:
            if newLvl == 5:
                role = None  # TODO: get lvl 5 role
                roleStr = f"\nYou've earned a new role: {role}"

            elif newLvl == 10:
                role = None  # TODO: get lvl 10 role
                roleStr = f"\nYou've earned a new role: {role}"

            elif newLvl == 20:
                role = None  # TODO: get lvl 20 role
                roleStr = f"\nYou've earned a new role: {role}"

            elif newLvl == 30:
                role = None  # TODO: get lvl 30 role
                roleStr = f"\nYou've earned a new role: {role}"

            elif newLvl == 40:
                role = None  # TODO: get lvl 40 role
                roleStr = f"\nYou've earned a new role: {role}"

            elif newLvl == 50:
                role = None  # TODO: get lvl 50 role
                roleStr = f"\nYou've earned a new role: {role}"

            elif newLvl == 60:
                role = None  # TODO: get lvl 60 role
                roleStr = f"\nYou've earned a new role: {role}"

            elif newLvl == 70:
                role = None  # TODO: get lvl 70 role
                roleStr = f"\nYou've earned a new role: {role}"

            elif newLvl == 80:
                role = None  # TODO: get lvl 80 role
                roleStr = f"\nYou've earned a new role: {role}"

            elif newLvl == 90:
                role = None  # TODO: get lvl 90 role
                roleStr = f"\nYou've earned a new role: {role}"

            elif newLvl == 100:
                role = None  # TODO: get lvl 100 role
                roleStr = f"\nYou've earned a new role: {role}"

            else:
                roleStr = ""

            dmMSG = f"{member.mention}, you've reached level **{newLvl}** in Study VC!" \
                    f"{roleStr}"
            try:
                await member.send(dmMSG)
            except:
                pass

        if newLvl < 5:
            pass

        elif newLvl < 10:
            # TODO: add user lvl 5 role
            pass

        elif newLvl < 20:
            # TODO: add user lvl 10 role
            pass

        elif newLvl < 30:
            # TODO: add user lvl 20 role
            pass

        elif newLvl < 40:
            # TODO: add user lvl 30 role
            pass

        elif newLvl < 50:
            # TODO: add user lvl 40 role
            pass

        elif newLvl < 60:
            # TODO: add user lvl 50 role
            pass

        elif newLvl < 70:
            # TODO: add user lvl 60 role
            pass

        elif newLvl < 80:
            # TODO: add user lvl 70 role
            pass

        elif newLvl < 90:
            # TODO: add user lvl 80 role
            pass

        elif newLvl < 100:
            # TODO: add user lvl 90 role
            pass

        elif newLvl >= 100:
            # TODO: add user lvl 100 role
            pass

    else:
        return
    StudySessionQ = StudySessionQ.get()
    StudySessionQ.StartTime = datetime.now(EST)
    StudySessionQ.Paused = True
    StudySessionQ.save()



async def setNewStudyGoal(self, console: discord.TextChannel, member: discord.Member, renew: bool):
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
        return await MSV.send("Timed out, try again later.")
    
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
        await addLeaderboardProgress(self, member)

        query.goal = goal
        query.RenewalTime = renewal
        query.save()
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


def getXPForNextLvl(lvl: int):
    xpNeeded = (5 * lvl * lvl) + (50 * lvl) + 100

    return xpNeeded


class StudyVCUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xpPerMinute = 30
        self.StudyVCCategory = [945459539967348787]
        self.StudyVCChannels = [954516833694810152]
        self.StudyVCConsole = 954516809577533530

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
        if (
            before.channel is not None
            and (
                after.channel is None
                or after.channel.category_id not in self.StudyVCCategory
                or after.channel.id in self.StudyVCChannels
            )
            and not member.bot
        ):
            await addLeaderboardProgress(self, member)
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
                await console.send(
                    f"{member.mention} Your study goal has been updated to '{goal}'.\n\n**That's it!** Make sure you come back at {renewal.strftime(r'%I:%M %p')} to renew your study session!"
                )
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

    @tasks.loop(seconds=60.0)
    async def StudyVCChecker(self):
        """Loop through each session and check if a user's study session is about to end"""
        console: discord.TextChannel = await self.bot.fetch_channel(self.StudyVCConsole)

        for q in database.StudyVCDB:
            q: database.StudyVCDB = q
            dateObj = pytz.timezone("America/New_York").localize(q.RenewalTime)
            if datetime.now(EST) >= dateObj:
                user = await self.bot.fetch_user(q.discordID)
                await console.send(
                    f"{self.bot.get_user(q.discordID).mention} Your study session has ended, set a new goal!"
                )
                goal, renewal = await setNewStudyGoal(self, console, user, True)
                await console.send(
                    f"{user.mention} Your study goal has been updated to '{goal}'.\n\n**That's it!** Make sure you come back at {renewal.strftime(r'%I:%M %p')} to renew your study session!"
                )
            elif q.RenewalTime - datetime.now(EST) < timedelta(minutes=5):
                await console.send(
                    f"{self.bot.get_user(q.discordID).mention} Your study session is ending in **less than 5 minutes**. (Ends at: {q.RenewalTime.strftime(r'%I:%M %p')})\n\nMaybe renew your study session?"
                )




    
def setup(bot):
    bot.add_cog(StudyVCUpdate(bot))
