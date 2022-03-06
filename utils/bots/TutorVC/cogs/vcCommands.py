import datetime
from datetime import datetime, timedelta

import discord
import pytz
from core import database
from core.checks import is_botAdmin
from core.common import TECH_ID, Emoji, MAIN_ID, STAFF_ID, TUT_ID, SandboxConfig, SelectMenuHandler
from discord.ext import commands

# global variables
time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
EST = pytz.timezone("US/Eastern")


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
    print(now_plus_10)

    return now_plus_10.strftime(r"%I:%M %p")


def showTotalMinutes(dateObj: datetime):
    now = datetime.now(EST)

    deltaTime = now - dateObj

    minutes = str(deltaTime.total_seconds() // 60)

    return minutes, now


VCGamesList = [  # TODO add emojis and descriptions to these items
    discord.SelectOption(label="Awkword"),
    discord.SelectOption(label="Betrayal"),
    discord.SelectOption(label="CG4"),
    discord.SelectOption(label="Chess in the Park"),
    discord.SelectOption(label="Doodle Crew"),
    discord.SelectOption(label="Letter Tile"),
    discord.SelectOption(label="Fishington"),
    discord.SelectOption(label="Poker Night"),
    discord.SelectOption(label="Putts"),
    discord.SelectOption(label="Sketchy Artist"),
    discord.SelectOption(label="Spell Cast"),
    discord.SelectOption(label="Youtube Together"),
    discord.SelectOption(label="Word Snacks"),
]

GameDict = {
    "Awkword": 879863881349087252,
    "Betrayal": 773336526917861400,
    "CG4": 832025144389533716,
    "Chess in the Park": 832012774040141894,
    "Doodle Crew": 878067389634314250,
    "Letter Tile": 879863686565621790,
    "Fishington": 814288819477020702,
    "Poker Night": 755827207812677713,
    "Putts": 832012854282158180,
    "Sketchy Artist": 879864070101172255,
    "Spell Cast": 852509694341283871,
    "Youtube Together": 755600276941176913,
    "Word Snacks": 879863976006127627,
}


class TutorVCCMD(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()

        self.channel_id = MAIN_ID.ch_controlPanel
        self.categoryID = [MAIN_ID.cat_privateVC, STAFF_ID.cat_privateVC, SandboxConfig.cat_sandbox]
        self.staticChannels = [MAIN_ID.ch_startPrivateVC, q.ch_tv_startvc]
        self.presetChannels = [MAIN_ID.ch_controlPanel, MAIN_ID.ch_startPrivateVC, q.ch_tv_startvc, q.ch_tv_console]

        self.ownerID = 409152798609899530
        # self.botID = bot.user.id

        self.AT = "Academics Team"
        self.SB = "Simplified Booster"
        self.Legend = "Legend"

        self.TMOD = "Mod Trainee"
        self.MOD = "Moderator"
        self.SMOD = "Senior Mod"
        self.CO = "Corporate Officer"
        self.VP = "Vice President"

        self.MAT = "Marketing Team"
        self.TT = "Technical Team"

        self.ST = "Lead Tutor"

        # Level Roles
        self.leveledRoles = [
            "〚Level 120〛Grandmaster",
            "〚Level 110〛Master",
            "〚Level 100〛Prodigy",
            "〚Level 90〛 Legend",
            "〚Level 80〛Connoisseur",
            "〚Level 70 〛Professor",
            "〚Level 60〛Mentor",
            "〚Level 50〛Scholar",
            "〚Level 40〛Expert",
            "〚Level 35〛Experienced",
            "〚Level 30〛Apprentice",
            "〚Level 25〛Amateur",
            "〚Level 20〛Student",
            "〚Level 15〛Learner",
            "〚Level 10〛Beginner",
            "〚Level 5〛Novice",
            "〚Level 1〛New",
        ]
        self.renameRoles = [
            "〚Level 120〛Grandmaster",
            "〚Level 110〛Master",
            "〚Level 100〛Prodigy",
            "〚Level 90〛 Legend",
            "〚Level 80〛Connoisseur",
            "〚Level 70 〛Professor",
            "〚Level 60〛Mentor",
            "〚Level 50〛Scholar",
            "〚Level 40〛Expert",
            "Simplified Booster",
            "Legend",
            "Moderator",
            "Marketing Team",
            "Technical Team",
        ]

        self.L120 = "〚Level 120〛Grandmaster"
        self.L110 = "〚Level 110〛Master"
        self.L100 = "〚Level 100〛Prodigy"
        self.L90 = "〚Level 90〛 Legend"
        self.L80 = "〚Level 80〛Connoisseur"
        self.L70 = "〚Level 70 〛Professor"
        self.L60 = "〚Level 60〛Mentor"
        self.L50 = "〚Level 50〛Scholar"
        self.L40 = "〚Level 40〛Expert"

        self.TutorRole = "Tutor"
        self.TutorLogID = TUT_ID.ch_hourLogs
        self.LobbyStartIDs = {
            MAIN_ID.g_main: MAIN_ID.ch_controlPanel,
            STAFF_ID.g_staff: STAFF_ID.ch_console,
            TECH_ID.g_tech: q.ch_tv_console,
        }
        self.StartVCIDs = {
            MAIN_ID.g_main: MAIN_ID.ch_startPrivateVC,
            STAFF_ID.g_staff: STAFF_ID.ch_startPrivateVC,
            TECH_ID.g_tech: q.ch_tv_startvc,
        }

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def startmusic(self, ctx: commands.Context):
        voice_state = ctx.author.voice
        if voice_state is None:
            return await ctx.send("You are not in a voice channel.")
        GameLink = str(await voice_state.channel.create_activity_invite(880218394199220334))
        await ctx.send(f"**Click the link to get started!**\n{GameLink}")

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def startgame(self, ctx: commands.Context):
        database.db.connect(reuse_if_open=True)
        voice_state = ctx.author.voice
        if voice_state is None:
            query = database.VCChannelInfo.select().where(
                (database.VCChannelInfo.authorID == ctx.author.id)
                & (database.VCChannelInfo.GuildID == ctx.guild.id)
            )
            if query.exists():
                query = (
                    database.VCChannelInfo.select()
                    .where(
                        (database.VCChannelInfo.authorID == ctx.author.id)
                        & (database.VCChannelInfo.GuildID == ctx.guild.id)
                    )
                    .get()
                )
                channel: discord.VoiceChannel = await self.bot.fetch_channel(
                    int(query.ChannelID)
                )
                view = discord.ui.View()
                var = SelectMenuHandler(
                    VCGamesList,
                    "VCGameDropdown",
                    "Click a game you want to start!",
                    select_user=ctx.author,
                )
                view.add_item(var)
                await ctx.send(
                    "Select a game from the dropdown you wish to initiate.", view=view
                )
                timeout = await view.wait()
                if not timeout:
                    SelectedGame = var.view_response
                else:
                    return await ctx.send("Timed out, try again later.")
                GameID = GameDict[SelectedGame]
                GameLink = str(await channel.create_activity_invite(GameID))
                await ctx.send("Loading...")
                await ctx.send(f"**Click the link to get started!**\n{GameLink}")

            else:
                embed = discord.Embed(
                    title=f"{Emoji.deny} Ownership Check Failed",
                    description=f"You are not the owner of this voice channel, "
                    f"please ask the original owner to start a game!",
                    color=discord.Colour.red(),
                )
                return await ctx.send(embed=embed)

        elif voice_state.channel.id in self.presetChannels:
            embed = discord.Embed(
                title=f"{Emoji.invalidchannel} UnAuthorized Channel Deletion",
                description="You are not allowed to delete these channels!"
                "\n\n**Error Detection:**"
                "\n**1)** Detected Static Channels",
                color=discord.Colour.dark_red(),
            )
            return await ctx.send(embed=embed)

        elif voice_state.channel.category_id in self.categoryID:
            query = database.VCChannelInfo.select().where(
                (database.VCChannelInfo.authorID == ctx.author.id)
                & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                & (database.VCChannelInfo.GuildID == ctx.guild.id)
            )

            if query.exists():
                q: database.VCChannelInfo = (
                    database.VCChannelInfo.select()
                    .where(
                        (database.VCChannelInfo.authorID == ctx.author.id)
                        & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                        & (database.VCChannelInfo.GuildID == ctx.guild.id)
                    )
                    .get()
                )
                channel: discord.VoiceChannel = await self.bot.fetch_channel(
                    q.ChannelID
                )

                view = discord.ui.View()
                var = SelectMenuHandler(
                    VCGamesList,
                    "VCGameDropdown",
                    "Click a game you want to start!",
                    select_user=ctx.author,
                )
                view.add_item(var)
                await ctx.send(
                    "Select a game from the dropdown you wish to initiate.", view=view
                )
                timeout = await view.wait()
                if not timeout:
                    SelectedGame = var.view_response
                else:
                    return await ctx.send("Timed out, try again later.")
                print(SelectedGame)
                GameID = GameDict[SelectedGame]
                GameLink = str(await channel.create_activity_invite(GameID))
                await ctx.send(f"**Click the link to get started!**\n{GameLink}")

            else:
                embed = discord.Embed(
                    title=f"{Emoji.deny} Ownership Check Failed",
                    description=f"You are not the owner of this voice channel, "
                    f"please ask the original owner to start a game!",
                    color=discord.Colour.red(),
                )
                return await ctx.send(embed=embed)
        database.db.close()

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def startyt(self, ctx: commands.Context):
        database.db.connect(reuse_if_open=True)
        voice_state = ctx.author.voice
        if voice_state is None:
            query = database.VCChannelInfo.select().where(
                (database.VCChannelInfo.authorID == ctx.author.id)
                & (database.VCChannelInfo.GuildID == ctx.guild.id)
            )
            if query.exists():
                query = (
                    database.VCChannelInfo.select()
                    .where(
                        (database.VCChannelInfo.authorID == ctx.author.id)
                        & (database.VCChannelInfo.GuildID == ctx.guild.id)
                    )
                    .get()
                )
                channel: discord.VoiceChannel = await self.bot.fetch_channel(
                    int(query.ChannelID)
                )
                GameLink = str(await channel.create_activity_invite(880218394199220334))
                await ctx.send(f"**Click the link to get started!**\n{GameLink}")

            else:
                embed = discord.Embed(
                    title=f"{Emoji.deny} Ownership Check Failed",
                    description=f"You are not the owner of this voice channel, "
                    f"please ask the original owner to start a game!",
                    color=discord.Colour.red(),
                )
                return await ctx.send(embed=embed)

        elif voice_state.channel.id in self.presetChannels:
            embed = discord.Embed(
                title=f"{Emoji.invalidchannel} UnAuthorized Channel Deletion",
                description="You are not allowed to delete these channels!"
                "\n\n**Error Detection:**"
                "\n**1)** Detected Static Channels",
                color=discord.Colour.dark_red(),
            )
            return await ctx.send(embed=embed)

        elif voice_state.channel.category_id in self.categoryID:
            query = database.VCChannelInfo.select().where(
                (database.VCChannelInfo.authorID == ctx.author.id)
                & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                & (database.VCChannelInfo.GuildID == ctx.guild.id)
            )

            if query.exists():
                q: database.VCChannelInfo = (
                    database.VCChannelInfo.select()
                    .where(
                        (database.VCChannelInfo.authorID == ctx.author.id)
                        & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                        & (database.VCChannelInfo.GuildID == ctx.guild.id)
                    )
                    .get()
                )
                channel: discord.VoiceChannel = await self.bot.fetch_channel(
                    q.ChannelID
                )

                GameLink = str(await channel.create_activity_invite(880218394199220334))
                await ctx.send(f"**Click the link to get started!**\n{GameLink}")

            else:
                embed = discord.Embed(
                    title=f"{Emoji.deny} Ownership Check Failed",
                    description=f"You are not the owner of this voice channel, "
                    f"please ask the original owner to start a game!",
                    color=discord.Colour.red(),
                )
                return await ctx.send(embed=embed)
        database.db.close()

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rename(self, ctx, *, name=None):
        database.db.connect(reuse_if_open=True)
        SB = discord.utils.get(ctx.guild.roles, name=self.SB)
        legend = discord.utils.get(ctx.guild.roles, name=self.Legend)

        MT = discord.utils.get(ctx.guild.roles, name=self.MOD)
        MAT = discord.utils.get(ctx.guild.roles, name=self.MAT)
        TT = discord.utils.get(ctx.guild.roles, name=self.TT)
        AT = discord.utils.get(ctx.guild.roles, name=self.AT)
        VP = discord.utils.get(ctx.guild.roles, name=self.VP)
        CO = discord.utils.get(ctx.guild.roles, name=self.CO)

        L120 = discord.utils.get(ctx.guild.roles, name=self.L120)
        L110 = discord.utils.get(ctx.guild.roles, name=self.L110)
        L100 = discord.utils.get(ctx.guild.roles, name=self.L100)
        L90 = discord.utils.get(ctx.guild.roles, name=self.L90)
        L80 = discord.utils.get(ctx.guild.roles, name=self.L80)
        L70 = discord.utils.get(ctx.guild.roles, name=self.L70)
        L60 = discord.utils.get(ctx.guild.roles, name=self.L60)
        L50 = discord.utils.get(ctx.guild.roles, name=self.L50)
        L40 = discord.utils.get(ctx.guild.roles, name=self.L40)

        roleList = [
            SB,
            AT,
            legend,
            MT,
            MAT,
            TT,
            VP,
            CO,
            L120,
            L110,
            L100,
            L90,
            L80,
            L70,
            L60,
            L50,
            L40,
        ]

        member = ctx.guild.get_member(ctx.author.id)

        if (
            not any(role in ctx.author.roles for role in roleList)
            and ctx.guild.id == 763119924385939498
        ):
            embed = discord.Embed(
                title=f"{Emoji.deny} Insufficient Rank",
                description="Sorry! But only the following people who have these roles can rename their channel!"
                "\n\n- **Moderators**"
                "\n- **Marketing Team**"
                "\n- **Technical Team**"
                "\n- **Academics Team**"
                "\n- **VP**\n- **CO**"
                "\n- **Legends**"
                "\n- **Simplified Boosters**"
                "\n- **Level 40+**",
                color=discord.Colour.blurple(),
            )
            return await ctx.send(embed=embed)

        voice_state = member.voice

        if voice_state is None:
            await ctx.send(
                f"{Emoji.deny} You need to be in a voice channel you own to use this!"
            )

        else:
            if member.voice.channel.category_id in self.categoryID:
                query = database.VCChannelInfo.select().where(
                    (database.VCChannelInfo.authorID == ctx.author.id)
                    & (database.VCChannelInfo.GuildID == ctx.guild.id)
                )

                if query.exists():
                    q: database.VCChannelInfo = (
                        database.VCChannelInfo.select()
                        .where(
                            (database.VCChannelInfo.authorID == ctx.author.id)
                            & (database.VCChannelInfo.GuildID == ctx.guild.id)
                        )
                        .get()
                    )

                    if member.voice.channel.id == int(q.ChannelID):
                        if name is not None:
                            embed = discord.Embed(
                                title=f"{Emoji.cycle} ReNamed Channel",
                                description=f"I have changed the channel's name to:"
                                f"\n**{name}**",
                                color=discord.Colour.green(),
                            )

                            await member.voice.channel.edit(name=name)
                            await ctx.send(embed=embed)

                            q.name = name
                            q.save()
                        else:
                            embed = discord.Embed(
                                title=f"{Emoji.cycle} ReNamed Channel",
                                description=f"I have changed the channel's name to:"
                                f"\n**{name}**",
                                color=discord.Colour.green(),
                            )

                            await member.voice.channel.edit(
                                name=f"{member.display_name}'s Channel"
                            )
                            await ctx.send(embed=embed)
                            q.name = f"{member.display_name}'s Channel"
                            q.save()

                    else:
                        embed = discord.Embed(
                            title=f"{Emoji.deny} Ownership Check Failed",
                            description=f"You are not the owner of this voice channel, "
                            f"please ask the original owner <@{q.authorID}>, to rename it!",
                            color=discord.Colour.red(),
                        )

                        await ctx.send(embed=embed)

                else:
                    q = database.VCChannelInfo.select().where(
                        (database.VCChannelInfo.ChannelID == member.voice.channel.id)
                        & (database.VCChannelInfo.GuildID == ctx.guild.id)
                    )
                    embed = discord.Embed(
                        title=f"{Emoji.deny} Ownership Check Failed",
                        description=f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, "
                        f"to rename it!",
                        color=discord.Colour.dark_red(),
                    )

                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"{Emoji.invalidchannel} Unknown Channel",
                    description="You are not the owner of this voice channel nor is this a "
                    "valid channel. Please execute the command under a channel you own!",
                    color=discord.Colour.red(),
                )

                await ctx.send(embed=embed)
        database.db.close()

    @commands.command()
    async def end(self, ctx):
        database.db.connect(reuse_if_open=True)
        team = discord.utils.get(ctx.guild.roles, name=self.AT)
        member = ctx.guild.get_member(ctx.author.id)
        timestamp2 = datetime.now(EST)

        voice_state = member.voice
        if voice_state is None:

            query = database.VCChannelInfo.select().where(
                (database.VCChannelInfo.authorID == ctx.author.id)
                & (database.VCChannelInfo.GuildID == ctx.guild.id)
            )
            if query.exists():
                query = (
                    database.VCChannelInfo.select()
                    .where(
                        (database.VCChannelInfo.authorID == ctx.author.id)
                        & (database.VCChannelInfo.GuildID == ctx.guild.id)
                    )
                    .get()
                )
                print(f"T: {query.TutorBotSessionID}")
                VCDatetime = pytz.timezone("America/New_York").localize(
                    query.datetimeObj
                )

                day, now = showTotalMinutes(VCDatetime)
                daySTR = int(VCDatetime.timestamp())
                nowSTR = int(now.timestamp())
                day = str(day)

                channel = await self.bot.fetch_channel(int(query.ChannelID))

                embed = discord.Embed(
                    title=f"{Emoji.archive} Ended Session",
                    description="I have successfully ended the session!",
                    color=discord.Colour.blue(),
                )
                embed.add_field(
                    name="Time Spent",
                    value=f"{member.mention} you have spent a total of {Emoji.calender} "
                    f"`{day} minutes` in voice channel, **{query.name}**.",
                )
                embed.set_footer(text="WARNING: Time displayed may not be accurate.")
                await ctx.send(embed=embed)

                print(query.TutorBotSessionID)
                tutorSession = database.TutorBot_Sessions.select().where(
                    database.TutorBot_Sessions.SessionID == query.TutorBotSessionID
                )

                query.delete_instance()

                if tutorSession.exists():
                    tutorSession = tutorSession.get()

                    student = await self.bot.fetch_user(tutorSession.StudentID)
                    tutor = await self.bot.fetch_user(tutorSession.TutorID)

                    HOURCH = await self.bot.fetch_channel(self.TutorLogID)

                    hourlog = discord.Embed(
                        title="Hour Log",
                        description=f"{tutor.mention}'s Tutor Log",
                        color=discord.Colour.blue(),
                    )
                    hourlog.add_field(
                        name="Information",
                        value=f"**Tutor:** {tutor.mention}"
                        f"\n**Student:** {student.mention}"
                        f"\n**Time Started:** <t:{daySTR}:t>"
                        f"\n**Time Ended:** <t:{nowSTR}:t>"
                        f"\n\n**Total Time:** {day}",
                    )
                    hourlog.set_footer(text=f"Session ID: {tutorSession.SessionID}")
                    await HOURCH.send(embed=hourlog)

                    embed = discord.Embed(
                        title="Feedback!",
                        description="Hey it looks like you're tutor session just ended, "
                        "if you'd like to let us know how we did please fill out the form "
                        "below!\n\nhttps://forms.gle/Y1oobNFEBf7vpfMM8",
                        color=discord.Colour.green(),
                    )
                    await student.send(embed=embed)

                await channel.delete()
                return

            else:
                return print("Ignore VC Leave")

        if voice_state.channel.id in self.presetChannels:
            embed = discord.Embed(
                title=f"{Emoji.invalidchannel} UnAuthorized Channel Deletion",
                description="You are not allowed to delete these channels!"
                "\n\n**Error Detection:**"
                "\n**1)** Detected Static Channels",
                color=discord.Colour.dark_red(),
            )
            return await ctx.send(embed=embed)

        if member.voice.channel.category_id in self.categoryID:
            query = database.VCChannelInfo.select().where(
                (database.VCChannelInfo.authorID == ctx.author.id)
                & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                & (database.VCChannelInfo.GuildID == ctx.guild.id)
            )

            if query.exists():
                q: database.VCChannelInfo = (
                    database.VCChannelInfo.select()
                    .where(
                        (database.VCChannelInfo.authorID == ctx.author.id)
                        & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                        & (database.VCChannelInfo.GuildID == ctx.guild.id)
                    )
                    .get()
                )

                tag: database.IgnoreThis = database.IgnoreThis.create(
                    channelID=voice_state.channel.id,
                    authorID=member.id,
                    GuildID=ctx.guild.id,
                )
                tag.save()
                VCDatetime = pytz.timezone("America/New_York").localize(q.datetimeObj)

                day, now = showTotalMinutes(VCDatetime)
                daySTR = int(VCDatetime.timestamp())
                nowSTR = int(now.timestamp())
                day = str(day)

                embed = discord.Embed(
                    title=f"{Emoji.archive} Ended Session",
                    description="I have successfully ended the session!",
                    color=discord.Colour.blue(),
                )
                embed.add_field(
                    name="Time Spent",
                    value=f"{member.mention} you have spent a total of {Emoji.calender} "
                    f"`{day} minutes` in voice channel, **{q.name}**.",
                )
                embed.set_footer(text="WARNING: Time displayed may not be accurate.")
                await ctx.send(embed=embed)

                print(q.TutorBotSessionID)
                tutorSession = database.TutorBot_Sessions.select().where(
                    database.TutorBot_Sessions.SessionID == q.TutorBotSessionID
                )
                if tutorSession.exists():
                    tutorSession = tutorSession.get()

                    student = await self.bot.fetch_user(tutorSession.StudentID)
                    tutor = await self.bot.fetch_user(tutorSession.TutorID)

                    HOURCH = await self.bot.fetch_channel(self.TutorLogID)

                    hourlog = discord.Embed(
                        title="Hour Log",
                        description=f"{tutor.mention}'s Tutor Log",
                        color=discord.Colour.blue(),
                    )
                    hourlog.add_field(
                        name="Information",
                        value=f"**Tutor:** {tutor.mention}"
                        f"\n**Student:** {student.mention}"
                        f"\n**Time Started:** <t:{daySTR}:t>"
                        f"\n**Time Ended:** <t:{nowSTR}:t>"
                        f"\n\n**Total Time:** {day} minutes",
                    )
                    hourlog.set_footer(text=f"Session ID: {tutorSession.SessionID}")
                    await HOURCH.send(embed=hourlog)

                    embed = discord.Embed(
                        title="Feedback!",
                        description="Hey it looks like you're tutor session "
                        "just ended, if you'd like to let us know how we did please fill out the form below!"
                        "\n\nhttps://forms.gle/Y1oobNFEBf7vpfMM8",
                        color=discord.Colour.green(),
                    )
                    try:
                        await student.send(embed=embed)
                    except discord.HTTPException:
                        pass

                    embed = discord.Embed(
                        title="Logged Hours",
                        description="Hey! It looks like you've finished your tutor session, "
                        f"I've already went ahead and sent your session legnth in <#{TUT_ID.ch_hourLogs}>."
                        "\n**NOTE:** You'll still need to fill in your hours on the hour log spreadsheet.",
                        color=discord.Color.green(),
                    )
                    try:
                        await tutor.send(embed=embed)
                    except discord.HTTPException:
                        pass

                q.delete_instance()
                await voice_state.channel.delete()

            else:
                try:
                    q = (
                        database.VCChannelInfo.select()
                        .where(
                            (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                            & (database.VCChannelInfo.GuildID == ctx.guild.id)
                        )
                        .get()
                    )
                except:
                    embed = discord.Embed(
                        title=f"{Emoji.invalidchannel} Ownership Check Failed",
                        description="This isn't a valid channel! Please use the command on an actual "
                        "voice channel thats inside the correct category!",
                        color=discord.Colour.red(),
                    )
                else:
                    embed = discord.Embed(
                        title=f"{Emoji.deny} Ownership Check Failed",
                        description=f"You are not the owner of this voice channel, please ask the "
                        f"original owner <@{q.authorID}>, to end it!",
                        color=discord.Colour.red(),
                    )
                finally:
                    await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"{Emoji.invalidchannel} Unknown Channel",
                description="You are not the owner of this voice channel nor is this a valid channel. "
                "Please execute the command under a channel you own!",
                color=discord.Colour.red(),
            )

            await ctx.send(embed=embed)
        database.db.close()

    @commands.command()
    @commands.has_any_role(
        "Moderator", "Secret Service", "Head Moderator", "Mod Trainee", "!"
    )
    async def forceend(self, ctx, channel):
        database.db.connect(reuse_if_open=True)
        channel = await self.bot.fetch_channel(channel)
        print(channel)

        if channel.id in self.presetChannels:
            embed = discord.Embed(
                title=f"{Emoji.invalidchannel} UnAuthorized Channel Deletion",
                description="You are not allowed to delete these channels!"
                "\n\n**Error Detection:**"
                "\n**1)** Detected Static Channels",
                color=discord.Colour.dark_red(),
            )
            return await ctx.send(embed=embed)

        if channel.category_id in self.categoryID:
            query = database.VCChannelInfo.select().where(
                (database.VCChannelInfo.ChannelID == channel.id)
                & (database.VCChannelInfo.GuildID == ctx.guild.id)
            )

            if query.exists():
                q: database.VCChannelInfo = (
                    database.VCChannelInfo.select()
                    .where(
                        (database.VCChannelInfo.ChannelID == channel.id)
                        & (database.VCChannelInfo.GuildID == ctx.guild.id)
                    )
                    .get()
                )
                VCDatetime = pytz.timezone("America/New_York").localize(q.datetimeObj)

                day, now = showTotalMinutes(VCDatetime)

                for VCMember in channel.members:
                    if VCMember.id == q.authorID:
                        tag: database.IgnoreThis = database.IgnoreThis.create(
                            channelID=channel.id,
                            authorID=VCMember.id,
                            GuildID=ctx.guild.id,
                        )
                        tag.save()

                await channel.delete()
                q.delete_instance()
                embed = discord.Embed(
                    title=f"{Emoji.archive} Force Ended Session",
                    description="Session has been forcefully removed.",
                    color=discord.Colour.blue(),
                )
                embed.add_field(
                    name="Time Spent",
                    value=f"<@{q.authorID}> you have spent a total of {Emoji.calender} "
                    f"`{day} minutes` in voice channel, **{q.name}**.",
                )
                embed.set_footer(text="WARNING: Time displayed may not be accurate.")
                await ctx.send(embed=embed)

            else:
                await channel.delete()
                embed = discord.Embed(
                    title=f"{Emoji.warn} Partial Completion",
                    description="The database indicates there is no owner or data related to this "
                    "voice channel but I have still deleted the channel!",
                    color=discord.Colour.gold(),
                )

                await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title=f"{Emoji.warn} Unknown Channel",
                description="You are not the owner of this voice channel nor is this a valid channel. "
                "Please execute the command under a valid voice channel!",
                color=discord.Colour.red(),
            )
            await ctx.send(embed=embed)

        database.db.close()

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def lock(self, ctx):
        database.db.connect(reuse_if_open=True)
        member = ctx.guild.get_member(ctx.author.id)

        BOT = ctx.guild.get_member(self.bot.user.id)
        OWNER = ctx.guild.get_member(self.ownerID)
        TMOD = discord.utils.get(ctx.guild.roles, name=self.TMOD)
        MOD = discord.utils.get(ctx.guild.roles, name=self.MOD)
        SMOD = discord.utils.get(ctx.guild.roles, name=self.SMOD)
        CO = discord.utils.get(ctx.guild.roles, name=self.CO)
        VP = discord.utils.get(ctx.guild.roles, name=self.VP)
        ST = discord.utils.get(ctx.guild.roles, name=self.ST)

        SE = discord.utils.get(ctx.guild.roles, name="Senior Executive")
        BM = discord.utils.get(ctx.guild.roles, name="Board Member")
        E = discord.utils.get(ctx.guild.roles, name="Executive")
        roles = [BM, SE, E, OWNER]

        voice_state = member.voice

        if voice_state is None:
            embed = discord.Embed(
                title=f"{Emoji.warn} Unknown Voice Channel",
                description="You have to be in a voice channel you own in order to use this!",
                color=discord.Colour.dark_red(),
            )
            return await ctx.send(embed=embed)

        else:
            if voice_state.channel.id in self.presetChannels:
                embed = discord.Embed(
                    title=f"{Emoji.deny} UnAuthorized Channel Modification",
                    description="You are not allowed to modify these channels!"
                    "\n\n**Error Detection:**"
                    "\n**1)** Detected Static Channels",
                    color=discord.Colour.dark_red(),
                )
                return await ctx.send(embed=embed)

            if member.voice.channel.category_id in self.categoryID:
                query = database.VCChannelInfo.select().where(
                    (database.VCChannelInfo.authorID == ctx.author.id)
                    & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                    & (database.VCChannelInfo.GuildID == ctx.guild.id)
                )

                if query.exists():
                    LOCK: database.VCChannelInfo = (
                        database.VCChannelInfo.select()
                        .where(
                            (database.VCChannelInfo.authorID == ctx.author.id)
                            & (
                                database.VCChannelInfo.ChannelID
                                == voice_state.channel.id
                            )
                            & (database.VCChannelInfo.GuildID == ctx.guild.id)
                        )
                        .get()
                    )
                    LOCK.lockStatus = "1"
                    LOCK.save()

                    await member.voice.channel.set_permissions(
                        ctx.guild.default_role, connect=False, view_channel=False
                    )
                    for role in roles:
                        if role is not None:
                            await member.voice.channel.set_permissions(
                                role,
                                connect=True,
                                manage_channels=True,
                                manage_permissions=True,
                                view_channel=True,
                            )

                    embed = discord.Embed(
                        title=f"{Emoji.lock} Locked Voice Channel",
                        description="Your voice channel has been locked and now only authorized users can join it!"
                        "\n\n**NOTE:** Moderators and other Administrators will always be allowed into your voice channels!",
                        color=discord.Colour.green(),
                    )
                    await ctx.send(embed=embed)

                else:
                    try:
                        q = (
                            database.VCChannelInfo.select()
                            .where(
                                (
                                    database.VCChannelInfo.ChannelID
                                    == voice_state.channel.id
                                )
                                & (database.VCChannelInfo.GuildID == ctx.guild.id)
                            )
                            .get()
                        )
                    except:
                        embed = discord.Embed(
                            title=f"{Emoji.deny} Ownership Check Failed",
                            description="This isn't a valid voice channel! "
                            "Please use the command on an actual voice channel thats under the correct category!",
                            color=discord.Colour.red(),
                        )
                    else:
                        embed = discord.Embed(
                            title=f"{Emoji.deny} Ownership Check Failed",
                            description=f"You are not the owner of this voice channel, "
                            f"please ask the original owner <@{q.authorID}>, to use this command!",
                            color=discord.Colour.red(),
                        )
                    finally:
                        await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"{Emoji.warn} Unknown Channel",
                    description="You are not the owner of this voice channel nor is this a valid channel. "
                    "Please execute the command under a channel you own!",
                    color=discord.Colour.red(),
                )

                await ctx.send(embed=embed)

        database.db.close()

    @commands.command()
    async def settutor(self, ctx, tutorcode):
        TR = discord.utils.get(ctx.guild.roles, name=self.TutorRole)

        if TR not in ctx.author.roles or ctx.guild.id == STAFF_ID.g_staff:
            return await ctx.message.add_reaction("❌")

        else:
            member = ctx.guild.get_member(ctx.author.id)
            voice_state = member.voice

            if voice_state is None:
                embed = discord.Embed(
                    title=f"{Emoji.warn} Unknown Voice Channel",
                    description="You have to be in a voice channel you own in order to use this!",
                    color=discord.Colour.dark_red(),
                )
                return await ctx.send(embed=embed)

            tutorSession = database.TutorBot_Sessions.select().where(
                database.TutorBot_Sessions.SessionID == tutorcode
            )
            if tutorSession.exists():
                tutorSession = tutorSession.get()
                if member.voice.channel.category_id in self.categoryID:

                    query = database.VCChannelInfo.select().where(
                        (database.VCChannelInfo.authorID == ctx.author.id)
                        & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                        & (database.VCChannelInfo.GuildID == ctx.guild.id)
                    )
                    if query.exists():
                        query = query.get()
                        student = await self.bot.fetch_user(tutorSession.StudentID)
                        tutor = await self.bot.fetch_user(tutorSession.TutorID)
                        ts = int(tutorSession.Date.timestamp())

                        query.TutorBotSessionID = tutorcode
                        query.save()

                        hourlog = discord.Embed(
                            title="Tutor Session Convert Complete",
                            description=f"I have successfully converted this voice session into a tutor session, "
                            f"when you end this session I will log this session for you.",
                            color=discord.Colour.blue(),
                        )
                        hourlog.add_field(
                            name="Information",
                            value=f"**Tutor:** {tutor.mention}"
                            f"\n**Student:** {student.mention}"
                            f"\n**Date:** <t:{ts}:R>",
                        )
                        await ctx.send(embed=hourlog)

                    else:
                        embed = discord.Embed(
                            title=f"{Emoji.warn} Unknown Voice Channel",
                            description="You have to be in a voice channel you own in order to use this!",
                            color=discord.Colour.dark_red(),
                        )
                        return await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title=f"{Emoji.warn} Unknown Voice Channel",
                        description="You have to be in a voice channel you own in order to use this!",
                        color=discord.Colour.dark_red(),
                    )
                    return await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Invalid Session",
                    description="This session does not exist, please check the ID you've provided!",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def unlock(self, ctx):
        database.db.connect(reuse_if_open=True)
        member = ctx.guild.get_member(ctx.author.id)

        voice_state = member.voice

        if voice_state is None:
            embed = discord.Embed(
                title=f"{Emoji.warn} Unknown Voice Channel",
                description="You have to be in a voice channel you own in order to use this!",
                color=discord.Colour.dark_red(),
            )
            return await ctx.send(embed=embed)

        else:
            if voice_state.channel.id in self.presetChannels:
                embed = discord.Embed(
                    title=f"{Emoji.deny} UnAuthorized Channel Modification",
                    description="You are not allowed to modify these channels!"
                    "\n\n**Error Detection:**"
                    "\n**1)** Detected Static Channels",
                    color=discord.Colour.dark_red(),
                )
                return await ctx.send(embed=embed)

            if member.voice.channel.category_id in self.categoryID:
                query = database.VCChannelInfo.select().where(
                    (database.VCChannelInfo.authorID == ctx.author.id)
                    & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                    & (database.VCChannelInfo.GuildID == ctx.guild.id)
                )

                if query.exists():
                    LOCK: database.VCChannelInfo = (
                        database.VCChannelInfo.select()
                        .where(
                            (database.VCChannelInfo.authorID == ctx.author.id)
                            & (
                                database.VCChannelInfo.ChannelID
                                == voice_state.channel.id
                            )
                            & (database.VCChannelInfo.GuildID == ctx.guild.id)
                        )
                        .get()
                    )
                    LOCK.lockStatus = "0"
                    LOCK.save()

                    query = (
                        database.VCChannelInfo.select()
                        .where(
                            (database.VCChannelInfo.authorID == ctx.author.id)
                            & (
                                database.VCChannelInfo.ChannelID
                                == voice_state.channel.id
                            )
                            & (database.VCChannelInfo.GuildID == ctx.guild.id)
                        )
                        .get()
                    )
                    await member.voice.channel.edit(sync_permissions=True)

                    embed = discord.Embed(
                        title=f"{Emoji.unlock} Unlocked Voice Channel",
                        description="Your voice channel has been unlocked and now anyone can join it!",
                        color=discord.Colour.green(),
                    )
                    await ctx.send(embed=embed)

                else:
                    try:
                        q = (
                            database.VCChannelInfo.select()
                            .where(
                                (
                                    database.VCChannelInfo.ChannelID
                                    == voice_state.channel.id
                                )
                                & (database.VCChannelInfo.GuildID == ctx.guild.id)
                            )
                            .get()
                        )
                    except:
                        embed = discord.Embed(
                            title=f"{Emoji.deny} Ownership Check Failed",
                            description="This isn't a valid voice channel! Please use the command on "
                            "an actual voice channel thats under the correct category!",
                            color=discord.Colour.red(),
                        )
                    else:
                        embed = discord.Embed(
                            title=f"{Emoji.deny} Ownership Check Failed",
                            description=f"You are not the owner of this voice channel, "
                            f"please ask the original owner <@{q.authorID}>, to unlock it!",
                            color=discord.Colour.red(),
                        )
                    finally:
                        await ctx.send(embed=embed)

            else:
                embed = discord.Embed(
                    title=f"{Emoji.warn} Unknown Channel",
                    description="You are not the owner of this voice channel nor is this a valid channel. "
                    "Please execute the command under a channel you own!",
                    color=discord.Colour.red(),
                )

                await ctx.send(embed=embed)

        database.db.close()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def permit(self, ctx, typeAction, user: discord.Member = None):
        database.db.connect(reuse_if_open=True)
        member = ctx.guild.get_member(ctx.author.id)

        voice_state = member.voice

        if voice_state is None:
            embed = discord.Embed(
                title=f"{Emoji.warn} Unknown Voice Channel",
                description="You have to be in a voice channel you own in order to use this!",
                color=discord.Colour.dark_red(),
            )
            return await ctx.send(embed=embed)

        else:
            if voice_state.channel.id in self.presetChannels:
                embed = discord.Embed(
                    title=f"{Emoji.deny} UnAuthorized Channel Modification",
                    description="You are not allowed to modify these channels!"
                    "\n\n**Error Detection:**"
                    "\n**1)** Detected Static Channels",
                    color=discord.Colour.dark_red(),
                )
                return await ctx.send(embed=embed)

            if member.voice.channel.category_id in self.categoryID:
                query = database.VCChannelInfo.select().where(
                    (database.VCChannelInfo.authorID == ctx.author.id)
                    & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                    & (database.VCChannelInfo.GuildID == ctx.guild.id)
                )

                if query.exists():
                    query = (
                        database.VCChannelInfo.select()
                        .where(
                            (database.VCChannelInfo.authorID == ctx.author.id)
                            & (
                                database.VCChannelInfo.ChannelID
                                == voice_state.channel.id
                            )
                            & (database.VCChannelInfo.GuildID == ctx.guild.id)
                        )
                        .get()
                    )

                    if query.lockStatus == "0":
                        embed = discord.Embed(
                            title=f"{Emoji.deny} Invalid Setup",
                            description="Hey there! This voice channel is already open to the public, "
                            "if you want to limit its access to certain people. "
                            "Then consider using `+lock` and then come back this command!",
                            color=discord.Colour.blurple(),
                        )
                        return await ctx.send(embed=embed)

                    else:
                        if typeAction == "+" or typeAction.lower() == "add":
                            if user is None:
                                return await ctx.send(
                                    f"{Emoji.deny} Invalid User Provided..."
                                )
                            await member.voice.channel.set_permissions(
                                user, connect=True, view_channel=True
                            )
                            embed = discord.Embed(
                                title=f"{Emoji.addgear} Permit Setup",
                                description=f"{user.mention} now has access to this channel!",
                                color=discord.Colour.blurple(),
                            )
                            return await ctx.send(embed=embed)

                        elif typeAction == "-" or typeAction.lower() == "remove":
                            if user is None:
                                return await ctx.send(
                                    f"{Emoji.deny} Invalid User Provided..."
                                )

                            if user.id == int(query.authorID):
                                return await ctx.send(
                                    f"{Emoji.deny} You can't modify your own access!"
                                )

                            await member.voice.channel.set_permissions(
                                user, overwrite=None
                            )
                            embed = discord.Embed(
                                title=f"{Emoji.minusgear} Permit Setup",
                                description=f"{user.mention}'s access has been removed from this channel!",
                                color=discord.Colour.blurple(),
                            )
                            return await ctx.send(embed=embed)

                        elif typeAction == "=" or typeAction.lower() == "list":
                            ch = member.voice.channel
                            randomlist = []
                            for x in ch.overwrites:
                                if isinstance(x, discord.Member):
                                    randomlist.append(x.display_name)

                            formatVer = "\n".join(randomlist)

                            embed = discord.Embed(
                                title=f"{Emoji.cycle} Permit List",
                                description=f"**Users Authorized:**" f"\n\n{formatVer}",
                                color=discord.Color.gold(),
                            )
                            await ctx.send(embed=embed)

                        else:
                            embed = discord.Embed(
                                title=f"{Emoji.warn} Invalid Operation",
                                description="Supported operations: `+`/add, `-`/remove, `=`/list",
                                color=discord.Color.dark_gold(),
                            )
                            embed.add_field(
                                name="Documentation",
                                value="Hey there, it looks you didn't specify a valid operation type to this user. "
                                "Take a look at this documentation!"
                                "\n\n**PERMIT:**"
                                "\n\nUsage: `+permit <operation> <user>`"
                                "\n**Description:** Modifies your voice channel's permissions."
                                "\n**NOTE:** The argument `operation` supports `+`/add, `-`/remove, `=`/list. "
                                "If you are using `=` or `list`, you do not need to specify a user."
                                "\n\n**Examples:**"
                                "\n\nAdding Members -> `+permit add @Space#0001`"
                                "\nRemoving Members -> `+permit remove @Space#0001`"
                                "\nListing Members -> `+permit =`",
                            )
                            return await ctx.send(embed=embed)

                else:
                    try:
                        q = (
                            database.VCChannelInfo.select()
                            .where(
                                (
                                    database.VCChannelInfo.ChannelID
                                    == voice_state.channel.id
                                )
                                & (database.VCChannelInfo.GuildID == ctx.guild.id)
                            )
                            .get()
                        )
                    except:
                        embed = discord.Embed(
                            title=f"{Emoji.invalidchannel} Ownership Check Failed",
                            description="This isn't a valid channel! "
                            "Please use the command on an actual private voice channel!",
                            color=discord.Colour.red(),
                        )
                    else:
                        embed = discord.Embed(
                            title=f"{Emoji.deny} Ownership Check Failed",
                            description=f"You are not the owner of this voice channel, "
                            f"please ask the original owner <@{q.authorID}>, to use this command!",
                            color=discord.Colour.red(),
                        )
                    finally:
                        await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"{Emoji.warn} Unknown Channel",
                    description="You are not the owner of this voice channel nor is this a valid channel. "
                    "Please execute the command under a channel you own!",
                    color=discord.Colour.red(),
                )

                await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def voicelimit(self, ctx, new_voice_limit):
        member = ctx.guild.get_member(ctx.author.id)

        MT = discord.utils.get(ctx.guild.roles, name=self.MOD)
        MAT = discord.utils.get(ctx.guild.roles, name=self.MAT)
        TT = discord.utils.get(ctx.guild.roles, name=self.TT)
        AT = discord.utils.get(ctx.guild.roles, name=self.AT)
        VP = discord.utils.get(ctx.guild.roles, name=self.VP)
        CO = discord.utils.get(ctx.guild.roles, name=self.CO)

        roleList = [MT, MAT, TT, AT, VP, CO]

        voice_state = member.voice

        if voice_state is None:
            embed = discord.Embed(
                title=f"{Emoji.invalidchannel} Unknown Voice Channel",
                description="You have to be in a voice channel you own in order to use this!",
                color=discord.Colour.dark_red(),
            )
            return await ctx.send(embed=embed)

        else:
            if voice_state.channel.id in self.presetChannels:
                embed = discord.Embed(
                    title=f"{Emoji.deny} UnAuthorized Channel Modification",
                    description="You are not allowed to modify these channels!"
                    "\n\n**Error Detection:**"
                    "\n**1)** Detected Static Channels",
                    color=discord.Colour.dark_red(),
                )
                return await ctx.send(embed=embed)

            if member.voice.channel.category_id in self.categoryID:
                query = database.VCChannelInfo.select().where(
                    (database.VCChannelInfo.authorID == ctx.author.id)
                    & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                    & (database.VCChannelInfo.GuildID == ctx.guild.id)
                )

                if query.exists():
                    try:
                        voiceLIMIT = int(new_voice_limit)
                    except:
                        return await ctx.send(f"{Emoji.deny} Not a valid number!")
                    else:
                        if voiceLIMIT == 0:
                            return await ctx.send(
                                f"{Emoji.warn} Sorry, you can't set your voice channel to `0`!"
                            )

                        if voiceLIMIT < 0:
                            return await ctx.send(
                                f"{Emoji.warn} Sorry, you can't set your voice channel to something below `-1`!"
                            )

                        if not any(role in ctx.author.roles for role in roleList):
                            if voiceLIMIT > 4 and ctx.guild.id == MAIN_ID.g_main:
                                return await ctx.send(
                                    f"{Emoji.warn} You can't increase the voice limit to something bigger then 4 members!"
                                )

                            elif ctx.guild.id == STAFF_ID.g_staff:
                                await member.voice.channel.edit(user_limit=voiceLIMIT)
                                return await ctx.send(
                                    f"{Emoji.confirm} Successfully modified voice limit!"
                                )

                        else:
                            if voiceLIMIT > 10:
                                return await ctx.send(
                                    f"{Emoji.warn} You can't increase the voice limit to something bigger then 10 members!"
                                )

                            else:
                                await member.voice.channel.edit(user_limit=voiceLIMIT)
                                return await ctx.send(
                                    f"{Emoji.confirm} Successfully modified voice limit!"
                                )

                else:
                    try:
                        q = (
                            database.VCChannelInfo.select()
                            .where(
                                (
                                    database.VCChannelInfo.ChannelID
                                    == voice_state.channel.id
                                )
                                & (database.VCChannelInfo.GuildID == ctx.guild.id)
                            )
                            .get()
                        )
                    except:
                        embed = discord.Embed(
                            title=f"{Emoji.invalidchannel} Ownership Check Failed",
                            description="This isn't a voice channel! Please use the command on an actual private channel!",
                            color=discord.Colour.red(),
                        )
                    else:
                        embed = discord.Embed(
                            title=f"{Emoji.deny} Ownership Check Failed",
                            description=f"You are not the owner of this voice channel, "
                            f"please ask the original owner <@{q.authorID}>, to use this command!",
                            color=discord.Colour.red(),
                        )
                    finally:
                        await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"{Emoji.warn} Unknown Channel",
                    description="You are not the owner of this voice channel nor is this a valid channel. "
                    "Please execute the command under a channel you own!",
                    color=discord.Colour.red(),
                )

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def disconnect(self, ctx, user: discord.Member):
        database.db.connect(reuse_if_open=True)
        member = ctx.guild.get_member(ctx.author.id)

        voice_state = member.voice

        if voice_state is None:
            embed = discord.Embed(
                title=f"{Emoji.warn} Unknown Voice Channel",
                description="You have to be in a voice channel you own in order to use this!",
                color=discord.Colour.dark_red(),
            )
            return await ctx.send(embed=embed)

        else:
            if voice_state.channel.id in self.presetChannels:
                embed = discord.Embed(
                    title=f"{Emoji.deny} UnAuthorized Channel Modification",
                    description="You are not allowed to modify these channels!"
                    "\n\n**Error Detection:**"
                    "\n**1)** Detected Static Channels",
                    color=discord.Colour.dark_red(),
                )
                return await ctx.send(embed=embed)

            if member.voice.channel.category_id in self.categoryID:
                query = database.VCChannelInfo.select().where(
                    (database.VCChannelInfo.authorID == ctx.author.id)
                    & (database.VCChannelInfo.ChannelID == voice_state.channel.id)
                    & (database.VCChannelInfo.GuildID == ctx.guild.id)
                )

                if query.exists():
                    await user.move_to(None)
                    embed = discord.Embed(
                        title=f"{Emoji.minusgear} Disconnected User",
                        description=f"Disconnected {user.mention}!",
                        color=discord.Colour.green(),
                    )
                    return await ctx.send(embed=embed)

                else:
                    try:
                        q = (
                            database.VCChannelInfo.select()
                            .where(
                                (
                                    database.VCChannelInfo.ChannelID
                                    == voice_state.channel.id
                                )
                                & (database.VCChannelInfo.GuildID == ctx.guild.id)
                            )
                            .get()
                        )
                    except:
                        embed = discord.Embed(
                            title=f"{Emoji.deny} Ownership Check Failed",
                            description="This isn't a valid voice channel! "
                            "Please use the command on an actual voice channel thats under the correct category!",
                            color=discord.Colour.red(),
                        )
                    else:
                        embed = discord.Embed(
                            title=f"{Emoji.deny} Ownership Check Failed",
                            description=f"You are not the owner of this voice channel, "
                            f"please ask the original owner <@{q.authorID}>, to disconnect them!",
                            color=discord.Colour.red(),
                        )
                    finally:
                        await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f"{Emoji.warn} Unknown Channel",
                    description="You are not the owner of this voice channel nor is this a valid channel. "
                    "Please execute the command under a channel you own!",
                    color=discord.Colour.red(),
                )

                await ctx.send(embed=embed)

    @commands.command(aliases=["start"])
    async def startVC(self, ctx):
        embed = discord.Embed(
            title="Private Channels",
            description="First off, there is **no** command to start a private channel.",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Creating a Private Channel",
            value=f"The **only** way to create a voice channel is through **you** joining <#{self.StartVCIDs[ctx.guild.id]}>. "
            f"There is **no command**, so please don't spam `+start` or whatever comes up in your head.",
        )
        embed.add_field(
            name="Permissions",
            value="The voice channel owner is the only person who can run any of the modifier commands. (Rename, Permit, Disconnect, etc) "
            "\n**No**, there is no way of adding extra users to manage the voice channel. "
            "Anyone who tries will just get an error saying they'd have to redirect the command back to the original owner.",
            inline=False,
        )
        embed.add_field(
            name="Rank Requirements",
            value="In order to create a private voice channel, you need to be level 10 or above. "
            "Unfortunately, if you are not above level 10 you won't be able to join the Start Private VC channel and create one.",
            inline=False,
        )
        embed.set_footer(text="Feel free to ping Space if you have any questions.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(TutorVCCMD(bot))
