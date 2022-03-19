import asyncio
import datetime
from datetime import datetime, timedelta

import discord
from core import database
from core.common import Emoji, MAIN_ID, STAFF_ID, TUT_ID, TECH_ID, SandboxConfig, SelectMenuHandler
from discord.ext import commands
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
        emoji="⚡️",
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

    deltaTime = now - dateObj

    totalmin = deltaTime.total_seconds() // 60

    return totalmin, now


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
    def __init__(self, bot):
        self.bot = bot
        

    @commands.Cog.listener("on_voice_state_update")
    async def StudyVCModule(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        console: discord.TextChannel = await self.bot.fetch_channel(954516809577533530)
        if (
            before.channel is not None
            and (
                after.channel is None
                or after.channel.category_id not in self.categoryIDs
                or after.channel.id in self.staticChannels
            )
            and not member.bot
        ):
            StudySessionQ = database.StudyVCDB.select().where(database.StudyVCDB.discordID == member.id)
            if StudySessionQ.exists():
                StudySessionQ = StudySessionQ.get()
                totalmin, now = showTotalMinutes(StudySessionQ.startTime)
                leaderboardQuery = database.StudyVCLeaderboard.select().where(database.StudyVCLeaderboard.discordID == member.id)
                if leaderboardQuery.exists():
                    leaderboardQuery = leaderboardQuery.get()
                    leaderboardQuery.totalMinutes = int(totalmin) + leaderboardQuery.totalMinutes
                    leaderboardQuery.totalSession = leaderboardQuery.totalSession + 1
                    leaderboardQuery.save()

                else:
                    q = database.StudyVCLeaderboard.create(
                        discordID=member.id,
                        totalMinutes=int(totalmin),
                        totalSessions=1,
                    )
                    q.save()
            else:
                return
            StudySessionQ = StudySessionQ.get()
            StudySessionQ.startTime = datetime.now(EST)
            StudySessionQ.Paused = True
            StudySessionQ.save()
            await console.send(
                f"{member.mention} has left the channel, saved your current progress!"
            )


        if (
            after.channel is not None
            and after.channel.id in self.presetChannels
            and not member.bot
        ):
            query = database.StudyVCDB.select().where(database.StudyVCDB.discordID == member.id)
            if not query.exists():
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
                    selection_str = MSV.value
                else:
                    await member.move_to(None)
                    return await MSV.send("Timed out, try again later.")
                
                await console.send("Send your goal for this study session!")

                try:
                    goal = await self.bot.wait_for(
                        "message", check=lambda m: m.author == member, timeout=60
                    )
                except asyncio.TimeoutError:
                    await member.send(
                        f"{member.mention} You took too long to enter a study goal. Please try again."
                    )
                    return await member.move_to(None)
                goal = goal.content

                now = datetime.now(EST)
                renewal = now + timedelta(minutes=duration[selection_str])
                q = database.StudyVCDB.create(discordID = member.id, goal = goal, channelID = after.channel.id, StartTime = datetime.now(EST), RenewalTime = renewal)
                q.save()

                await member.send(
                    f"{member.mention} Your study goal has been updated to {goal}.\n\n**That's it!** Make sure you come back at {renewal.strftime(r'%I:%M %p')} to renew your study session!"
                )
            else:
                query = query.get()
                query.Paused = False
                query.StartTime = datetime.now(EST)
                query.save()

                if query.RenewalTime - datetime.now(EST) < timedelta(minutes=5):
                    await member.send(
                        f"{member.mention} Your study session is ending in **less than 5 minutes**. (Ends at: {query.RenewalTime.strftime(r'%I:%M %p')})\n\nMaybe renew your study session?"
                    )
                else:
                    await member.send(
                        f"{member.mention} You already have a study session going!\n\nMake sure you come back at {query.RenewalTime.strftime(r'%I:%M %p')} to renew your study session!"
                    )

            


    
def setup(bot):
    bot.add_cog(StudyVCUpdate(bot))
