"""
Copyright (C) School Simplified - All Rights Reserved
 * Permission is granted to use this application as a code reference for educational purposes.
 * Written by School Simplified, IT Dept. <timmy@schoolsimplified.org>, March 2022
"""

__version__ = "beta3.0.1"
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
from core.common import get_extensions
from core.special_methods import (
    before_invoke_,
    initializeDB,
    main_mode_check_,
    on_command_error_,
    on_ready_,
    on_app_command_error_
)

load_dotenv()
faulthandler.enable()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

logger.warning("Started Timmy")
print("Starting Timmy...")


class TimmyCommandTree(app_commands.CommandTree):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.bot = bot

    async def on_error(
            self,
            interaction: discord.Interaction,
            command: Union[app_commands.Command, app_commands.ContextMenu],
            error: app_commands.AppCommandError
    ):
        return await on_app_command_error_(self.bot, interaction, command, error)


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
                name="/help | ssimpl.org/timmy",
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
        # for guild in self.guilds:
        #     await self.tree.sync(guild=guild)

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

    @property
    def version(self):
        return __version__


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

initializeDB(bot)

bot.run(os.getenv("TOKEN"))