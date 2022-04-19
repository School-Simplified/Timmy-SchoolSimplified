"""
Copyright (C) School Simplified - All Rights Reserved
 * Permission is granted to use this application as a code reference for educational purposes.
 * Written by School Simplified, IT Dept. <timmy@schoolsimplified.org>, March 2022
"""

__version__ = "beta3.0.2"
__author__ = "School Simplified, IT Dept."
__author_email__ = "timmy@schoolsimplified.org"

import faulthandler
import logging
import os
from typing import Union

from alive_progress import alive_bar
import discord
from discord import app_commands
from discord.ext import commands
from discord_sentry_reporting import use_sentry
from dotenv import load_dotenv
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from core import database
from core.common import get_extensions
from core.special_methods import (before_invoke_, initializeDB,
                                  main_mode_check_, on_app_command_error_,
                                  on_command_error_, on_ready_)


load_dotenv()
faulthandler.enable()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

logger.warning("Started Timmy")
print("Starting Timmy...")


class TimmyCommandTree(app_commands.CommandTree):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        blacklisted_users = [p.discordID for p in database.Blacklist]
        if interaction.user.id in blacklisted_users:
            await interaction.response.send_message("You have been blacklisted from using commands!",
                                                    ephemeral=True)
            return False
        return True

    async def on_error(self,
                       interaction: discord.Interaction,
                       command: Union[app_commands.Command, app_commands.ContextMenu],
                       error: app_commands.AppCommandError):
        await on_app_command_error_(self.bot, interaction, command, error)


class Timmy(commands.Bot):
    """
    Generates a Timmy Instance.
    """

    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(os.getenv("PREFIX")),
                         intents=discord.Intents.all(),
                         case_insensitive=True,
                         tree_cls=TimmyCommandTree,
                         activity=discord.Activity(
                             type=discord.ActivityType.watching,
                             name="/help | ssimpl.org/timmy"))
        self.help_command = None

    async def on_ready(self):
        await on_ready_(self)

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        await on_command_error_(self, ctx, error)

    async def before_invoke(self, ctx: commands.Context):
        await before_invoke_(ctx)

    async def check(self, ctx: commands.Context):
        await main_mode_check_(ctx)

    async def setup_hook(self) -> None:
        with alive_bar(len(get_extensions()),
                       ctrl_c=False,
                       bar="bubbles",
                       title="Initializing Cogs:") as bar:
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
        query = database.Administrators.select().where(database.Administrators.TierLevel >= 3)
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
    sentry_logging = LoggingIntegration(level=logging.INFO,         # Capture info and above as breadcrumbs
                                        event_level=logging.ERROR   # Send errors as events
                                        )

    # Traceback tracking, DO NOT MODIFY THIS
    use_sentry(bot,
               dsn=os.getenv("DSN_SENTRY"),
               traces_sample_rate=1.0,
               integrations=[FlaskIntegration(), sentry_logging])

initializeDB(bot)
bot.run(os.getenv("TOKEN"))
