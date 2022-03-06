import asyncio
import datetime
import re
from typing import List
import random, string
import os

import discord
from discord.ext import commands
from core.checks import isnot_hostTimmyA
from core.common import hexColors as hex
from core.common import Emoji
from core.common import MAIN_ID, DIGITAL_ID, TECH_ID, MKT_ID, TUT_ID, HR_ID, LEADER_ID, STAFF_ID
from core.common import stringTimeConvert, ButtonHandler, searchCustomEmoji


class VotingBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.acceptedAnnouncementCHs = [
            MAIN_ID.ch_announcements,
            MAIN_ID.ch_modAnnouncements,
            DIGITAL_ID.ch_announcements,
            DIGITAL_ID.ch_acadAnnouncements,
            DIGITAL_ID.ch_clubAnnouncements,
            DIGITAL_ID.ch_coAnnouncements,
            DIGITAL_ID.ch_mktAnnouncements,
            DIGITAL_ID.ch_notesAnnouncements,
            DIGITAL_ID.ch_techAnnouncements,
            TECH_ID.ch_announcements,
            TECH_ID.ch_botAnnouncements,
            TECH_ID.ch_itAnnouncements,
            TECH_ID.ch_webAnnouncements,
            MKT_ID.ch_announcements,
            MKT_ID.ch_modAnnouncements,
            MKT_ID.ch_bpAnnouncements,
            MKT_ID.ch_mediaAnnouncements,
            MKT_ID.ch_designAnnouncements,
            MKT_ID.ch_eventsAnnouncements,
            TUT_ID.ch_announcements,
            TUT_ID.ch_csAnnouncements,
            TUT_ID.ch_mathAnnouncements,
            TUT_ID.ch_miscAnnouncements,
            TUT_ID.ch_englishAnnouncements,
            TUT_ID.ch_leadershipAnnouncements,
            TUT_ID.ch_scienceAnnouncements,
            TUT_ID.ch_ssAnnouncements,
            HR_ID.ch_announcements,
            HR_ID.ch_leadershipAnnouncements,
            HR_ID.ch_techAnnouncements,
            HR_ID.ch_mktAnnouncements,
            HR_ID.ch_acadAnnouncements,
            LEADER_ID.ch_mktAnnouncements,
            LEADER_ID.ch_mainAnnouncements,
            LEADER_ID.ch_envAnnouncements,
            LEADER_ID.ch_ssdAnnouncements,
            LEADER_ID.ch_workonlyAnnouncements,
            LEADER_ID.ch_financeAnnouncements,
            LEADER_ID.ch_rebrandAnnouncements,
            LEADER_ID.ch_staffAnnouncements,
            STAFF_ID.ch_announcements,
            STAFF_ID.ch_leadershipAnnouncements
        ]

    """
    vote create: creates a voting
        1. Announcement channel
        2. Text                                                                             # TODO: not longer than X symbols
        3. Options (would be buttons)
        4. Durations

        # TODO: Add message and components to db
        # TODO: Add count to components in db (NOT MEMBER DUE OF PRIVACY)
        # TODO: Catch interaction
        - Embed displays a timestamp and notes that the vote can't get undo                 # DONE
        - When someone voted, he gets a ephemeral message, that the person has voted on X  
        - If the person votes again, he gets an ephemeral message, that he already voted

    vote list: lists every voting (finished and ongoing votings)
        - Votings have an unique ID
        - Votings have a status: ongoing or expired                                            
        - Votings have expiration date or when it expired
        - Votings have user, who created the voting
        - Channel and server

    vote stats <ID>: shows stats of the voting
        - ID
        - status
        - expiration date or when it expired
        - user, who created the voting
        - channel and server
        - Text of the voting
        - Options of the voting
        - Diagram (on ongoing and on expired votings)
        
        
    vote end <ID>: Immediately ends a voting
    
    vote delete <ID>: Deletes a voting and ends the voting if ongoing
    """

    @commands.group(invoke_without_command=True)
    @commands.has_any_role(
        LEADER_ID.r_corporateOfficer,
        LEADER_ID.r_director,
        LEADER_ID.r_president,
        LEADER_ID.r_vicePresident,
        LEADER_ID.r_boardMember,
        LEADER_ID.r_informationTechnologyManager,
        LEADER_ID.r_ssDigitalCommittee
    )
    async def vote(self, ctx):
        pass

    @vote.command()
    @isnot_hostTimmyA
    async def create(self, ctx: commands.Context):

        acceptedChannelsStr = ""
        for channelID in self.acceptedAnnouncementCHs:
            acceptedChannel = self.bot.get_channel(channelID)

            acceptedChannelsStr += f"- {acceptedChannel.name} from {acceptedChannel.guild.name} ({acceptedChannel.id})\n"

        randomID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        tempVoteCHsPath = f"./TEMP_voteCHS_{randomID}.txt"
        tempVoteCHsFilename = "TEMP_voteCHS_{randomID}.txt"

        tempVoteCHsFileWrite = open(tempVoteCHsPath, "w+")
        tempVoteCHsFileWrite.write(f"Accepted channels:"
                                   f"\n{acceptedChannelsStr}")
        tempVoteCHsFileWrite.close()
        tempVoteCHsFile = discord.File(tempVoteCHsPath, filename=tempVoteCHsFilename)

        os.remove(tempVoteCHsPath)

        ch_snakePit = self.bot.get_channel(TECH_ID.ch_snakePit)
        msgVoteCHsFile = await ch_snakePit.send(file=tempVoteCHsFile)
        voteCHsFileURL = msgVoteCHsFile.attachments[0].url
        await msgVoteCHsFile.delete()
        embedServer = discord.Embed(
            color=hex.ss_blurple,
            title="Create Voting",
            description="Please provide the announcement-channel/s ID in which the voting should get sent. To send it to "
                        "multiple channels, separate the channels with commas (`,`)."
                        "\n**Click on the link below to see a list of the accepted channels.**",
        )
        embedServer.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
        embedServer.set_footer(text="Type 'cancel' to cancel | Timeout after 60s")

        viewAcceptedCHs = discord.ui.View()
        viewAcceptedCHs.add_item(
            ButtonHandler(
                style=discord.ButtonStyle.link,
                url=voteCHsFileURL,
                label="Accepted Channels"
            )
        )
        msgSetup = await ctx.send(embed=embedServer, view=viewAcceptedCHs)

        def msgInputCheck(message: discord.Message):
            return message.channel == ctx.channel and message.author == ctx.author

        channels = []
        text = ...  # type: str
        options = []
        datetimeExpiration = ...  # type: datetime.datetime

        msgError = ...  # type: discord.Message
        viewReset = discord.ui.View()

        setupFinished = False
        index = 0
        while True:
            try:
                msgResponse: discord.Message = await self.bot.wait_for(
                    "message", check=msgInputCheck, timeout=60
                )
            except asyncio.TimeoutError:
                embedTimeout = discord.Embed(
                    color=hex.red_cancel,
                    title="Create Voting",
                    description="Setup canceled due to timeout.",
                )
                embedTimeout.set_author(
                    name=f"{ctx.author}", icon_url=ctx.author.avatar.url
                )
                embedTimeout.set_footer(text="Use '+vote create' to start again")

                await msgSetup.edit(embed=embedTimeout, view=viewReset)

                try:
                    await msgError.delete()
                except:
                    pass

                break

            else:
                msgContent = msgResponse.content

                if msgContent.lower() == "cancel":
                    embedCancel = discord.Embed(
                        color=hex.red_cancel,
                        title="Create Voting",
                        description="Setup canceled."
                    )
                    embedCancel.set_author(
                        name=f"{ctx.author}", icon_url=ctx.author.avatar.url
                    )
                    embedCancel.set_footer(text="Use '+vote create' to start again")
                    await msgSetup.edit(embed=embedCancel, view=viewReset)

                    try:
                        await msgError.delete()
                    except:
                        pass

                    break

                if index == 0:
                    try:
                        await msgError.delete()
                    except:
                        pass

                    embedNotFound = discord.Embed(
                        color=hex.red_error,
                        title="Create Voting",
                        description=f"Couldn't find one or more of the given text channels. Make sure the channel exists, "
                                    f"you provide the channel's ID and it's an accepted channel."
                    )
                    embedNotFound.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                    embedNotFound.set_footer(text="Use 'cancel' to cancel")

                    tempChannels = []
                    if "," in msgContent:
                        channelsStrList = msgContent.split(",")
                        for channelStr in channelsStrList:
                            stripChannelStr = channelStr.strip()
                            channelsStrList[channelsStrList.index(channelStr)] = stripChannelStr

                            if stripChannelStr.isdigit():
                                channel = self.bot.get_channel(int(stripChannelStr))

                            else:
                                channel = None

                            tempChannels.append(channel)

                        if any(channelInList is None for channelInList in tempChannels) or \
                                any(type(channelInList) is not discord.TextChannel for channelInList in tempChannels) or \
                                any(channelInList.id not in self.acceptedAnnouncementCHs for channelInList in tempChannels):
                            msgError = await ctx.send(embed=embedNotFound)
                            try:
                                await msgError.delete(delay=7)
                            except:
                                pass

                            continue

                    else:
                        channelStr = msgContent.strip()
                        if channelStr.isdigit():
                            channel = self.bot.get_channel(int(channelStr))

                        else:
                            channel = None

                        if channel is None or type(channel) is not discord.TextChannel or channel.id not in self.acceptedAnnouncementCHs:
                            msgError = await ctx.send(embed=embedNotFound)
                            try:
                                await msgError.delete(delay=7)
                            except:
                                pass

                            continue

                        tempChannels.append(channel)

                    channels = tempChannels

                    embedText = discord.Embed(
                        color=hex.ss_blurple,
                        title="Create Voting",
                        description="Please provide the text you want to add to the voting."
                                    "\n\n**Example:**"
                                    "\nHey everyone,"
                                    "\nWhich programming language is better? Please vote now!"
                                    f"\n{Emoji.pythonLogo} Python | {Emoji.javascriptLogo} JavaScript"
                                    f"\n\n(In the example above you would choose Python of course {Emoji.blobamused})",
                    )
                    embedText.set_author(
                        name=f"{ctx.author}", icon_url=ctx.author.avatar.url
                    )
                    embedText.set_footer(
                        text="Type 'cancel' to cancel | Timeout after 60s"
                    )
                    await msgSetup.edit(embed=embedText, view=viewReset)

                    index += 1

                elif index == 1:
                    try:
                        await msgError.delete()
                    except:
                        pass

                    text = msgContent

                    embedText = discord.Embed(
                        color=hex.ss_blurple,
                        title="Create Voting",
                        description="Please provide the options for the voting by separating the options with commas (`,`). "
                                    "They will shown as buttons."
                                    f"\n\nFrom the example on the last message, the options would be: "
                                    f"{Emoji.pythonLogo} Python, {Emoji.javascriptLogo} JavaScript",
                    )
                    embedText.set_author(
                        name=f"{ctx.author}", icon_url=ctx.author.avatar.url
                    )
                    embedText.set_footer(
                        text="Type 'cancel' to cancel | Timeout after 60s"
                    )
                    await msgSetup.edit(embed=embedText)

                    index += 1

                elif index == 2:
                    try:
                        await msgError.delete()
                    except:
                        pass

                    optionsStrList = msgContent.split(",")
                    for optionStr in optionsStrList:
                        options.append(optionStr.strip())

                    embedDuration = discord.Embed(
                        color=hex.ss_blurple,
                        title="Create Voting",
                        description="Please provide the duration of the voting."
                                    "\n\n**Example:**"
                                    "\n`2d 4h 5m 50s` -> would be 2 days, 4 hours, 5m and 50 seconds."
                    )
                    embedDuration.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                    embedDuration.set_footer(text="Type 'cancel' to cancel | Timeout after 60s")
                    await msgSetup.edit(embed=embedDuration)

                    index += 1

                elif index == 3:
                    try:
                        await msgError.delete()
                    except:
                        pass

                    timeDict: dict = stringTimeConvert(msgContent)
                    days = timeDict["days"]
                    hours = timeDict["hours"]
                    minutes = timeDict["minutes"]
                    seconds = timeDict["seconds"]

                    if days is None and hours is None and minutes is None and seconds is None:
                        embedNotFound = discord.Embed(
                            color=hex.red_error,
                            title="Create Voting",
                            description="Couldn't find something matching to the time units. Please try again."
                        )
                        embedNotFound.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                        embedNotFound.set_footer(text="Use 'cancel' to cancel")
                        msgError = await ctx.send(embed=embedNotFound)
                        try:
                            await msgError.delete(delay=7)
                        except:
                            pass

                        continue

                    if days is None:
                        days = 0

                    if hours is None:
                        hours = 0

                    if minutes is None:
                        minutes = 0

                    if seconds is None:
                        seconds = 0

                    datetimeNow = datetime.datetime.now()
                    try:
                        datetimeExpiration = datetimeNow + datetime.timedelta(days=days) + datetime.timedelta(
                            hours=hours) + datetime.timedelta(minutes=minutes) + datetime.timedelta(seconds=seconds)
                    except OverflowError as _error:
                        embedOverflow = discord.Embed(
                            color=hex.red_error,
                            title="Create Voting",
                            description="Couldn't convert it to a datetime due of a too big expiration date. Please try again."
                                        f"\n\n**Error:** `{_error.__class__.__name__}: {_error}`"
                        )
                        embedOverflow.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                        embedOverflow.set_footer(text="Use 'cancel' to cancel")
                        msgError = await ctx.send(embed=embedOverflow)
                        try:
                            await msgError.delete(delay=7)
                        except:
                            pass

                        continue

                    embedFinish = discord.Embed(
                        color=hex.ss_blurple,
                        title="Create Voting",
                        description="**Almost done...** Please overview the pseudo voting below and confirm it."
                    )
                    embedFinish.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                    await ctx.send(embed=embedFinish)

                    await msgSetup.delete()

                    expLongDateTimeTP = discord.utils.format_dt(datetimeExpiration, "F")
                    expRelativeTimeTP = discord.utils.format_dt(datetimeExpiration, "R")

                    embedPseudo = discord.Embed(
                        color=hex.ss_blurple,
                        title="Voting",
                        description=f"{text}"
                                    f"\n\nExpires {expLongDateTimeTP} ({expRelativeTimeTP})"
                    )
                    embedPseudo.set_author(name="Pseudo voting embed")
                    embedPseudo.set_footer(text="Please vote anonymously below | You can't undo your vote!")

                    viewOverview = discord.ui.View()

                    for option in options:

                        customEmoji = searchCustomEmoji(option)
                        if customEmoji is not None:
                            option = option.replace(f"{customEmoji}", "")

                        viewOverview.add_item(
                            ButtonHandler(
                                style=discord.ButtonStyle.gray,
                                disabled=False,
                                label=option,
                                emoji=customEmoji
                            )
                        )

                    await ctx.send(embed=embedPseudo, view=viewOverview)

                    setupFinished = True
                    break

        if setupFinished:
            try:
                await msgError.delete()
            except:
                pass

            strChannels = ""
            for channel in channels:
                strChannels += f"\n- {channel.name} (`{channel.id}`) from {channel.guild.name}"

            embedConfirm = discord.Embed(
                color=hex.yellow,
                title="Confirm",
                description=f"Please confirm that you overviewed the voting message and that this message will be sent and ping @everyone "
                            f"in the following channel/s:"
                            f"\n{strChannels}"
            )
            embedConfirm.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
            embedConfirm.set_footer(text="Abusing this feature has severe consequences! | Timeout after 60s")
            msgConfirm = await ctx.send(embed=embedConfirm)
            await msgConfirm.add_reaction("✅")
            await msgConfirm.add_reaction("❌")

            def confirmCheck(reaction, user):
                return user.id == ctx.author.id and reaction.message.id == msgConfirm.id and \
                        str(reaction.emoji) in ["✅", "❌"]

            try:
                reactionResponse, userResponse = await self.bot.wait_for("reaction_add", check=confirmCheck, timeout=120)
            except asyncio.TimeoutError:
                embedTimeout = discord.Embed(
                    color=hex.red_error,
                    title="Confirm",
                    description="Confirmation canceled due to timeout."
                )
                embedTimeout.set_author(
                    name=f"{ctx.author}", icon_url=ctx.author.avatar.url
                )
                embedTimeout.set_footer(text="Use '+vote create' to start again")
                await msgConfirm.edit(embed=embedTimeout)
                await msgConfirm.clear_reactions()

            else:
                if str(reactionResponse.emoji) == "✅":
                    await msgConfirm.clear_reactions()

                    embedSending = discord.Embed(
                        color=hex.yellow,
                        title="Confirm",
                        description="Sending message/s..."
                    )
                    await msgConfirm.edit(embed=embedSending)

                    print("sending")        # TODO: !!

                    expLongDateTimeTP = discord.utils.format_dt(datetimeExpiration, "F")
                    expRelativeTimeTP = discord.utils.format_dt(datetimeExpiration, "R")

                    embedVoting = discord.Embed(
                        color=hex.ss_blurple,
                        title="Voting",
                        description=f"{text}"
                                    f"\n\nExpires {expLongDateTimeTP} ({expRelativeTimeTP})"
                    )
                    embedVoting.set_footer(text="Please vote anonymously below | You can't undo your vote!")

                    viewVoting = discord.ui.View()

                    for option in options:

                        customEmoji = searchCustomEmoji(option)
                        if customEmoji is not None:
                            option = option.replace(f"{customEmoji}", "")

                        viewVoting.add_item(
                            ButtonHandler(
                                style=discord.ButtonStyle.gray,
                                disabled=False,
                                label=option,
                                emoji=customEmoji
                            )
                        )

                    channelTest = self.bot.get_channel(932066545738350640)
                    try:
                        await channelTest.send(content="@ everyone", embed=embedVoting, view=viewVoting)        # TODO: everyone
                    except Exception as _error:
                        embedError = discord.Embed(
                            color=hex.red_error,
                            title="Error while sending message/s",
                            description="An unexpected error occurred! Please make sure I can send messages into the "
                                        "provided channel/s."
                                        f"\n\n**Error:** `{_error.__class__.__name__}: {_error}`"
                        )
                        embedError.set_footer(text="Canceled | Use '+vote create' to start again")
                        embedError.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                        await msgConfirm.edit(embed=embedError)
                    else:

                        embedSuccess = discord.Embed(
                            color=hex.green_confirm,
                            title="Confirm",
                            description="Successfully sent messages to following channel/s:"
                                        f"\n{strChannels}"
                        )
                        await msgConfirm.edit(embed=embedSuccess)

                elif str(reactionResponse.emoji) == "❌":
                    await msgConfirm.clear_reactions()

                    embedCancel = discord.Embed(
                        color=hex.red_cancel,
                        title="Confirm",
                        description="Confirmation canceled."
                    )
                    embedCancel.set_author(
                        name=f"{ctx.author}", icon_url=ctx.author.avatar.url
                    )
                    embedCancel.set_footer(text="Use '+vote create' to start again")
                    await msgConfirm.edit(embed=embedCancel)

def setup(bot):
    bot.add_cog(VotingBot(bot))
