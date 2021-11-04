import asyncio
import io
import os
import typing
from datetime import datetime, timedelta
from io import BytesIO

import chat_exporter
import discord
import pytz
from core import database
from core.common import (
    ACAD_ID,
    HR_ID,
    MAIN_ID,
    MKT_ID,
    TECH_ID,
    ButtonHandler,
    Emoji,
    Others,
    S3_upload_file,
    SelectMenuHandler,
)
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(
        label="Create Ticket",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:ticketdrop",
        emoji="📝",
    )
    async def verify(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True

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
    responsesauthor: typing.List[discord.User] = None,
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
        url=user.display_avatar.url,
        icon_url=user.display_avatar.url,
    )
    embed.add_field(name="Transcript Owner", value=TicketOwner.mention)
    embed.add_field(name="Ticket Name", value=channel.name, inline=False)
    embed.add_field(name="Category", value=channel.category.name)
    embed.set_footer(text="Transcript Attached Above")
    var = transcript.encode()

    transcript_file = discord.File(
        io.BytesIO(var), filename=f"transcript-{channel.name}.html"
    )

    myIO = BytesIO()
    myIO.write(var)
    with open(f"transcript-{channel.name}.html", "wb") as f:
        f.write(myIO.getbuffer())

    S3_upload_file(f"transcript-{channel.name}.html", "ch-transcriptlogs")
    S3_URL = f"[Direct Transcript Link](https://acad-transcripts.schoolsimplified.org/transcript-{channel.name}.html)"
    embed.add_field(name="Transcript Link", value=S3_URL)
    if response != None:
        msg = await response.send(embed=embed)
    if responsesauthor != None:
        for UAuthor in responsesauthor:
            try:
                await UAuthor.send(embed=embed)
            except Exception:
                continue
        if user not in responsesauthor:
            try:
                await user.send(embed=embed)
            except Exception:
                pass

    os.remove(f"transcript-{channel.name}.html")

    if response == None:
        msg == None
    return msg, transcript_file, S3_URL


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
        discord.SelectOption(label="Precalculus"),
        discord.SelectOption(label="Calculus"),  # Calculus
        discord.SelectOption(label="Statistics"),
        discord.SelectOption(label="Other"),
    ]

    ScienceOptions = [
        discord.SelectOption(label="Biology"),
        discord.SelectOption(label="Chemistry"),
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
        discord.SelectOption(label="Other Languages"),
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
        "['Computer Science Helpers']": MAIN_ID.cat_otherTicket,
        "['Fine Art Helpers']": MAIN_ID.cat_otherTicket,
        "['Other Helpers']": OtherOptions,
    }

    decodeID = {
        "['Math Helpers']": MAIN_ID.cat_mathTicket,
        "['Science Helpers']": MAIN_ID.cat_scienceTicket,
        "['Social Studies Helpers']": MAIN_ID.cat_socialStudiesTicket,
        "['English Helpers']": MAIN_ID.cat_englishTicket,
        "['Essay Helpers']": MAIN_ID.cat_essayTicket,
        "['Language Helpers']": MAIN_ID.cat_languageTicket,
        "['Computer Science Helpers']": MAIN_ID.cat_otherTicket,
        "['Fine Art Helpers']": MAIN_ID.cat_otherTicket,
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
        self.CHID_DEFAULT = Others.CHID_DEFAULT
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
            #and interaction.message.id == int(self.CHID_DEFAULT)
            and InteractionResponse["custom_id"] == "persistent_view:ticketdrop"
        ):
            channel = await self.bot.fetch_channel(interaction.channel_id)
            guild = interaction.message.guild
            author = interaction.user
            DMChannel = await author.create_dm()
            try:
                await interaction.response.send_message(
                    "Check your DM's!", ephemeral=True
                )
            except Exception:
                await interaction.followup.send("Check your DM's!", ephemeral=True)
            except Exception:
                await interaction.channel.send(
                    f"{interaction.user.mention} Check your DM's!", delete_after=5.0
                )

            def check(m):
                return (
                    m.content is not None
                    and m.channel == DMChannel
                    and m.author.id is author.id
                )
            
            MSV = discord.ui.View()
            var = SelectMenuHandler(
                    MasterSubjectOptions,
                    "persistent_view:ticketdrop",
                    "Click a subject!"
                )
            MSV.add_item(
                var
            )
            await DMChannel.send("**Let's start this!**\nStart off by selecting a subject that matches what your ticket is about!", view = MSV)
            timeout = await MSV.wait()
            if not timeout:
                MasterSubjectView = var.view_response
            else:
                return await DMChannel.send("Timed out, try again later.")

            ViewResponse = str(MasterSubjectView)
            print(ViewResponse)
            TypeSubject, CategoryID, OptList = decodeDict(self, f"['{ViewResponse}']")
            print(f"CATID: {CategoryID}")
            c = discord.utils.get(guild.categories, id=int(CategoryID))

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
                    title="1) Ticket Info", description="Select a more specific topic!", color=discord.Color.gold()
                )
                try:
                    await DMChannel.send(embed=embed, view=MiscOptList)
                except Exception as e:
                    await interaction.followup.send(embed=embed, view=MiscOptList)

                timeout = await MiscOptList.wait()
                if not timeout:
                    selection_str = MiscOptList.value
                else:
                    return await DMChannel.send("Timed out, try again later.")
            else:
                selection_str = TypeSubject

            embed = discord.Embed(title="2) Send Question", description="Whats your question?", color=discord.Color.blue())
            await DMChannel.send(embed=embed)
            answer1 = await self.bot.wait_for("message", check=check)
            if answer1.content is None or answer1.content == "" or answer1.content == " ":
                return await DMChannel.send("No question was sent, try selecting a subject back in the homework help channel again.")

            embed = discord.Embed(
                title="3) Send Assignment Title",
                description="**Acceptable Forms of Proof:**\n1) Images/Attachments.\n2) URL's such as Gyazo.",
                color=discord.Color.blue(),
            )
            embed.set_footer(text="We need images/urls as proof that you aren't cheating, School Simplified does not offer assistance on assessments.")

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

            LDC = await DMChannel.send(
                f"Please wait, creating your ticket {Emoji.loadingGIF}"
            )
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
                RoleOBJ = discord.utils.get(interaction.message.guild.roles, name=role)
                await channel.set_permissions(
                    RoleOBJ,
                    read_messages=True,
                    send_messages=True,
                    reason="Ticket Perms",
                )
            await channel.set_permissions(
                interaction.user,
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

            try:
                embed = discord.Embed(
                    title="Ticket Information", color=discord.Colour.blue()
                )
                embed.set_author(
                    name=f"{interaction.user.name}#{interaction.user.discriminator}",
                    url=interaction.user.avatar.url,
                    icon_url=interaction.user.avatar.url,
                )
                embed.add_field(name="Question:", value=f"A: {answer1.content}", inline=False)
                embed.add_field(name="Attachment URL:", value=f"URL: {attachmentlist}")
                # embed.set_image(url=attachmentlist[0])
                await channel.send(embed=embed)
                await channel.send(f"URLs:\n{attachmentlist}")
            except Exception as e:
                print(e)
                await channel.send(
                    f"**Ticket Information**\n\n{interaction.user.mention}\nQuestion: {answer1.content}"
                )
                await channel.send(f"Attachment URL: {str(attachmentlist)}")

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
            try:
                await interaction.followup.send(embed=embed, view=ButtonViews)
            except:
                try:
                    await interaction.response.send_message(embed=embed, view=ButtonViews)
                except:
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
            embed.set_footer(text = "This ticket has been closed!")
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
                    style=discord.ButtonStyle.grey,
                    label="Re-Open Ticket",
                    custom_id="ch_lock_R",
                    emoji="🔓",
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
            await interaction.channel.send(
                f"{author.mention} Alright, canceling request.", delete_after=5.0
            )
            await interaction.message.delete()

        elif InteractionResponse["custom_id"] == "ch_lock_C":
            channel = await self.bot.fetch_channel(interaction.channel_id)
            author = interaction.user

            try:
                await interaction.response.send_message(
                    f"{author.mention} Alright, canceling request.", delete_after=5.0
                )
            except Exception:
                await interaction.channel.send(
                    f"{author.mention} Alright, canceling request.", delete_after=5.0
                )
            await interaction.message.delete()
        
        elif InteractionResponse["custom_id"] == "ch_lock_R":
            """
            Re-open Ticket
            """
            channel = await self.bot.fetch_channel(interaction.channel_id)
            author = interaction.user
            guild = interaction.message.guild
            query = (
                database.TicketInfo.select()
                .where(database.TicketInfo.ChannelID == interaction.channel_id)
                .get()
            )
            TicketOwner = await guild.fetch_member(query.authorID)
            await channel.set_permissions(
                TicketOwner, read_messages=True, reason="Ticket Perms ReOpen (User)"
            )
            
            try:
                await interaction.response.send_message(
                    f"{author.mention} Ticket has been re-opened.", delete_after=5.0
                )
            except Exception:
                await interaction.channel.send(
                    f"{author.mention} Ticket has been re-opened.", delete_after=5.0
                )
            await interaction.message.delete()


        elif InteractionResponse["custom_id"] == "ch_lock_T":
            channel = await self.bot.fetch_channel(interaction.channel_id)
            ResponseLogChannel = await self.bot.fetch_channel(MAIN_ID.ch_transcriptLogs)
            author = interaction.user
            msg = await interaction.channel.send(f"Please wait, creating your transcript {Emoji.loadingGIF2}")

            msg, file, S3_URL = await TicketExport(
                self, channel, ResponseLogChannel, author
            )
            await msg.delete()
            await interaction.channel.send(f"Transcript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {S3_URL}")

        elif InteractionResponse["custom_id"] == "ch_lock_C&D":
            channel = await self.bot.fetch_channel(interaction.channel_id)
            author = interaction.user
            ResponseLogChannel = await self.bot.fetch_channel(MAIN_ID.ch_transcriptLogs)
            query = (
                database.TicketInfo.select()
                .where(database.TicketInfo.ChannelID == interaction.channel_id)
                .get()
            )
            msgO = await interaction.channel.send(f"Please wait, generating a transcript {Emoji.loadingGIF2}")
            TicketOwner = await self.bot.fetch_user(query.authorID)

            messages = await channel.history(limit=None).flatten()
            authorList = []

            for msg in messages:
                if msg.author not in authorList:
                    authorList.append(msg.author)
            msg, transcript_file, url = await TicketExport(
                self, channel, ResponseLogChannel, TicketOwner, authorList
            )
            #S3_upload_file(transcript_file.filename, "ch-transcriptlogs")
            #print(transcript_file.filename)

            try:
                await msgO.edit(
                    f"Transcript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {url}"
                )
            except Exception:
                try:
                    await msgO.edit(
                        f"Transcript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {url}"
                    )
                except Exception:
                    await msgO.edit(
                        f"Transcript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {url}"
                    )
            await asyncio.sleep(5)
            await channel.send(f"{author.mention} Alright, closing ticket.")
            await channel.delete()
            query.delete()

    @tasks.loop(hours=1.0)
    async def TicketInactive(self):
        TicketInfoTB = database.TicketInfo
        for entry in TicketInfoTB:
            try:
                channel: discord.TextChannel = await self.bot.fetch_channel(
                    entry.ChannelID
                )
            except Exception as e:
                print(entry.ChannelID, e)
                continue
            fetchMessage = await channel.history(limit=1).flatten()
            query = (
                database.TicketInfo.select()
                .where(database.TicketInfo.ChannelID == entry.ChannelID)
                .get()
            )
            TicketOwner = await self.bot.fetch_user(query.authorID)
            messages = await channel.history(limit=None).flatten()
            authorList = []
            if len(messages) == 0:
                continue

            if fetchMessage[0].created_at < (
                datetime.now(pytz.timezone("US/Eastern"))
                - timedelta(minutes=self.TICKET_INACTIVE_TIME)
            ):
                await channel.send(
                    f"Ticket has been inactive for {self.TICKET_INACTIVE_TIME} hours.\nTicket has been closed."
                )
                for msgI in messages:
                    if msgI.author not in authorList:
                        authorList.append(msgI.author)

                msg, transcript_file, url = await TicketExport(
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
                "Click here to start a ticket!",
                1,
                1,
                interaction_message="Check your DM's!",
                ephemeral=True,
            )
        )
        await ctx.send(
            """**Note:** *Make sure to allow direct messages from server members!*\n
        <:SchoolSimplified:820705120429277194> **__How to Get School Help:__**
            > <:SS:865715703545069568> Click on the button to start the process.
            > <:SS:865715703545069568> In your direct messages with <@852251896130699325>, select the sub-topic you need help with.
            > <:SS:865715703545069568> Send the question in your direct messages as per the bot instructions.
            > <:SS:865715703545069568> Send a picture of your assignment title in your direct messages as per the bot instructions.""",
            view=TicketButton(),
        )


def setup(bot):
    bot.add_cog(DropdownTickets(bot))
