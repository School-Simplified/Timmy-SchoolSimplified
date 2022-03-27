"""
Copyright (C) School Simplified - All Rights Reserved
 * Permission is granted to use this application as a code reference for educational purposes.
 * Written by School Simplified, IT Dept. <timmy@schoolsimplified.org>, March 2022
"""

__version__ = "3.0.0"
__author__ = "School Simplified, IT Dept."
__author_email__ = "timmy@schoolsimplified.org"

import faulthandler
import logging
import os
from typing import Optional, Union

import discord
from alive_progress import alive_bar
from discord import app_commands
from discord.ext import commands
from discord_sentry_reporting import use_sentry
from dotenv import load_dotenv
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from core import database
from core.common import (
    MAIN_ID,
    TECH_ID,
    CheckDB_CC,
    Emoji,
    FeedbackButton,
    GSuiteVerify,
    LockButton,
    Others,
    bcolors,
    get_extensions,
    hexColors,
    deprecatedFiles,
)

load_dotenv()
faulthandler.enable()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

logger.warning("Started Timmy")
print("Starting Timmy...")


class TimmyCommandTree(app_commands.CommandTree):
    def __init__(self, client: commands.Bot):
        super().__init__(client)

#     async def on_error(
#             self,
#             interaction: discord.Interaction,
#             command: Optional[Union[app_commands.ContextMenu, app_commands.Command]],
#             error: app_commands.AppCommandError,
#     ) -> None:
#         ...

    # Implement error system

    # async def interaction_check(
    #         self,
    #         interaction: discord.Interaction,
    #         /
    # ) -> bool:
    #     ...
    #  Implement blacklist check for spammers


class Timmy(commands.Bot):
    """
    Generates a Timmy Instance.
    """

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=commands.when_mentioned_or(os.getenv("PREFIX")),
            intents=intents,
            case_insensitive=True,
            tree_cls=TimmyCommandTree,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="+help | timmy.schoolsimplified.org",
            ),
        )
        self.help_command = None

    async def on_ready(self):
        return await on_ready_(self)

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        return await on_command_error_(self, ctx, error)

    async def before_invoke(self, ctx: commands.Context):
        return await before_invoke_(ctx)

    async def check(self, ctx: commands.Context):
        return await main_mode_check_(ctx)

    async def setup_hook(self) -> None:
        for guild in self.guilds:
            await self.tree.sync(guild=guild)

        with alive_bar(len(get_extensions()), ctrl_c=False, bar="bubbles", title="Initializing Cogs:") as bar:
            for ext in get_extensions():
                try:
                    await bot.load_extension(ext)
                except commands.ExtensionAlreadyLoaded:
                    await bot.unload_extension(ext)
                    await bot.load_extension(ext)
                except commands.ExtensionNotFound:
                    raise commands.ExtensionNotFound(ext)
                bar()

    async def is_owner(self, user: discord.User):
        admin_ids = []
        query = database.Administrators.select().where(
            database.Administrators.TierLevel >= 3
        )
        for admin in query:
            admin_ids.append(admin.discordID)

        if user.id in admin_ids:
            return True

        return await super().is_owner(user)


bot = Timmy()


if os.getenv("DSN_SENTRY") is not None:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )

    use_sentry(
        bot,  # Traceback tracking, DO NOT MODIFY THIS
        dsn=os.getenv("DSN_SENTRY"),
        traces_sample_rate=1.0,
        integrations=[FlaskIntegration(), sentry_logging],
    )

# Start Check
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

database.db.connect(reuse_if_open=True)
q: database.Uptime = database.Uptime.select().where(database.Uptime.id == 1).get()
q.UpStart = time.time()
q.save()

query: database.CheckInformation = (
    database.CheckInformation.select().where(database.CheckInformation.id == 1).get()
)
query.PersistantChange = False
query.save()
database.db.close()

for deprecationFile in deprecatedFiles:
    if os.path.exists("gsheetsadmin/{}".format(deprecationFile)):
        print(f"{bcolors.WARNING}Authentication via {deprecationFile} is deprecated. Consider removing this file and using sstimmy.json instead.{bcolors.ENDC}")



@bot.slash_command(description="Play a game of TicTacToe with someone!")
async def tictactoe(ctx, user: Option(discord.Member, "Enter an opponent you want")):
    if ctx.channel.id != MAIN_ID.ch_commands:
        return await ctx.respond(
            f"{ctx.author.mention}\nMove to <#{MAIN_ID.ch_commands}> to play Tic Tac Toe!",
            ephemeral=True,
        )
    if user is None:
        return await ctx.respond(
            "lonely :(, sorry but you need a person to play against!"
        )
    elif user == bot.user:
        return await ctx.respond("i'm good.")
    elif user == ctx.author:
        return await ctx.respond(
            "lonely :(, sorry but you need an actual person to play against, not yourself!"
        )

    await ctx.respond(
        f"Tic Tac Toe: {ctx.author.mention} goes first",
        view=TicTacToe(ctx.author, user),
    )


@bot.user_command(name="Are they short?")
async def short(ctx, member: discord.Member):
    if random.randint(0, 1) == 1:
        await ctx.respond(f"{member.mention} is short!")
    else:
        await ctx.respond(f"{member.mention} is tall!")


@bot.slash_command(description="Check's if a user is short!")
async def short_detector(
    ctx, member: Option(discord.Member, "Enter a user you want to check!")
):
    if random.randint(0, 1) == 1:
        await ctx.respond(f"{member.mention} is short!")
    else:
        await ctx.respond(f"{member.mention} is tall!")


@bot.user_command(name="Play TicTacToe with them!")
async def tictactoeCTX(ctx, member: discord.Member):
    if member is None:
        return await ctx.respond(
            "lonely :(, sorry but you need a person to play against!"
        )
    elif member == bot.user:
        return await ctx.respond("i'm good.")
    elif member == ctx.author:
        return await ctx.respond(
            "lonely :(, sorry but you need an actual person to play against, not yourself!"
        )

    await ctx.respond(
        f"Tic Tac Toe: {ctx.author.mention} goes first",
        view=TicTacToe(ctx.author, member),
    )


with alive_bar(
    len(get_extensions()), ctrl_c=False, bar="bubbles", title=f"Initializing Cogs:"
) as bar:
    for ext in get_extensions():
        #start = time.time()
        try:
            bot.load_extension(ext)
        except discord.ExtensionAlreadyLoaded:
            bot.unload_extension(ext)
            bot.load_extension(ext)
        except discord.ExtensionNotFound:
            raise discord.ExtensionNotFound(ext)
        #end = time.time()
        #print(f"{ext} loaded in {end - start:.2f} seconds")
        bar()


@bot.check
async def mainModeCheck(ctx: commands.Context):
    """MT = discord.utils.get(ctx.guild.roles, name="Moderator")
    VP = discord.utils.get(ctx.guild.roles, name="VP")
    CO = discord.utils.get(ctx.guild.roles, name="CO")
    SS = discord.utils.get(ctx.guild.roles, name=844013914609680384)"""

    blacklistedUsers = []
    for p in database.Blacklist:
        blacklistedUsers.append(p.discordID)

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
    elif ctx.author.id in blacklistedUsers:
        return False

    # DM Check
    elif ctx.guild is None:
        return True
        # return CheckDB_CC.guildNone

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


bot.run(os.getenv("TOKEN"))
