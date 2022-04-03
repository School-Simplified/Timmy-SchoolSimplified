import collections
import json
import os
import subprocess
import time
import traceback
from datetime import datetime
from difflib import get_close_matches
from typing import Union

import discord
from discord import app_commands
from discord.ext import commands
import sentry_sdk
import requests
from core import database
from core.common import (
    bcolors,
    FeedbackButton,
    GSuiteVerify,
    Colors,
    LockButton,
    Others,
    MAIN_ID,
    TECH_ID,
    CheckDB_CC,
    Emoji,
)
from utils.events.TicketDropdown import TicketButton
from utils.bots.CoreBot.cogs.techCommissions import CommissionTechButton
from pathlib import Path

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
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button,):
        self.value = True

async def before_invoke_(ctx: commands.Context):
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


async def on_ready_(bot: commands.Bot):
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
        query.PersistantChange = True
        query.save()

    if not os.getenv("USEREAL"):
        IP = os.getenv("IP")
        databaseField = (
            f"{bcolors.OKGREEN}Selected Database: External ({IP}){bcolors.ENDC}"
        )
    else:
        databaseField = (
            f"{bcolors.FAIL}Selected Database: localhost{bcolors.ENDC}\n{bcolors.WARNING}WARNING: Not "
            f"recommended to use SQLite.{bcolors.ENDC} "
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
            {bcolors.OKCYAN}Discord API Wrapper Version: {discord.__version__}{bcolors.ENDC}
            {bcolors.WARNING}TimmyOS Version: {output}{bcolors.ENDC}
            {databaseField}

            {bcolors.OKCYAN}Current Time: {now}{bcolors.ENDC}
            {bcolors.OKGREEN}Cogs, libraries, and views have successfully been initalized.{bcolors.ENDC}
            ==================================================
            {bcolors.WARNING}Statistics{bcolors.ENDC}

            Guilds: {len(bot.guilds)}
            Members: {len(bot.users)}
            """
    )


async def on_command_error_(bot: commands.Bot, ctx: commands.Context, error: Exception):
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
            return await ctx.send(
                f'Command "{cmd}" not found, use the help command to know what commands are available. '
                f"Some commands have moved over to slash commands, please check "
                f"https://timmy.schoolsimplified.org/#slash-command-port "
                f"for more updates! "
            )

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

    elif isinstance(error, (commands.BadArgument, commands.BadLiteralArgument, commands.BadUnionArgument)):
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
            API_TOKEN = os.getenv("GIST")
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
            print(gisturl)

            permitlist = []
            query = database.Administrators.select().where(
                database.Administrators.TierLevel >= 3
            )
            for user in query:
                permitlist.append(user.discordID)

            if ctx.author.id not in permitlist:
                embed = discord.Embed(
                    title="Traceback Detected!",
                    description="Timmy here has ran into an error!\nPlease check what you sent and/or check out "
                                "the "
                                "help command!",
                    color=Colors.red,
                )
                embed.set_thumbnail(url=Others.timmyDog_png)
                embed.set_footer(text=f"Error: {str(error)}")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Traceback Detected!",
                    description="Timmy here has ran into an error!\nTraceback has been attached below.",
                    color=Colors.red,
                )
                embed.add_field(name="GIST URL", value=gisturl)
                embed.set_thumbnail(url=Others.timmyDog_png)
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

            view = FeedbackButton()
            await ctx.send(
                "Want to help even more? Click here to submit feedback!", view=view
            )
            error_file.unlink()

    raise error


async def on_app_command_error(bot:commands.Bot,
                               interaction: discord.Interaction,
                               command: Union[app_commands.Command, app_commands.ContextMenu],
                               error: app_commands.AppCommandError
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
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    else:
        error_file = Path("error.txt")
        error_file.touch()
        with error_file.open("w") as f:
            f.write(exception_msg)
        with error_file.open("r") as f:
            # config, _ = core.common.load_config()
            data = "\n".join([l.strip() for l in f])

            GITHUB_API = "https://api.github.com"
            API_TOKEN = os.getenv("GIST")
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
                    title="Traceback Detected!",
                    description="Timmy here has ran into an error!\nPlease check what you sent and/or check out "
                                "the "
                                "help command!",
                    color=Colors.red,
                )
                embed.set_thumbnail(url=Others.timmyDog_png)
                embed.set_footer(text=f"Error: {str(error)}")
                await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(
                    title="Traceback Detected!",
                    description="Timmy here has ran into an error!\nTraceback has been attached below.",
                    color=Colors.red,
                )
                embed.add_field(name="GIST URL", value=gisturl)
                embed.set_thumbnail(url=Others.timmyDog_png)
                embed.set_footer(text=f"Error: {str(error)}")
                await interaction.response.send_message(embed=embed)

            guild = bot.get_guild(Me.TechGuild)
            channel = guild.get_channel(Me.TracebackChannel)

            embed2 = discord.Embed(
                title="Traceback Detected!",
                description=f"**Information**\n"
                            f"**Server:** {interaction.message.guild.name}\n"
                            f"**User:** {interaction.message.author.mention}\n"
                            f"**Command:** {interaction.command.name}",
                color=Colors.red,
            )
            embed2.add_field(
                name="Gist URL",
                value=f"[Uploaded Traceback to GIST](https://gist.github.com/{ID})",
            )
            await channel.send(embed=embed2)

            view = FeedbackButton()
            await interaction.response.send_message(
                "Want to help even more? Click here to submit feedback!", view=view
            )
            error_file.unlink()

    raise error


class Me:
    publicCH = [
        MAIN_ID.cat_casual,
        MAIN_ID.cat_community,
        MAIN_ID.cat_lounge,
        MAIN_ID.cat_events,
        MAIN_ID.cat_voice,
    ]
    TechGuild = TECH_ID.g_tech
    TracebackChannel = TECH_ID.ch_tracebacks


async def main_mode_check_(ctx: commands.Context):
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
        return CheckDB_CC.guildNone

    # External Server Check
    elif ctx.guild.id != MAIN_ID.g_main:
        return CheckDB_CC.externalGuild

    # Rule Command Check
    elif ctx.command.name == "rule":
        return CheckDB_CC.ruleBypass

    # Public Category Check
    elif ctx.channel.category_id in Me.publicCH:
        return CheckDB_CC.publicCategories

    # Else...
    else:
        return CheckDB_CC.elseSituation

def initializeDB(bot):
    """
    Initializes the database, and creates the needed table data if they don't exist.
    """
    database.db.connect(reuse_if_open=True)
    UpQ = database.Uptime.select().where(database.Uptime.id == 1)
    CIQ = database.CheckInformation.select().where(database.CheckInformation.id == 1)
    BTE = database.BaseTickerInfo.select().where(database.BaseTickerInfo.id == 1)
    SM = database.SandboxConfig.select().where(database.SandboxConfig.id == 1)

    if not UpQ.exists():
        database.Uptime.create(UpStart="1")
        print("Created Uptime Entry.")

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
        print("Created CheckInformation Entry.")

    if len(database.Administrators) == 0:
        for person in bot.owner_ids:
            database.Administrators.create(discordID=person, TierLevel=4)
            print("Created Administrator Entry.")
        database.Administrators.create(discordID=409152798609899530, TierLevel=4)

    if not BTE.exists():
        database.BaseTickerInfo.create(
            counter=0,
        )
        print("Created BaseTickerInfo Entry.")

    if not SM.exists():
        database.SandboxConfig.create(
            mode="None",
        )
        print("Created SandboxConfig Entry.")

    q: database.Uptime = database.Uptime.select().where(database.Uptime.id == 1).get()
    q.UpStart = time.time()
    q.save()

    query: database.CheckInformation = (
        database.CheckInformation.select().where(database.CheckInformation.id == 1).get()
    )
    query.PersistantChange = False
    query.save()
    database.db.close()
