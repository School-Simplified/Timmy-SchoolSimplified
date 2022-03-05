import asyncio
import io
import os
import typing
from datetime import datetime, timedelta
from pytz import timezone
from io import BytesIO
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

import chat_exporter
import discord
import pytz
from core import database
from core.common import (
    CH_ID,
    TUT_ID,
    HR_ID,
    MAIN_ID,
    MKT_ID,
    TECH_ID,
    ButtonHandler,
    Emoji,
    Others,
    SandboxConfig,
    S3_upload_file,
    SelectMenuHandler,
    CHHelperRoles,
    access_secret,
)
from discord.ext import commands, tasks
from dotenv import load_dotenv
from core.checks import is_botAdmin

load_dotenv()

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
essayTicketLog_key = "1pB5xpsBGKIES5vmEY4hjluFg7-FYolOmN_w3s20yzr0"

creds = access_secret("gsheets_c", True, 3, scope)
gspread_client = gspread.authorize(creds)
print("Connected to Gspread.")


"""
if not (RoleOBJ.id == MAIN_ID.r_chatHelper or RoleOBJ.id == MAIN_ID.r_leadHelper) and not channel.category.id == MAIN_ID.cat_essayTicket:
                    if RoleOBJ.id == MAIN_ID.r_essayReviser:
                        if channel.category.id == MAIN_ID.cat_essayTicket or channel.category.id == MAIN_ID.cat_englishTicket:
"""
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
    directTranscript: bool = False,
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
    try:
        os.remove(f"transcript-{channel.name}.html")
    except:
        pass

    if response == None:
        msg = S3_URL
    return msg, transcript_file, S3_URL


def decodeDict(self, value: str, sandbox: bool = False) -> typing.Union[str, int]:
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
        discord.SelectOption(label="Economy"),
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
        "['Other Helpers']": "Other Helpers",
    }

    decodeOptList = {
        "['Math Helpers']": MathOptions,
        "['Science Helpers']": ScienceOptions,
        "['Social Studies Helpers']": SocialStudiesOptions,
        "['English Helpers']": EnglishOptions,
        "['Essay Helpers']": EssayOptions,
        "['Language Helpers']": LanguageOptions,
        "['Other Helpers']": OtherOptions,
    }

    if sandbox:
        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        decodeID = {
            "['Math Helpers']": q.cat_mathticket,
            "['Science Helpers']": q.cat_scienceticket,
            "['Social Studies Helpers']": q.cat_socialstudiesticket,
            "['English Helpers']": q.cat_englishticket,
            "['Essay Helpers']": q.cat_essayticket,
            "['Language Helpers']": q.cat_otherticket,
            "['Other Helpers']": q.cat_otherticket,
        }
    else:
        decodeID = {
            "['Math Helpers']": MAIN_ID.cat_mathTicket,
            "['Science Helpers']": MAIN_ID.cat_scienceTicket,
            "['Social Studies Helpers']": MAIN_ID.cat_socialStudiesTicket,
            "['English Helpers']": MAIN_ID.cat_englishTicket,
            "['Essay Helpers']": MAIN_ID.cat_essayTicket,
            "['Language Helpers']": MAIN_ID.cat_otherTicket,
            "['Other Helpers']": MAIN_ID.cat_otherTicket,
        }

    name = decodeName[value]
    CategoryID = decodeID[value]
    if type(decodeOptList[value]) == int:
        OptList = name
    else:
        OptList = decodeOptList[value]

    return name, CategoryID, OptList


def getRole(
    guild: discord.Guild, mainSubject: str, subject: str, sandbox: bool = False
) -> discord.Role:
    """Returns the role of the subject.

    Args:
        guild (discord.Guild): The guild where the role is in
        mainSubject (str): Main subject name
        subject (str): Subject name

    Returns:
        discord.Role: Role of the subject
    """

    mainSubject = mainSubject.title()
    subject = subject.title()

    if subject == "Other":
        role = guild.get_role(CHHelperRoles[mainSubject])
    else:
        role = guild.get_role(CHHelperRoles[subject])

    return role


class TicketBT(discord.ui.Button):
    def __init__(self, bot):
        """
        A button for one role. `custom_id` is needed for persistent views.
        """
        self.bot = bot
        self.mainserver = MAIN_ID.g_main
        self.ServerIDs = [
            TECH_ID.g_tech,
            CH_ID.g_ch,
            TUT_ID.g_tut,
            MKT_ID.g_mkt,
            HR_ID.g_hr,
        ]
        self.TICKET_INACTIVE_TIME = Others.TICKET_INACTIVE_TIME
        self.CHID_DEFAULT = Others.CHID_DEFAULT
        self.EssayCategory = [CH_ID.cat_essay, CH_ID.cat_essay]
        self.sheet = gspread_client.open_by_key(essayTicketLog_key).sheet1

        super().__init__(
            label="Create Ticket",
            style=discord.enums.ButtonStyle.blurple,
            custom_id="persistent_view:ticketdrop",
            emoji="📝",
        )

    async def callback(self, interaction: discord.Interaction):
        Sandbox = False
        if interaction.message.guild.id == TECH_ID.g_tech:
            Sandbox = True

        bucket = self.view.cd_mapping.get_bucket(interaction.message)
        retry_after = bucket.update_rate_limit()
        print(retry_after)
        if retry_after:
            return await interaction.response.send_message(
                "Sorry, you are being rate limited.", ephemeral=True
            )
        else:
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

            def check(m):
                return (
                    m.content is not None
                    and m.channel == DMChannel
                    and m.author.id is author.id
                )

            MSV = discord.ui.View()
            var = SelectMenuHandler(
                MasterSubjectOptions, "persistent_view:ticketdrop", "Click a subject!"
            )
            MSV.add_item(var)
            try:
                await DMChannel.send(
                    "**Let's start this!**\nStart off by selecting a subject that matches what your ticket is about!",
                    view=MSV,
                )
            except Exception as e:
                await interaction.channel.send(
                    f"{interaction.user.mention} I can't send you messages, please check you're privacy settings!",
                    delete_after=5.0,
                )
            timeout = await MSV.wait()
            if not timeout:
                MasterSubjectView = var.view_response
            else:
                return await DMChannel.send("Timed out, try again later.")

            ViewResponse = str(MasterSubjectView)
            TypeSubject, CategoryID, OptList = decodeDict(
                self, f"['{ViewResponse}']", Sandbox
            )
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
                    title="1) Ticket Info",
                    description="Select a more specific topic!",
                    color=discord.Color.gold(),
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

            if ViewResponse == "Essay Helpers" and selection_str == "Essay Reviser":
                embed = discord.Embed(
                    title="2) Send Google Docs Link",
                    description="Please send the link of a Google Docs of your essay."
                    "\nDo not send a file.",
                    color=discord.Color.blue(),
                )
                await DMChannel.send(embed=embed)

                answer1 = await self.bot.wait_for("message", check=check)
                if (
                    answer1.content is None
                    or answer1.content == ""
                    or answer1.content == " "
                ):
                    return await DMChannel.send(
                        "No message was sent, try selecting a subject back in the homework help channel again."
                    )

                attachmentlist = []

                uri_re = re.compile(
                    r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|"""
                    r"""www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?"""
                    r""":[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))"""
                    r"""*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|"""
                    r"""[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
                )

                list_input = uri_re.split(answer1.content)
                if len(list_input) > 1:
                    found_link = list_input[1]
                    found_link = re.sub(r"^.*?https", "https", found_link)
                    if ":" in found_link:
                        last_check = found_link.split(":")
                        if last_check[1].isdigit():
                            found_link = None
                else:
                    found_link = None

                if found_link is not None and "docs.google." in found_link:
                    attachmentlist.append(found_link)
                else:
                    return await DMChannel.send("No Google Docs link found.")

                embed = discord.Embed(
                    title="3) Additional comment",
                    description='If you don\'t have an additional comment, just write "No".',
                    color=discord.Color.blue(),
                )

                await DMChannel.send(embed=embed)
                answer2: discord.Message = await self.bot.wait_for(
                    "message", check=check
                )

            else:
                embed = discord.Embed(
                    title="2) Send Question",
                    description="What is your question or topic?\nDo not send a URL. You must send the question or topic in plain text.",
                    color=discord.Color.blue(),
                )
                await DMChannel.send(embed=embed)
                answer1 = await self.bot.wait_for("message", check=check)
                if (
                    answer1.content is None
                    or answer1.content == ""
                    or answer1.content == " "
                ):
                    return await DMChannel.send(
                        "No question was sent, try selecting a subject back in the homework help channel again."
                    )

                embed = discord.Embed(
                    title="3) Send Assignment Title",
                    description="**Acceptable Forms of Proof:**\n1) Images/Attachments.\n2) URL's such as Gyazo.\n\nSend them all in one message for them to all be sent.",
                    color=discord.Color.blue(),
                )
                embed.set_footer(
                    text="We need images/urls as proof that you aren't cheating, School Simplified does not offer assistance on assessments."
                )

                await DMChannel.send(embed=embed)
                answer2: discord.Message = await self.bot.wait_for(
                    "message", check=check
                )

                attachmentlist = []
                if answer2.attachments:
                    for URL in answer2.attachments:
                        attachmentlist.append(URL.url)
                else:
                    if answer2.content.find("https://") != -1:
                        attachmentlist.append(answer2.content)
                    else:
                        return await DMChannel.send("No attachments found.")

            CounterNum = (
                database.BaseTickerInfo.select()
                .where(database.BaseTickerInfo.guildID == guild.id)
                .get()
            )
            TNUM = CounterNum.counter
            CounterNum.counter = CounterNum.counter + 1
            CounterNum.save()

            LDC = await DMChannel.send(
                f"Please wait, creating your ticket {Emoji.loadingGIF}"
            )

            if TypeSubject == "Language Helpers":
                mainSubject = "languages"
            else:
                mainSubject = (
                    c.name.replace("═", "")
                    .replace("⁃", "")
                    .replace("Ticket", "")
                    .strip()
                )

            if selection_str == "Other":
                channel: discord.TextChannel = await guild.create_text_channel(
                    f"other-{mainSubject}-{TNUM}", category=c
                )
            else:
                channel: discord.TextChannel = await guild.create_text_channel(
                    f"{selection_str}-{TNUM}", category=c
                )

            await channel.set_permissions(
                guild.default_role, read_messages=False, reason="Ticket Perms"
            )
            tz = timezone("EST")
            opened_at = datetime.now(tz)
            query = database.TicketInfo.create(
                ChannelID=channel.id, authorID=author.id, createdAt=opened_at
            )
            query.save()

            if not Sandbox:
                roles = [
                    # "Board Member",
                    # "Senior Executive",
                    # "Executive",
                    "Head Moderator",
                    "Moderator",
                    "Lead Helper",
                    "Chat Helper",
                    "Bot: TeXit",
                    "Academics Director",
                ]
                for role in roles:
                    RoleOBJ = discord.utils.get(
                        interaction.message.guild.roles, name=role
                    )
                    await channel.set_permissions(
                        RoleOBJ,
                        read_messages=True,
                        send_messages=True,
                        manage_messages=True,
                        reason="Ticket Perms",
                    )
                    RoleOBJ = discord.utils.get(guild.roles, name=role)
                    if (
                        not (
                            RoleOBJ.id == MAIN_ID.r_chatHelper
                            or RoleOBJ.id == MAIN_ID.r_leadHelper
                        )
                        and not channel.category.id == MAIN_ID.cat_essayTicket
                    ):
                        if RoleOBJ.id == MAIN_ID.r_essayReviser:
                            if (
                                channel.category.id == MAIN_ID.cat_essayTicket
                                or channel.category.id == MAIN_ID.cat_englishTicket
                            ):
                                await channel.set_permissions(
                                    RoleOBJ,
                                    read_messages=True,
                                    send_messages=True,
                                    reason="Ticket Perms",
                                )
                            else:
                                continue
                    else:
                        await channel.set_permissions(
                            RoleOBJ,
                            read_messages=True,
                            send_messages=True,
                            reason="Ticket Perms",
                        )

                if channel.category_id in self.EssayCategory:
                    roles = ["Essay Reviser"]
                    for role in roles:
                        RoleOBJ = discord.utils.get(
                            interaction.message.guild.roles, name=role
                        )
                        await channel.set_permissions(
                            RoleOBJ,
                            read_messages=True,
                            send_messages=True,
                            reason="Ticket Perms",
                        )
                else:
                    roles = ["Chat Helper", "Lead Helper"]
                    for role in roles:
                        RoleOBJ = discord.utils.get(
                            interaction.message.guild.roles, name=role
                        )
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
            await channel.set_permissions(
                interaction.guild.default_role,
                read_messages=False,
                send_messages=False,
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

            LCM = await channel.send(
                interaction.user.mention, embed=controlTicket, view=LockControlButton
            )
            await LCM.pin()
            attachmentlist = ", ".join(attachmentlist)

            try:
                if ViewResponse == "Essay Helpers" and selection_str == "Essay Reviser":
                    embed = discord.Embed(
                        title="Ticket Information", color=discord.Colour.blue()
                    )
                    embed.set_author(
                        name=f"{interaction.user.name}#{interaction.user.discriminator}",
                        url=interaction.user.avatar.url,
                        icon_url=interaction.user.avatar.url,
                    )
                    embed.add_field(
                        name="Google Docs Link: ",
                        value=f"{answer1.content}",
                        inline=False,
                    )
                    embed.add_field(
                        name="Additional Comment:", value=f"{answer2.content}"
                    )

                else:
                    embed = discord.Embed(
                        title="Ticket Information", color=discord.Colour.blue()
                    )
                    embed.set_author(
                        name=f"{interaction.user.name}#{interaction.user.discriminator}",
                        url=interaction.user.avatar.url,
                        icon_url=interaction.user.avatar.url,
                    )
                    embed.add_field(
                        name="Question:", value=f"A: {answer1.content}", inline=False
                    )
                    embed.add_field(
                        name="Attachment URL:", value=f"URL: {attachmentlist}"
                    )

                mentionRole = getRole(interaction.guild, mainSubject, selection_str)

                await channel.send(mentionRole.mention, embed=embed)

            except Exception as e:
                print(f"{e.__class__.__name__}: {e}")
                await channel.send(
                    f"**Ticket Information**\n\n{interaction.user.mention}\nQuestion: {answer1.content}"
                )
            await channel.send(f"Attachment URL: {str(attachmentlist)}")

            await LDC.edit(f"Ticket Created!\nYou can view it here: {channel.mention}")


class TicketButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

        self.add_item(TicketBT(self.bot))
        self.cookie = 0
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 30, commands.BucketType.member
        )

    """@discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.blurple, emoji="📝", custom_id="persistent_view:ticketdrop")
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        print("hi")
        bucket = self.view.cd_mapping.get_bucket(interaction.message)
        retry_after = bucket.update_rate_limit()
        print(retry_after)
        if retry_after:
            await interaction.response.send_message("Sorry, you are being rate limited.", ephemeral=True)
            return self.stop()
        else:
            pass"""


class DropdownTickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mainserver = MAIN_ID.g_main
        self.ServerIDs = [
            TECH_ID.g_tech,
            CH_ID.g_ch,
            TUT_ID.g_tut,
            MKT_ID.g_mkt,
            HR_ID.g_hr,
        ]
        self.TICKET_INACTIVE_TIME = Others.TICKET_INACTIVE_TIME
        self.CHID_DEFAULT = Others.CHID_DEFAULT
        self.EssayCategory = [CH_ID.cat_essay, CH_ID.cat_essay]
        self.TicketInactive.start()
        self.sheet = gspread_client.open_by_key(essayTicketLog_key).sheet1

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
            # and interaction.message.id == int(self.CHID_DEFAULT)
            and InteractionResponse["custom_id"] == "persistent_view:ticketdrop"
        ):
            pass
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
                await interaction.followup.send(
                    f"{author.mention}\n", embed=embed, view=ButtonViews
                )
            except:
                try:
                    await interaction.response.send_message(
                        f"{author.mention}\n", embed=embed, view=ButtonViews
                    )
                except:
                    await channel.send(
                        f"{author.mention}\n", embed=embed, view=ButtonViews
                    )

        elif InteractionResponse["custom_id"] == "ch_lock_CONFIRM":
            channel = interaction.message.channel
            guild = interaction.message.guild
            author = interaction.user
            query = (
                database.TicketInfo.select()
                .where(database.TicketInfo.ChannelID == interaction.channel_id)
                .get()
            )

            try:
                TicketOwner = await guild.fetch_member(query.authorID)
            except discord.NotFound:
                await channel.send(
                    f"{author.mention} The ticket owner has left the server."
                )
            else:
                await channel.set_permissions(
                    TicketOwner, read_messages=False, reason="Ticket Perms Close(User)"
                )
            await interaction.message.delete()
            embed = discord.Embed(
                title="Support Staff Commands",
                description="Click an appropriate button.",
                color=discord.Colour.red(),
            )
            embed.set_footer(text="This ticket has been closed!")
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
                    style=discord.ButtonStyle.grey,
                    label="Re-Open Ticket",
                    custom_id="ch_lock_R",
                    emoji="🔓",
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

            await channel.send(author.mention, embed=embed, view=ButtonViews2)

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
            try:
                TicketOwner = await guild.fetch_member(query.authorID)
            except discord.NotFound:
                await channel.send(
                    f"{author.mention} Sorry, but the ticket owner has left the server."
                )
                return
            else:
                await channel.set_permissions(
                    TicketOwner,
                    read_messages=True,
                    send_messages=True,
                    reason="Ticket Perms Re-Open (User)",
                )
                await channel.send(
                    f"{author.mention} Alright, the ticket has been re-opened."
                )
                await interaction.message.delete()

        elif InteractionResponse["custom_id"] == "ch_lock_T":
            channel = interaction.channel
            if interaction.guild.id == MAIN_ID.g_main:
                ResponseLogChannel: discord.TextChannel = await self.bot.fetch_channel(
                    MAIN_ID.ch_transcriptLogs
                )
            else:
                ResponseLogChannel: discord.TextChannel = await self.bot.fetch_channel(
                    TECH_ID.ch_ticketLog
                )
            author = interaction.user
            msg = await interaction.channel.send(
                f"Please wait, creating your transcript {Emoji.loadingGIF2}\n**THIS MAY TAKE SOME TIME**"
            )

            msg, file, S3_URL = await TicketExport(
                self, channel, ResponseLogChannel, author, None, True
            )

            if channel.category_id == MAIN_ID.cat_essayTicket:
                raw_url = S3_URL.split("](")[1].strip(")")
                values = self.sheet.col_values(1)

                if raw_url not in values:
                    row = []
                    async for message in channel.history(limit=None):
                        if (
                            f"{message.author} ({message.author.id})" not in row
                            and not message.author.bot
                        ):
                            row.append(f"{message.author} ({message.author.id})")

                    query = (
                        database.TicketInfo.select()
                        .where(database.TicketInfo.ChannelID == interaction.channel_id)
                        .get()
                    )

                    tz = timezone("EST")
                    closed_at_raw = datetime.now(tz)
                    opened_at_raw = query.createdAt

                    opened_at = datetime.strftime(opened_at_raw, "%Y-%m-%d\n%I.%M %p")
                    closed_at = datetime.strftime(closed_at_raw, "%Y-%m-%d\n%I.%M %p")

                    row.insert(0, raw_url)
                    row.insert(1, "")  #
                    row.insert(2, "")  #
                    row.insert(3, "")  # because of connected cells
                    row.insert(4, "")  #
                    row.insert(5, "")  #
                    row.insert(6, opened_at)
                    row.insert(7, closed_at)
                    self.sheet.append_row(row)
                    self.sheet.sort((8, "des"))

            await msg.delete()
            await interaction.channel.send(
                f"{author.mention}\nTranscript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {S3_URL}"
            )

        elif InteractionResponse["custom_id"] == "ch_lock_C&D":
            channel = await self.bot.fetch_channel(interaction.channel_id)
            author = interaction.user
            if interaction.guild.id == MAIN_ID.g_main:
                ResponseLogChannel: discord.TextChannel = await self.bot.fetch_channel(
                    MAIN_ID.ch_transcriptLogs
                )
            else:
                ResponseLogChannel: discord.TextChannel = await self.bot.fetch_channel(
                    TECH_ID.ch_ticketLog
                )
            query = (
                database.TicketInfo.select()
                .where(database.TicketInfo.ChannelID == interaction.channel_id)
                .get()
            )
            msgO = await interaction.channel.send(
                f"{author.mention}\nPlease wait, generating a transcript {Emoji.loadingGIF2}\n**THIS MAY TAKE SOME TIME**"
            )
            TicketOwner = await self.bot.fetch_user(query.authorID)

            messages = await channel.history(limit=None).flatten()
            authorList = []

            for msg in messages:
                if msg.author not in authorList:
                    authorList.append(msg.author)
            print(self, channel, ResponseLogChannel, TicketOwner, authorList)
            msg, transcript_file, url = await TicketExport(
                self, channel, ResponseLogChannel, TicketOwner, authorList
            )
            # S3_upload_file(transcript_file.filename, "ch-transcriptlogs")
            # print(transcript_file.filename)

            if channel.category_id == MAIN_ID.cat_essayTicket:
                raw_url = url.split("](")[1].strip(")")
                values = self.sheet.col_values(1)

                if raw_url not in values:
                    row = []
                    async for message in channel.history(limit=None):
                        if (
                            f"{message.author} ({message.author.id})" not in row
                            and not message.author.bot
                        ):
                            row.append(f"{message.author} ({message.author.id})")

                    tz = timezone("EST")
                    closed_at_raw = datetime.now(tz)
                    opened_at_raw = query.createdAt

                    opened_at = datetime.strftime(opened_at_raw, "%Y-%m-%d\n%I.%M %p")
                    closed_at = datetime.strftime(closed_at_raw, "%Y-%m-%d\n%I.%M %p")

                    row.insert(0, raw_url)
                    row.insert(1, "")  #
                    row.insert(2, "")  #
                    row.insert(3, "")  # because of connected cells
                    row.insert(4, "")  #
                    row.insert(5, "")  #
                    row.insert(6, opened_at)
                    row.insert(7, closed_at)
                    self.sheet.append_row(row)
                    self.sheet.sort((8, "des"))

            try:
                await msgO.edit(
                    f"{author.mention}\nTranscript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {url}"
                )
            except Exception:
                try:
                    await msgO.edit(
                        f"{author.mention}\nTranscript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {url}"
                    )
                except Exception:
                    await msgO.edit(
                        f"{author.mention}\nTranscript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {url}"
                    )
            await asyncio.sleep(5)
            await channel.send(f"{author.mention} Alright, closing ticket.")
            await channel.delete()
            query.delete_instance()

    @commands.command()
    async def close(self, ctx: commands.Context):
        query = database.TicketInfo.select().where(
            database.TicketInfo.ChannelID == ctx.channel.id
        )
        if query.exists():
            query = query.get()
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
                    button_user=ctx.author,
                )
            )
            ButtonViews.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.red,
                    label="Cancel",
                    custom_id="ch_lock_CANCEL",
                    emoji="❌",
                    button_user=ctx.author,
                )
            )
            await ctx.send(f"{ctx.author.mention}\n", embed=embed, view=ButtonViews)
        else:
            await ctx.send("Not a ticket.")

    @tasks.loop(minutes=1.0)
    async def TicketInactive(self):
        TicketInfoTB = database.TicketInfo
        for entry in TicketInfoTB:
            try:
                channel: discord.TextChannel = await self.bot.fetch_channel(
                    entry.ChannelID
                )
            except Exception as e:
                continue
            fetchMessage = await channel.history(limit=1).flatten()
            TicketOwner = await self.bot.fetch_user(entry.authorID)
            messages = await channel.history(limit=None).flatten()
            LogCH = await self.bot.fetch_channel(MAIN_ID.ch_transcriptLogs)
            authorList = []
            if len(messages) == 0:
                continue

            if fetchMessage[0].created_at < (
                datetime.now(pytz.timezone("US/Eastern"))
                - timedelta(minutes=self.TICKET_INACTIVE_TIME)
            ):
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
                        style=discord.ButtonStyle.grey,
                        label="Re-Open Ticket",
                        custom_id="ch_lock_R",
                        emoji="🔓",
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
                overwrite = discord.PermissionOverwrite()
                overwrite.read_messages = False
                print(channel, overwrite)
                await channel.set_permissions(
                    TicketOwner, overwrite=overwrite, reason="Ticket Perms Close (User)"
                )
                await channel.send(
                    f"Ticket has been inactive for 24 hours.\nTicket has been closed.",
                    view=ButtonViews2,
                )

                """for msgI in messages:
                    if msgI.author not in authorList:
                        authorList.append(msgI.author)

                MG, file, S3ink = await TicketExport(
                    self, channel, None, TicketOwner, authorList
                )

                embed = discord.Embed(title="Channel Transcript", color=discord.Colour.green())
                embed.set_author(
                    name=f"{TicketOwner.name}#{TicketOwner.discriminator}",
                    url=TicketOwner.display_avatar.url,
                    icon_url=TicketOwner.display_avatar.url,
                )
                embed.add_field(name="Transcript Owner", value=TicketOwner.mention)
                embed.add_field(name="Ticket Name", value=channel.name, inline=False)
                embed.add_field(name="Category", value=channel.category.name, inline=False)
                embed.add_field(name="Transcript Link", value=S3ink, inline=False)
                embed.set_footer(text="Transcript Attached Above | Ticket was closed due to inactivity")
                await LogCH.send(embed=embed)

                await channel.delete()
                entry.delete_instance()"""

    @commands.command()
    @is_botAdmin
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
            view=TicketButton(self.bot),
        )


def setup(bot):
    bot.add_cog(DropdownTickets(bot))
