import datetime
import time
from datetime import datetime
from core.common import MAIN_ID

import discord
from discord import Option, permissions, slash_command
from discord.ext import commands
from core.common import Emoji, hexColors
from discord.commands import permissions

subjects = [
    "CS",
    "English",
    "Language",
    "Math",
    "Science",
    "Social Studies",
    "Algebra",
    "Geometry",
    "Precalc",
    "Calc",
    "Statistics",
    "English",
    "Lang",
    "English",
    "Lit",
    "Research",
    "Seminar",
    "Bio",
    "Chem",
    "Physics",
    "ASL",
    "Chinese",
    "French",
    "German",
    "Italian",
    "Latin",
    "Korean",
    "Russian",
    "Spanish",
    "Econ",
    "Euro",
    "Psych US",
    "Gov US",
    "History",
    "World History",
]

add_opt = [
    {
        "name": "question",
        "description": "Question you answered.",
        "type": 3,
        "required": True,
    },
    {
        "name": "subject_answered",
        "description": "Subject the question falls under.",
        "type": 3,
        "required": True,
    },
]


class TallyCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[MAIN_ID.g_main])
    @permissions.has_any_role(833891065974226975)
    async def ticketban(
        self,
        ctx,
        member: Option(discord.User, "Enter the user you want to TicketBan"),
        reason: Option(str, "Enter the reason for the TicketBan"),
    ):
        ticketBan = discord.utils.get(ctx.guild.roles, name="NoTickets")
        helper = discord.utils.get(ctx.guild.roles, name="Lead Helper")
        manager = discord.utils.get(ctx.guild.roles, name="Academics Manager")
        moderator = discord.utils.get(ctx.guild.roles, name="Moderator")

        #  Secondary Check
        if (
            helper not in ctx.author.roles
            and manager not in ctx.author.roles
            and moderator not in ctx.author.roles
        ):
            embed = discord.Embed(
                title="Woah Woah Woah!",
                description="You can't use this command, you require Lead Helper+ to use this!",
                color=hexColors.red_error,
            )
            return await ctx.respond(embed=embed)

        if member.id == self.bot.user.id:
            embed = discord.Embed(
                title="Unable to TicketBan this User",
                description="Why are you trying to ticketban me?",
                color=hexColors.red_error,
            )
            return await ctx.respond(embed=embed)

        if member.id == ctx.author.id:
            embed = discord.Embed(
                title="Unable to TicketBan this User",
                description="Why are you trying to ticketban yourself?",
                color=hexColors.red_error,
            )
            return await ctx.respond(embed=embed)

        if ticketBan not in member.roles:
            try:
                if reason is None:
                    return await ctx.respond(
                        "Please specify a reason for this ticket ban!"
                    )

                update_reason = f"Ticket Ban requested by {ctx.author.display_name} | Reason: {reason}"
                await member.add_roles(ticketBan, reason=update_reason)
            except Exception as e:
                await ctx.respond(f"ERROR:\n{e}")
                print(e)
            else:
                embed = discord.Embed(
                    title="Ticket Banned!",
                    description=f"{Emoji.check} {member.display_name} has been ticket banned!"
                    f"\n{Emoji.space}{Emoji.arrow} **Reason:** {reason}",
                    color=hexColors.yellow_ticketBan,
                )
                await ctx.respond(embed=embed)

        else:
            try:
                if reason is None:
                    reason = "No Reason Given"

                update_reason = f"Ticket UnBan requested by {ctx.author.display_name} | Reason: {reason}"
                await member.remove_roles(ticketBan, reason=update_reason)
            except Exception as e:
                await ctx.respond(f"ERROR:\n{e}")
            else:
                embed = discord.Embed(
                    title="Ticket Unbanned!",
                    description=f"{Emoji.check} {member.display_name} has been ticket unbanned!"
                    f"\n{Emoji.space}{Emoji.arrow} **Reason:** {reason}",
                    color=hexColors.yellow_ticketBan,
                )
                await ctx.respond(embed=embed)

    @commands.command()
    @commands.has_any_role("Academics Manager", "Lead Helper")
    async def msgfind(
        self,
        ctx,
        userList: commands.Greedy[discord.Member],
        channelList: commands.Greedy[discord.TextChannel] = [],
        dayQuery: commands.Greedy[int] = [14],
    ):
        plsDoNotShowChannels = False

        tempMemberList = []
        for u in userList:
            tempMemberList.append(u.mention)

        membersFull = ",".join(tempMemberList)

        tempChannelList = []
        for c in channelList:
            tempChannelList.append(c.mention)

        channelsFull = ",".join(tempChannelList)

        embed = discord.Embed(
            title="Search Query:",
            description=f"{Emoji.person} **Requested By:** {ctx.author.mention}\n{Emoji.profile} "
            f"**Member Search:** {membersFull}\n{Emoji.reason} **Channels:** {channelsFull}"
            f"\n{Emoji.date} **Day Query:** {str(dayQuery)}",
            color=discord.Colour.red(),
        )
        embed.set_footer(text="Processing your query...")
        msg = await ctx.send(embed=embed)
        startTime = float(time.time())

        print(type(userList))
        print(type(channelList))
        amountUser = len(userList)
        amountChannel = len(channelList)
        guild = ctx.message.guild

        print(amountUser)
        print(amountChannel)

        if channelList == []:
            for channel in guild.text_channels:
                channelList.append(channel)

            plsDoNotShowChannels = True

        dayQuery = int(dayQuery[0])
        yesterday = datetime.datetime.now() - datetime.timedelta(days=dayQuery)

        for user in userList:
            counter = 0
            try:
                for channel in channelList:
                    async for message in channel.history(limit=None, after=yesterday):
                        if message.author == user:
                            counter += 1
                        else:
                            pass

            except Exception as e:
                await ctx.send(f"ERROR: \n{e}")

            current_time = float(time.time())
            difference = int(round(current_time - startTime))
            text = str(datetime.timedelta(seconds=difference))

            listOfChannel = []
            for channel in channelList:
                listOfChannel.append(channel.mention)

            listStuff = ", ".join(listOfChannel)
            if plsDoNotShowChannels is True:
                listStuff = (
                    "\n**Too much stuff to display!**\n*Searched in all channels.*"
                )

            embed = discord.Embed(
                title="Fetching Search Query",
                description="Here are your results!",
                color=hexColors.orange,
            )

            embed.add_field(
                name="Results",
                value=f"{Emoji.person} **Requested By:** {ctx.author.mention}"
                f"\n{Emoji.profile} **Member Search:** {membersFull}"
                f"\n{Emoji.reason} **Channels:** {channelsFull}"
                f"\n{Emoji.date} **Day Query:** {str(dayQuery)}"
                f"\n{Emoji.ban} **Messages Sent:** `{str(counter)}`",
            )
            embed.set_footer(text=f"Query Time Legnth: {text} (HH:MM:SS)")

            await msg.edit(embed=embed)

    @commands.command()
    @commands.has_any_role("Academics Manager", "Lead Helper")
    async def quota(
        self,
        ctx,
        userList: commands.Greedy[discord.Member],
        channelList: commands.Greedy[discord.TextChannel] = [],
        messageQuery: commands.Greedy[int] = [30],
    ):
        tempMemberList = []
        for u in userList:
            tempMemberList.append(u.mention)

        membersFull = ",".join(tempMemberList)

        tempChannelList = []
        for c in channelList:
            tempChannelList.append(c.mention)

        channelsFull = ",".join(tempChannelList)

        embed = discord.Embed(
            title="Search Query:",
            description=f"{Emoji.person} **Requested By:** {ctx.author.mention}"
            f"\n{Emoji.profile} **Member Search:** {membersFull}"
            f"\n{Emoji.reason} **Channels:** {channelsFull}"
            f"\n{Emoji.date} **Message Filter:** {str(messageQuery)}",
            color=discord.Colour.red(),
        )
        embed.set_footer(text="Processing your query...")
        msg = await ctx.send(embed=embed)
        startTime = float(time.time())

        print(type(userList))
        print(type(channelList))
        amountUser = len(userList)
        amountChannel = len(channelList)
        guild = ctx.message.guild

        print(amountUser)
        print(amountChannel)

        userCopyList = []

        for userCopy in userList:
            userCopyList.append(userCopy.mention)

        if channelList == []:
            for channel in guild.text_channels:
                channelList.append(channel)

        messageQuery = int(messageQuery[0])
        print(messageQuery)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=5)
        listUserCompleted = []

        async def your_command():
            for user in userList:
                counter = 0
                for channel in channelList:
                    stop, counter = await process_channel(counter, channel, user)
                    if stop:
                        break

        async def process_channel(counter, channel, user):
            async for message in channel.history(limit=None, after=yesterday):
                if message.author == user:
                    counter += 1
                    if counter == messageQuery:
                        listUserCompleted.append(message.author.mention)
                        return True, counter
            return False, counter

        await your_command()

        listUserCompleted = ", ".join(listUserCompleted)

        current_time = float(time.time())
        difference = int(round(current_time - startTime))
        text = str(datetime.timedelta(seconds=difference))

        channelList2 = []
        for channel in channelList:
            channelList2.append(channel.mention)
        channelList2 = ", ".join(channelList2)

        userList2 = []
        for user in userList:
            userList2.append(user.mention)

        userList2 = ", ".join(userList2)

        peopleNoQuota = []
        for noQuota in userCopyList:
            if noQuota not in listUserCompleted:
                peopleNoQuota.append(noQuota)
        peopleNoQuota = ", ".join(peopleNoQuota)

        print(peopleNoQuota)

        embed = discord.Embed(
            title="Fetching Search Query",
            description="Here are your results!",
            color=hexColors.orange,
        )
        embed.add_field(
            name="Query Information",
            value=f"{Emoji.person} **Requested By:** {ctx.author.mention}"
            f"\n{Emoji.profile} **Member Search:** {membersFull}"
            f"\n{Emoji.reason} **Channels:** {channelsFull}"
            f"\n{Emoji.date} **Message Filter:** {str(messageQuery)}",
        )
        embed.add_field(
            name="Quota Completed",
            value=f"{Emoji.check} **Completed List:**"
            f"\n{Emoji.space}{Emoji.arrow} {listUserCompleted}",
        )
        embed.add_field(
            name="Quota UnCompleted",
            value=f"{Emoji.cancel} **UnCompleted List:**"
            f"\n{Emoji.space}{Emoji.arrow} {peopleNoQuota}",
            inline=False,
        )
        embed.set_footer(text=f"Query Time Legnth: {text} (HH:MM:SS)")
        await msg.edit(embed=embed)


def setup(bot):
    bot.add_cog(TallyCMD(bot))
