import asyncio
import io
import typing
from datetime import datetime, timedelta

import chat_exporter
import discord
import pytz
from core import database
from core.common import (ACAD_ID, HR_ID, MAIN_ID, MKT_ID, TECH_ID,
                         ButtonHandler, Emoji, Others, SelectMenuHandler)
from discord.ext import commands, tasks

MasterSubjectOptions = [
    discord.SelectOption(
        label="Math Helpers",
        description="If you need help with Math, click here!",
        emoji="✖️",
    ),
    discord.SelectOption(
        label="Science Helpers",
        description="If you need help with Science, click here!",
        emoji="🧪",
    ),
    discord.SelectOption(
        label="Social Studies Helpers",
        description="If you need help with Social Studies, click here!",
        emoji="📙",
    ),
    discord.SelectOption(
        label="English Helpers",
        description="If you need help with English, click here!",
        emoji="📖",
    ),
    discord.SelectOption(
        label="Essay Helpers",
        description="If you need help with an Essay, click here!",
        emoji="✍️",
    ),
    discord.SelectOption(
        label="Language Helpers",
        description="If you need help with a Language, click here!",
        emoji="🗣",
    ),
    discord.SelectOption(
        label="Computer Science Helpers",
        description="If you need help with Computer Science, click here!",
        emoji="💻",
    ),
    discord.SelectOption(
        label="Fine Art Helpers",
        description="If you need help with Fine Arts, click here!",
        emoji="🎨",
    ),
    discord.SelectOption(
        label="Other Helpers",
        description="If you need help with anything else, click here!",
        emoji="🧐",
    ),
]


async def TicketExport(
    self,
    channel: discord.TextChannel,
    response: discord.TextChannel = None,
    user: discord.User = None,
    responsesauthor: typing.List[discord.User] = None
):
    transcript = await chat_exporter.export(channel, None)
    query = (
        database.TicketInfo.select()
        .where(database.TicketInfo.ChannelID == channel.id)
        .get()
    )
    TicketOwner = await self.bot.fetch_user(query.authorID)

    if transcript is None:
        return

    embed = discord.Embed(title="Channel Transcript", color=discord.Colour.green())
    embed.set_author(
        name=f"{user.name}#{user.discriminator}",
        url=user.avatar.url,
        icon_url=user.avatar.url,
    )
    embed.add_field(name="Transcript Owner", value=TicketOwner.mention)
    embed.add_field(name="Ticket Name", value=channel.name, inline=False)
    embed.add_field(name="Category", value=channel.category.name)
    embed.set_footer(text="Transcript Attached Below")

    transcript_file = discord.File(
        io.BytesIO(transcript.encode()), filename=f"transcript-{channel.name}.html"
    )

    if response != None:
        msg = await response.send(embed=embed)
        await response.send(file=transcript_file)
    if responsesauthor != None:
        transcript = await chat_exporter.export(channel, None)
        transcript_file = discord.File(
            io.BytesIO(transcript.encode()), filename=f"transcript-{channel.name}.html"
        )
        for UAuthor in responsesauthor:
            try:
                await UAuthor.send(embed = embed, file=transcript_file)
            except Exception:
                continue
        if user not in responsesauthor:
            transcript = await chat_exporter.export(channel, None)
            transcript_file = discord.File(
                io.BytesIO(transcript.encode()), filename=f"transcript-{channel.name}.html"
            )
            try:
                await user.send(embed = embed, file=transcript_file)
            except Exception:
                pass
        
    return msg, transcript_file


def decodeDict(self, value: str) -> typing.Union[str, int]:
    """Returns the true value of a dict output and pair value.

    Args:
        value (str): Dict output

    Returns:
        typing.Union[str, int]: Raw output of the Dict and Pair value.
    """

    EssayOptions = [
        discord.SelectOption(label="Essay Reviser"),
        discord.SelectOption(label="Other"),
    ]

    EnglishOptions = [
        discord.SelectOption(label="English Language"),
        discord.SelectOption(label="English Literature"),
        discord.SelectOption(label="Other"),
    ]

    MathOptions = [
        discord.SelectOption(label="Algebra"),
        discord.SelectOption(label="Geometry"),
        discord.SelectOption(label="Precalculous"),
        discord.SelectOption(label="Calculous"),
        discord.SelectOption(label="Statistics"),
        discord.SelectOption(label="Other"),
    ]

    ScienceOptions = [
        discord.SelectOption(label="Biology"),
        discord.SelectOption(label="Chemistry"),
        discord.SelectOption(label="Biology"),
        discord.SelectOption(label="Physics"),
        discord.SelectOption(label="Psych"),
        discord.SelectOption(label="Other"),
    ]

    SocialStudiesOptions = [
        discord.SelectOption(label="World History"),
        discord.SelectOption(label="US History"),
        discord.SelectOption(label="US Gov"),
        discord.SelectOption(label="Euro"),
        discord.SelectOption(label="Human Geo"),
        discord.SelectOption(label="Economy Helper"),
        discord.SelectOption(label="Other"),
    ]

    LanguageOptions = [
        discord.SelectOption(label="French"),
        discord.SelectOption(label="Chinese"),
        discord.SelectOption(label="Korean"),
        discord.SelectOption(label="Spanish"),
        discord.SelectOption(label="Other"),
    ]

    OtherOptions = [
        discord.SelectOption(label="Computer Science"),
        discord.SelectOption(label="Fine Arts"),
        discord.SelectOption(label="Research"),
        discord.SelectOption(label="SAT/ACT"),
    ]

    decodeName = {
        "['Math Helpers']": "Math Helpers",
        "['Science Helpers']": "Science Helpers",
        "['Social Studies Helpers']": "Social Studies Helpers",
        "['English Helpers']": "English Helpers",
        "['Essay Helpers']": "Essay Helpers",
        "['Language Helpers']": "Language Helpers",
        "['Computer Science Helpers']": "Computer Science Helpers",
        "['Fine Art Helpers']": "Fine Art Helpers",
        "['Other Helpers']": "Other Helpers",
    }

    decodeOptList = {
        "['Math Helpers']": MathOptions,
        "['Science Helpers']": ScienceOptions,
        "['Social Studies Helpers']": SocialStudiesOptions,
        "['English Helpers']": EnglishOptions,
        "['Essay Helpers']": EssayOptions,
        "['Language Helpers']": LanguageOptions,
        "['Computer Science Helpers']": MAIN_ID.cat_scienceTicket,
        "['Fine Art Helpers']": MAIN_ID.cat_fineArtsTicket,
        "['Other Helpers']": OtherOptions,
    }

    decodeID = {
        "['Math Helpers']": MAIN_ID.cat_mathTicket,
        "['Science Helpers']": MAIN_ID.cat_scienceTicket,
        "['Social Studies Helpers']": MAIN_ID.cat_socialStudiesTicket,
        "['English Helpers']": MAIN_ID.cat_englishTicket,
        "['Essay Helpers']": MAIN_ID.cat_essayTicket,
        "['Language Helpers']": MAIN_ID.cat_languageTicket,
        "['Computer Science Helpers']": MAIN_ID.cat_scienceTicket,
        "['Fine Art Helpers']": MAIN_ID.cat_fineArtsTicket,
        "['Other Helpers']": MAIN_ID.cat_otherTicket,
    }
    name = decodeName[value]
    CategoryID = decodeID[value]
    if type(decodeOptList[value]) == int:
        OptList = name
    else:
        OptList = decodeOptList[value]

    return name, CategoryID, OptList


class DropdownTickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mainserver = MAIN_ID.g_main
        self.ServerIDs = [TECH_ID.g_tech, ACAD_ID.g_acad, MKT_ID.g_mkt, HR_ID.g_hr]
        self.TICKET_INACTIVE_TIME = Others.TICKET_INACTIVE_TIME
        self.TicketInactive.start()

    def cog_unload(self):
        self.TicketInactive.cancel()
    
    @commands.Cog.listener("on_interaction")
    async def TicketDropdown(self, interaction: discord.Interaction):
        InteractionResponse = interaction.data

        if interaction.message is None:
            return

        try:
            val = InteractionResponse["custom_id"]
        except KeyError:
            return

        if (
            interaction.guild_id == self.mainserver
            and interaction.message.id == 904375029989515355
            and InteractionResponse["custom_id"] == "persistent_view:ticketdrop"
        ):
            channel = await self.bot.fetch_channel(interaction.channel_id)
            # guild = await self.bot.fetch_guild(interaction.guild_id)
            guild = interaction.message.guild
            author = interaction.user
            DMChannel = await author.create_dm()

            def check(m):
                return (
                    m.content is not None
                    and m.channel == DMChannel
                    and m.author.id is author.id
                )

            ViewResponse = str(InteractionResponse["values"])
            print(ViewResponse)
            TypeSubject, CategoryID, OptList = decodeDict(self, ViewResponse)
            print(f"CATID: {CategoryID}")
            c = discord.utils.get(guild.categories, id=int(CategoryID))
            print(c)

            if not TypeSubject == OptList:
                MiscOptList = discord.ui.View()
                MiscOptList.add_item(
                    SelectMenuHandler(
                        OptList,
                        place_holder="Select a more specific subject!",
                        select_user=author,
                    )
                )

                embed = discord.Embed(
                    title="1) Ticket Info", color=discord.Color.gold()
                )
                try:
                    await DMChannel.send(embed=embed, view=MiscOptList)
                except Exception as e:
                    await interaction.followup.user.send(embed=embed, view=MiscOptList)
                timeout = await MiscOptList.wait()
                if not timeout:
                    selection_str = MiscOptList.value
                else:
                    return await DMChannel.send("Timed out, try again later.")
            else:
                selection_str = TypeSubject

            embed = discord.Embed(title="2) Send Question", color=discord.Color.blue())
            await DMChannel.send(embed=embed)
            answer1 = await self.bot.wait_for("message", check=check)

            embed = discord.Embed(
                title="3) Send Assignment Title",
                description="**Acceptable Forms of Proof:**\n1) Images/Attachments.\n2) URL's such as Gyazo.",
                color=discord.Color.blue(),
            )

            await DMChannel.send(embed=embed)
            answer2: discord.Message = await self.bot.wait_for("message", check=check)

            attachmentlist = []
            if answer2.attachments:
                for URL in answer2.attachments:
                    attachmentlist.append(URL.url)
            else:
                if answer2.content.find("https://") != -1:
                    attachmentlist.append(answer2.content)
                else:
                    return await DMChannel.send("No attachments found.")

            print(attachmentlist)
            CounterNum = (
                database.BaseTickerInfo.select()
                .where(database.BaseTickerInfo.id == 1)
                .get()
            )
            TNUM = CounterNum.counter
            CounterNum.counter = CounterNum.counter + 1
            CounterNum.save()

            LDC = await DMChannel.send(f"Please wait, creating your ticket {Emoji.loadingGIF}")
            channel: discord.TextChannel = await guild.create_text_channel(
                f"{selection_str}-{TNUM}", category=c
            )
            await channel.set_permissions(
                guild.default_role, read_messages=False, reason="Ticket Perms"
            )
            query = database.TicketInfo.create(ChannelID=channel.id, authorID=author.id)
            query.save()

            roles = [
                "Board Member",
                "Senior Executive",
                "Executive",
                "Head Moderator",
                "Moderator",
                "Academic Manager",
                "Lead Helper",
                "Chat Helper",
                "Bot: TeXit",
            ]
            for role in roles:
                print(role)
                RoleOBJ = discord.utils.get(interaction.message.guild.roles, name=role)
                await channel.set_permissions(
                    RoleOBJ,
                    read_messages=True,
                    send_messages=True,
                    reason="Ticket Perms",
                )
            await channel.set_permissions(
                interaction.message.author,
                read_messages=True,
                send_messages=True,
                reason="Ticket Perms (User)",
            )

            controlTicket = discord.Embed(
                title="Control Panel",
                description="To end this ticket, click the lock button!",
                color=discord.Colour.gold(),
            )
            LockControlButton = discord.ui.View()
            LockControlButton.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.green,
                    url=None,
                    disabled=False,
                    label="Lock",
                    emoji="🔒",
                    custom_id="ch_lock",
                )
            )
            await channel.send(
                interaction.user.mention, embed=controlTicket, view=LockControlButton
            )
            attachmentlist = ", ".join(attachmentlist)

            embed = discord.Embed(title="Ticket Information", color=discord.Colour.blue())
            embed.set_author(
                name=f"{interaction.user.name}#{interaction.user.discriminator}",
                url=interaction.user.avatar.url,
                icon_url=interaction.user.avatar.url,
            )
            embed.add_field(name="Question:", value=answer1.content, inline=False)
            embed.add_field(name="Attachment URL:", value=attachmentlist)
            #embed.set_image(url=attachmentlist[0])
            await channel.send(embed=embed)

            await LDC.edit(f"Ticket Created!\nYou can view it here: {channel.mention}")

        elif val == "ch_lock":
            channel = interaction.message.channel
            guild = interaction.message.guild
            author = interaction.user

            query = (
                database.TicketInfo.select()
                .where(database.TicketInfo.ChannelID == interaction.channel_id)
                .get()
            )
            embed = discord.Embed(
                title="Confirm?",
                description="Click an appropriate button.",
                color=discord.Colour.red(),
            )
            ButtonViews = discord.ui.View()
            ButtonViews.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.green,
                    label="Confirm",
                    custom_id="ch_lock_CONFIRM",
                    emoji="✅",
                    button_user=author,
                )
            )
            ButtonViews.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.red,
                    label="Cancel",
                    custom_id="ch_lock_CANCEL",
                    emoji="❌",
                    button_user=author,
                )
            )
            await channel.send(embed=embed, view=ButtonViews)

        elif InteractionResponse["custom_id"] == "ch_lock_CONFIRM":
            channel = interaction.message.channel
            guild = interaction.message.guild
            author = interaction.user
            query = (
                database.TicketInfo.select()
                .where(database.TicketInfo.ChannelID == interaction.channel_id)
                .get()
            )

            TicketOwner = await guild.fetch_member(query.authorID)
            await channel.set_permissions(
                TicketOwner, read_messages=False, reason="Ticket Perms Close (User)"
            )

            await interaction.message.delete()
            embed = discord.Embed(
                title="Support Staff Commands",
                description="Click an appropriate button.",
                color=discord.Colour.red(),
            )
            ButtonViews2 = discord.ui.View()

            ButtonViews2.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.green,
                    label="Close & Delete Ticket",
                    custom_id="ch_lock_C&D",
                    emoji="🔒",
                )
            )
            ButtonViews2.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.blurple,
                    label="Create Transcript",
                    custom_id="ch_lock_T",
                    emoji="📝",
                )
            )
            ButtonViews2.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.red,
                    label="Cancel",
                    custom_id="ch_lock_C",
                    emoji="❌",
                )
            )

            await channel.send(embed=embed, view=ButtonViews2)

        elif InteractionResponse["custom_id"] == "ch_lock_CANCEL":
            channel = interaction.message.channel
            author = interaction.user
            await channel.send(
                f"{author.mention} Alright, canceling request.", delete_after=5.0
            )
            await interaction.message.delete()

        elif InteractionResponse["custom_id"] == "ch_lock_C":
            channel = await self.bot.fetch_channel(interaction.channel_id)
            author = interaction.user

            await channel.send(
                f"{author.mention} Alright, canceling request.", delete_after=5.0
            )
            await interaction.message.delete()

        elif InteractionResponse["custom_id"] == "ch_lock_T":
            channel = await self.bot.fetch_channel(interaction.channel_id)
            ResponseLogChannel = await self.bot.fetch_channel(MAIN_ID.ch_transcriptLogs)
            author = interaction.user

            msg: discord.Message = await TicketExport(
                self, channel, ResponseLogChannel, author
            )
            await channel.send(f"Transcript Created!\n> {msg.jump_url}")

        elif InteractionResponse["custom_id"] == "ch_lock_C&D":
            channel = await self.bot.fetch_channel(interaction.channel_id)
            author = interaction.user
            ResponseLogChannel = await self.bot.fetch_channel(MAIN_ID.ch_transcriptLogs)
            query = (
                database.TicketInfo.select()
                .where(database.TicketInfo.ChannelID == interaction.channel_id)
                .get()
            )
            TicketOwner = await self.bot.fetch_user(query.authorID)

            messages = await channel.history(limit=None).flatten()
            authorList = []

            for msg in messages:
                if msg.author not in authorList:
                    authorList.append(msg.author)
            msg, transcript_file = await TicketExport(
                self, channel, ResponseLogChannel, TicketOwner, authorList
            )

            await channel.send(f"Transcript Created!\n> {msg.jump_url}")
            await asyncio.sleep(5)
            await channel.send(f"{author.mention} Alright, closing ticket.")
            await channel.delete()
            query.delete()

    @tasks.loop(hours=1.0)
    async def TicketInactive(self):
        TicketInfoTB = database.TicketInfo
        for entry in TicketInfoTB:
            channel: discord.TextChannel = await self.bot.fetch_channel(entry.ChannelID)
            fetchMessage = await channel.history(limit=1).flatten()
            query = (
                database.TicketInfo.select()
                .where(database.TicketInfo.ChannelID == entry.ChannelID)
                .get()
            )
            TicketOwner = await self.bot.fetch_user(query.authorID)
            messages = await channel.history(limit=None).flatten()
            authorList = []

            if fetchMessage[0].created_at < (datetime.now(pytz.timezone("US/Eastern")) - timedelta(
                minutes=self.TICKET_INACTIVE_TIME
            )):
                await channel.send(
                    f"Ticket has been inactive for {self.TICKET_INACTIVE_TIME} hours.\nTicket has been closed."
                )
                for msg in messages:
                    if msg.author not in authorList:
                        authorList.append(msg.author)

                msg, transcript_file = await TicketExport(
                    self, channel, None, TicketOwner, authorList
                )


                await channel.delete()
                query.delete()


    @commands.command()
    async def sendCHTKTView(self, ctx):
        MasterSubjectView = discord.ui.View()
        MasterSubjectView.add_item(
            SelectMenuHandler(
                MasterSubjectOptions,
                "persistent_view:ticketdrop",
                "masa short",
                1,
                1,
                interaction_message="Check your DM's!",
                ephemeral=True,
            )
        )
        await ctx.send("hello", view=MasterSubjectView)


def setup(bot):
    bot.add_cog(DropdownTickets(bot))
