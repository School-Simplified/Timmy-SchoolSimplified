from __future__ import annotations

import collections
import json
import os
import subprocess
import traceback
from datetime import datetime
from difflib import get_close_matches
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Union

import discord
import requests
import sentry_sdk
from discord import app_commands
from discord.ext import commands
from fastapi import HTTPException
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel

from core import database
from core.common import (
    ConsoleColors,
    Colors,
    Others,
    MainID,
    TechID,
    CheckDB_CC,
    Emoji, access_secret,
)
from core.gh_modals import FeedbackButton
from core.logging_module import get_log
from utils.bots.TicketSystem.tickets.bot_dev_tickets import CommissionTechButton
from utils.bots.TicketSystem.tickets.web_commissions import CommissionWebButton
from utils.bots.TicketSystem.view_models import (
    create_ui_modal_class,
    create_ticket_button,
    HREmailConfirm,
    MGMCommissionButton,
    EmailDropdown,
    LockButton,
    GSuiteVerify,
    RecruitmentButton,
    create_no_form_button,
)
from utils.events.chat_helper_ticket_sys import TicketButton

if TYPE_CHECKING:
    from main import Timmy

_log = get_log(__name__)


class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(
        label="Verify",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:verify",
        emoji="✅",
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        self.value = True


async def before_invoke_(ctx: commands.Context):
    q = database.CommandAnalytics.create(
        command=ctx.command.name,
        user=ctx.author.id,
        date=datetime.now(),
        command_type="regular",
        guild_id=ctx.guild.id,
    ).save()

    sentry_sdk.set_user(None)
    sentry_sdk.set_user({"id": ctx.author.id, "username": ctx.author.name})
    sentry_sdk.set_tag("username", f"{ctx.author.name}#{ctx.author.discriminator}")
    if ctx.command is None:
        sentry_sdk.set_context(
            "user",
            {
                "name": ctx.author.name,
                "id": ctx.author.id,
                "command": ctx.command,
                "guild": ctx.guild.name,
                "guild_id": ctx.guild.id,
                "channel": ctx.channel.name,
                "channel_id": ctx.channel.id,
            },
        )
    else:
        sentry_sdk.set_context(
            "user",
            {
                "name": ctx.author.name,
                "id": ctx.author.id,
                "command": "Unknown",
                "guild": ctx.guild.name,
                "guild_id": ctx.guild.id,
                "channel": ctx.channel.name,
                "channel_id": ctx.channel.id,
            },
        )


async def on_ready_(bot: Timmy):
    now = datetime.now()
    query: database.CheckInformation = (
        database.CheckInformation.select()
        .where(database.CheckInformation.id == 1)
        .get()
    )

    if not query.PersistantChange:
        bot.add_view(LockButton(bot))
        bot.add_view(VerifyButton())
        bot.add_view(GSuiteVerify())
        bot.add_view(CommissionTechButton(bot))
        bot.add_view(TicketButton(bot))
        bot.add_view(MGMCommissionButton(bot))
        bot.add_view(HREmailConfirm(bot))
        bot.add_view(EmailDropdown(bot))
        bot.add_view(CommissionWebButton(bot))
        bot.add_view(RecruitmentButton(bot))

        ticket_sys = database.TicketConfiguration
        for ticket in ticket_sys:
            ticket: database.TicketConfiguration = ticket
            if ticket.questions != "[]":
                UIModal = create_ui_modal_class(ticket.id)
                modal = UIModal(bot, ticket.title, ticket.questions, ticket.id)

                GlobalSubmitButton = create_ticket_button(ticket.id)
                submit_button = GlobalSubmitButton(modal)
            else:
                no_form_button = create_no_form_button(ticket.id)
                submit_button = no_form_button(ticket.id, bot)
            bot.add_view(view=submit_button)

        query.PersistantChange = True
        query.save()

    if not os.getenv("USEREAL"):
        IP = os.getenv("DATABASE_IP")
        databaseField = f"{ConsoleColors.OKGREEN}Selected Database: External ({IP}){ConsoleColors.ENDC}"
    else:
        databaseField = (
            f"{ConsoleColors.FAIL}Selected Database: localhost{ConsoleColors.ENDC}\n{ConsoleColors.WARNING}WARNING: Not "
            f"recommended to use SQLite.{ConsoleColors.ENDC} "
        )

    try:
        p = subprocess.run(
            "git describe --always",
            shell=True,
            text=True,
            capture_output=True,
            check=True,
        )
        output = p.stdout
    except subprocess.CalledProcessError:
        output = "ERROR"

    # chat_exporter.init_exporter(bot)

    print(
        f"""
            ╭━━┳╮
            ╰╮╭╋╋━━┳━━┳┳╮
            ╱┃┃┃┃┃┃┃┃┃┃┃┃
            ╱╰╯╰┻┻┻┻┻┻╋╮┃
            ╱╱╱╱╱╱╱╱╱╱╰━╯

            Bot Account: {bot.user.name} | {bot.user.id}
            {ConsoleColors.OKCYAN}Discord API Wrapper Version: {discord.__version__}{ConsoleColors.ENDC}
            {ConsoleColors.WARNING}TimmyOS Version: {output}{ConsoleColors.ENDC}
            {databaseField}

            {ConsoleColors.OKCYAN}Current Time: {now}{ConsoleColors.ENDC}
            {ConsoleColors.OKGREEN}Cogs, libraries, and views have successfully been initalized.{ConsoleColors.ENDC}
            ==================================================
            {ConsoleColors.WARNING}Statistics{ConsoleColors.ENDC}

            Guilds: {len(bot.guilds)}
            Members: {len(bot.users)}
            """
    )


async def on_command_error_(bot: Timmy, ctx: commands.Context, error: Exception):
    tb = error.__traceback__
    etype = type(error)
    exception = traceback.format_exception(etype, error, tb, chain=True)
    exception_msg = ""
    for line in exception:
        exception_msg += line

    error = getattr(error, "original", error)
    if ctx.command is not None:
        if ctx.command.name == "rule":
            return "No Rule..."

    if isinstance(error, (commands.CheckFailure, commands.CheckAnyFailure)):
        return

    if hasattr(ctx.command, "on_error"):
        return

    elif isinstance(error, (commands.CommandNotFound, commands.errors.CommandNotFound)):
        cmd = ctx.invoked_with
        cmds = [cmd.name for cmd in bot.commands]
        matches = get_close_matches(cmd, cmds)
        if len(matches) > 0:
            return await ctx.send(
                f'Command "{cmd}" not found, maybe you meant "{matches[0]}"?'
            )
        else:
            """return await ctx.send(
                f'Command "{cmd}" not found, use the help command to know what commands are available. '
                f"Some commands have moved over to slash commands, please check "
                f"https://timmy.schoolsimplified.org/#slash-command-port "
                f"for more updates! "
            )"""
            return await ctx.message.add_reaction("❌")

    elif isinstance(
        error, (commands.MissingRequiredArgument, commands.TooManyArguments)
    ):
        signature = f"{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}"

        if ctx.command.name == "schedule":
            em = discord.Embed(
                title="Missing/Extra Required Arguments Passed In!",
                description=f"Looks like you messed up an argument somewhere here!\n\n**Check the "
                f"following:**\nUsage:\n`{signature}`\n\n-> If you seperated the time and the AM/PM. "
                f"(Eg; "
                f"5:00 PM)\n-> If you provided a valid student's ID\n-> If you followed the MM/DD "
                f"Format.\n-> Keep all the arguments in one word.\n-> If you followed the ["
                f"documentation "
                f"for schedule.](https://timmy.schoolsimplified.org/tutorbot#schedule)",
                color=Colors.red,
            )
            em.set_thumbnail(url=Others.error_png)
            em.set_footer(
                text="Consult the Help Command if you are having trouble or call over a Bot Manager!"
            )
            return await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Missing/Extra Required Arguments Passed In!",
                description="You have missed one or several arguments in this command"
                "\n\nUsage:"
                f"\n`{signature}`",
                color=Colors.red,
            )
            em.set_thumbnail(url=Others.error_png)
            em.set_footer(
                text="Consult the Help Command if you are having trouble or call over a Bot Manager!"
            )
            return await ctx.send(embed=em)

    elif isinstance(
        error,
        (
            commands.MissingAnyRole,
            commands.MissingRole,
            commands.MissingPermissions,
            commands.errors.MissingAnyRole,
            commands.errors.MissingRole,
            commands.errors.MissingPermissions,
        ),
    ):
        em = discord.Embed(
            title="Invalid Permissions!",
            description="You do not have the associated role in order to successfully invoke this command! "
            "Contact an administrator/developer if you believe this is invalid.",
            color=Colors.red,
        )
        em.set_thumbnail(url=Others.error_png)
        em.set_footer(
            text="Consult the Help Command if you are having trouble or call over a Bot Manager!"
        )
        await ctx.send(embed=em)
        return

    elif isinstance(
        error,
        (commands.BadArgument, commands.BadLiteralArgument, commands.BadUnionArgument),
    ):
        signature = f"{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}"
        if ctx.command.name == "schedule":
            em = discord.Embed(
                title="Bad Argument!",
                description=f"Looks like you messed up an argument somewhere here!\n\n**Check the "
                f"following:**\nUsage:\n`{signature}`\n-> If you seperated the time and the AM/PM. (Eg; "
                f"5:00 PM)\n-> If you provided a valid student's ID\n-> If you followed the MM/DD "
                f"Format.\n-> Keep all the arguments in one word.\n-> If you followed the [documentation "
                f"for schedule.](https://timmy.schoolsimplified.org/tutorbot#schedule)",
                color=Colors.red,
            )
            em.set_thumbnail(url=Others.error_png)
            em.set_footer(
                text="Consult the Help Command if you are having trouble or call over a Bot Manager!"
            )
            return await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Bad Argument!",
                description=f"Unable to parse arguments, check what arguments you provided."
                f"\n\nUsage:\n`{signature}`",
                color=Colors.red,
            )
            em.set_thumbnail(url=Others.error_png)
            em.set_footer(
                text="Consult the Help Command if you are having trouble or call over a Bot Manager!"
            )
            return await ctx.send(embed=em)

    elif isinstance(
        error, (commands.CommandOnCooldown, commands.errors.CommandOnCooldown)
    ):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)

        msg = "This command cannot be used again for {} minutes and {} seconds".format(
            round(m), round(s)
        )

        embed = discord.Embed(
            title="Command On Cooldown", description=msg, color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    else:
        error_file = Path("error.txt")
        error_file.touch()
        with error_file.open("w") as f:
            f.write(exception_msg)
        with error_file.open("r") as f:
            # config, _ = core.common.load_config()
            data = "\n".join([l.strip() for l in f])

            GITHUB_API = "https://api.github.com"
            API_TOKEN = os.getenv("GITHUB")
            url = GITHUB_API + "/gists"
            headers = {"Authorization": "token %s" % API_TOKEN}
            params = {"scope": "gist"}
            payload = {
                "description": "Timmy encountered a Traceback!",
                "public": True,
                "files": {"error": {"content": f"{data}"}},
            }
            res = requests.post(
                url, headers=headers, params=params, data=json.dumps(payload)
            )
            j = json.loads(res.text)
            ID = j["id"]
            gisturl = f"https://gist.github.com/{ID}"
            _log.info(f"Gist URL: {gisturl}")

            permitlist = []
            query = database.Administrators.select().where(
                database.Administrators.TierLevel >= 3
            )
            for user in query:
                permitlist.append(user.discordID)

            if ctx.author.id not in permitlist:
                embed = discord.Embed(
                    title="Error Detected!",
                    description="Seems like I've ran into an unexpected error!",
                    color=Colors.red,
                )
                embed.set_thumbnail(url=Others.timmy_dog_png)
                embed.set_footer(text=f"Error: {str(error)}")
                await ctx.send(embed=embed)

                view = FeedbackButton(bot=bot, gist_url=gisturl)
                await ctx.send(
                    "Want to help even more? Click here to submit feedback!", view=view
                )
            else:
                embed = discord.Embed(
                    title="Traceback Detected!",
                    description="Timmy here has ran into an error!\nTraceback has been attached below.",
                    color=Colors.red,
                )
                embed.add_field(name="GIST URL", value=gisturl)
                embed.set_thumbnail(url=Others.timmy_dog_png)
                embed.set_footer(text=f"Error: {str(error)}")
                await ctx.send(embed=embed)

            guild = bot.get_guild(Me.TechGuild)
            channel = guild.get_channel(Me.TracebackChannel)

            embed2 = discord.Embed(
                title="Traceback Detected!",
                description=f"**Information**\n"
                f"**Server:** {ctx.message.guild.name}\n"
                f"**User:** {ctx.message.author.mention}\n"
                f"**Command:** {ctx.command.name}",
                color=Colors.red,
            )
            embed2.add_field(
                name="Gist URL",
                value=f"[Uploaded Traceback to GIST](https://gist.github.com/{ID})",
            )
            await channel.send(embed=embed2)
            error_file.unlink()

    raise error


async def on_app_command_error_(
    bot: Timmy,
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
):
    tb = error.__traceback__
    etype = type(error)
    exception = traceback.format_exception(etype, error, tb, chain=True)
    exception_msg = ""
    for line in exception:
        exception_msg += line

    if isinstance(error, app_commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)

        msg = "This command cannot be used again for {} minutes and {} seconds".format(
            round(m), round(s)
        )

        embed = discord.Embed(
            title="Command On Cooldown", description=msg, color=discord.Color.red()
        )
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    elif isinstance(error, app_commands.CheckFailure):
        if interaction.response.is_done():
            await interaction.followup.send(
                "You cannot run this command!", ephemeral=True
            )
        await interaction.response.send_message(
            "You cannot run this command!", ephemeral=True
        )

    elif isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message(
            f"Command /{interaction.command.name} not found."
        )

    else:
        error_file = Path("error.txt")
        error_file.touch()
        with error_file.open("w") as f:
            f.write(exception_msg)
        with error_file.open("r") as f:
            # config, _ = core.common.load_config()
            data = "\n".join([l.strip() for l in f])

            GITHUB_API = "https://api.github.com"
            API_TOKEN = os.getenv("GITHUB")
            url = GITHUB_API + "/gists"
            headers = {"Authorization": "token %s" % API_TOKEN}
            params = {"scope": "gist"}
            payload = {
                "description": "Timmy encountered a Traceback!",
                "public": True,
                "files": {"error": {"content": f"{data}"}},
            }
            res = requests.post(
                url, headers=headers, params=params, data=json.dumps(payload)
            )
            j = json.loads(res.text)
            ID = j["id"]
            gisturl = f"https://gist.github.com/{ID}"

            permitlist = []
            query = database.Administrators.select().where(
                database.Administrators.TierLevel >= 3
            )
            for user in query:
                permitlist.append(user.discordID)

            if interaction.user.id not in permitlist:
                embed = discord.Embed(
                    title="Error Detected!",
                    description="Seems like I've ran into an unexpected error!",
                    color=discord.Color.brand_red(),
                )
                embed.add_field(
                    name="Error Message",
                    value="I've contacted the IT Department and they have been notified, meanwhile, please double "
                    "check the command you've sent for any issues.\n "
                    "Consult the help command for more information.",
                )
                embed.set_thumbnail(url=Others.timmy_dog_png)
                embed.set_footer(text="Submit a bug report or feedback below!")
                if interaction.response.is_done():
                    await interaction.followup.send(
                        embed=embed, view=FeedbackButton(bot=bot, gist_url=gisturl)
                    )
                else:
                    await interaction.response.send_message(
                        embed=embed, view=FeedbackButton(bot=bot, gist_url=gisturl)
                    )
            else:
                embed = discord.Embed(
                    title="Traceback Detected!",
                    description="Timmy here has ran into an error!\nTraceback has been attached below.",
                    color=Colors.red,
                )
                embed.add_field(name="GIST URL", value=gisturl)
                embed.set_thumbnail(url=Others.timmy_dog_png)
                embed.set_footer(text=f"Error: {str(error)}")
                if interaction.response.is_done():
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.response.send_message(embed=embed)

            guild = bot.get_guild(Me.TechGuild)
            channel = guild.get_channel(Me.TracebackChannel)

            embed2 = discord.Embed(
                title="Traceback Detected!",
                description=f"**Information**\n"
                f"**Server:** {interaction.guild.name}\n"
                f"**User:** {interaction.user.mention}\n"
                f"**Command:** {interaction.command.name}",
                color=Colors.red,
            )
            embed2.add_field(
                name="Gist URL",
                value=f"[Uploaded Traceback to GIST](https://gist.github.com/{ID})",
            )
            await channel.send(embed=embed2)

            view = FeedbackButton(bot=bot, gist_url=gisturl)
            try:
                error_file.unlink()
                await interaction.followup.send(
                    "Want to help even more? Click here to submit feedback!", view=view
                )
            except:
                await interaction.channel.send(
                    "Want to help even more? Click here to submit feedback!", view=view
                )

    raise error


async def on_command_(bot: Timmy, ctx: commands.Context):
    if ctx.command.name in ["sync", "ping", "kill", "jsk", "py"]:
        return

    await ctx.reply(
        f":x: This command usage is deprecated. Use the equivalent slash command by using `/{ctx.command.name}` instead."
    )


class Me:
    publicCH = [
        MainID.cat_casual,
        MainID.cat_community,
        MainID.cat_lounge,
        MainID.cat_events,
        MainID.cat_voice,
    ]
    TechGuild = TechID.g_tech
    TracebackChannel = TechID.ch_tracebacks


async def main_mode_check_(ctx: commands.Context) -> bool:
    """MT = discord.utils.get(ctx.guild.roles, name="Moderator")
    VP = discord.utils.get(ctx.guild.roles, name="VP")
    CO = discord.utils.get(ctx.guild.roles, name="CO")
    SS = discord.utils.get(ctx.guild.roles, name="Secret Service")"""

    blacklisted_users = []
    db_blacklist: collections.Iterable = database.Blacklist
    for p in db_blacklist:
        blacklisted_users.append(p.discordID)

    adminIDs = []
    query = database.Administrators.select().where(
        database.Administrators.TierLevel == 4
    )
    for admin in query:
        adminIDs.append(admin.discordID)

    # Permit 4 Check
    if ctx.author.id in adminIDs:
        return True

    # Maintenance Check
    elif CheckDB_CC.MasterMaintenance:
        embed = discord.Embed(
            title="Master Maintenance ENABLED",
            description=f"{Emoji.deny} The bot is currently unavailable as it is under maintenance, check back later!",
            color=discord.Colour.gold(),
        )
        embed.set_footer(
            text="Need an immediate unlock? Message a Developer or SpaceTurtle#0001"
        )
        await ctx.send(embed=embed)

        return False

    # Blacklist Check
    elif ctx.author.id in blacklisted_users:
        return False

    # DM Check
    elif ctx.guild is None:
        return CheckDB_CC.guild_None

    # External Server Check
    elif ctx.guild.id != MainID.g_main:
        return CheckDB_CC.external_guild

    # Rule Command Check
    elif ctx.command.name == "rule":
        return CheckDB_CC.rule_bypass

    # Public Category Check
    elif ctx.channel.category_id in Me.publicCH:
        return CheckDB_CC.public_categories

    # Else...
    else:
        return CheckDB_CC.else_situation


def initializeDB(bot):
    """
    Initializes the database, and creates the needed table data if they don't exist.
    """
    database.db.connect(reuse_if_open=True)
    CIQ = database.CheckInformation.select().where(database.CheckInformation.id == 1)
    BTE = database.BaseTickerInfo.select().where(database.BaseTickerInfo.id == 1)
    SM = database.SandboxConfig.select().where(database.SandboxConfig.id == 1)

    if not CIQ.exists():
        database.CheckInformation.create(
            MasterMaintenance=False,
            guildNone=False,
            externalGuild=True,
            ModRoleBypass=True,
            ruleBypass=True,
            publicCategories=True,
            elseSituation=True,
            PersistantChange=False,
        )
        _log.info("Created CheckInformation Entry.")

    if len(database.Administrators) == 0:
        for person in bot.owner_ids:
            database.Administrators.create(discordID=person, TierLevel=4)
            _log.info("Created Administrator Entry.")
        database.Administrators.create(discordID=409152798609899530, TierLevel=4)

    query: database.CheckInformation = (
        database.CheckInformation.select()
        .where(database.CheckInformation.id == 1)
        .get()
    )
    query.PersistantChange = False
    query.save()
    database.db.close()

"""
# API Routes Below
"""

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.orgunit",
    "https://www.googleapis.com/auth/admin.directory.userschema",
]
orgUnit = {
    "Personal Account": "/School Simplified Personal Acc.",
    "Team Account": "/School Simplified Team Acc.",
}

creds = access_secret("adm_t", True, 0, SCOPES)
service = build("admin", "directory_v1", credentials=creds)

class JSONPayload(BaseModel):
    action: str
    custom_id: str
    description: str
    return_post: Union[str, None] = None
    payload: str


def authenticate_user(token: str):
    # ODO: add more security later
    query = database.APIRouteTable.select().where(database.APIRouteTable.hashed_password == token)
    if query.exists():
        return query.get()
    return None


def create_gsuite(payload: JSONPayload):
    """
    Example payload:
    {
        "action": "gsuite",
        "description": "breadcrums",

        "payload": {
            "name": {
                "givenName": firstname,
                "fullName": firstname + " " + lastname,
                "familyName": lastname,
            },
            "password": temppass,
            "primaryEmail": f"{firstname}.{lastname}@schoolsimplified.org",
            "changePasswordAtNextLogin": True,
            "orgUnitPath": orgUnit[organization_unit],
        }
    }
    """
    try:
        user = dict(payload.payload)
        service.users().insert(body=user).execute()
    except HttpError as e:
        """If the error code is 409, send a message to the user saying that the email is already taken."""
        if e.status_code == 409:
            raise HTTPException(
                status_code=409, detail=f"The email {user['primaryEmail']} is already taken."
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"API Error: {e}"
            )
    except TypeError:
        raise HTTPException(
            status_code=422, detail=f"The payload is not in the correct format. (Unprocessable Entity)"
        )


