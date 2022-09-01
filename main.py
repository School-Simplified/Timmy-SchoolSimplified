"""
Copyright (C) School Simplified - All Rights Reserved
 * Permission is granted to use this application as a code reference for educational purposes.
 * Written by School Simplified, IT Dept. <timmy@schoolsimplified.org>, March 2022
"""

__version__ = "beta4.1.1"
__author__ = "School Simplified, IT Dept."
__author_email__ = "timmy@schoolsimplified.org"

import asyncio
import faulthandler
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Union

import discord
import uvicorn
from alive_progress import alive_bar
from discord import app_commands
from discord.ext import commands
from discord_sentry_reporting import use_sentry
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status, Header
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
# from googletrans import Translator
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from core import database
from core.common import get_extensions
from core.logging_module import get_log
from core.special_methods import (
    before_invoke_,
    initializeDB,
    main_mode_check_,
    on_app_command_error_,
    on_command_error_,
    on_ready_,
    on_command_, authenticate_user, JSONPayload, create_gsuite,
)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

load_dotenv()
faulthandler.enable()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

_log = get_log(__name__)
_log.info("Starting Timmy...")


"""class TimmyTranslator(app_commands.Translator):
    async def load(self) -> None:
        _log.info('Translator loaded')

    async def unload(self) -> None:
        _log.info('Translator unloaded')

    async def translate(self, string: app_commands.locale_str, locale: discord.Locale, context: app_commands.TranslationContext):
        translator = Translator()
        locale = str(locale)
        #reg_local = None
        if "-" in locale:
            #locale = locale.split("-")[1]
            locale = locale.split("-")[0]
        _log.info(locale)

        try:
            translated_text = translator.translate(string, dest=locale).text
        except Exception as e:
            return None
        return translated_text"""


class TimmyCommandTree(app_commands.CommandTree):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        blacklisted_users = [p.discordID for p in database.Blacklist]
        if interaction.user.avatar is None:
            await interaction.response.send_message("Due to a discord limitation, you must have an avatar set to use this command.")
            return False
        if interaction.user.id in blacklisted_users:
            await interaction.response.send_message(
                "You have been blacklisted from using commands!", ephemeral=True
            )
            return False
        return True

    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        await on_app_command_error_(self.bot, interaction, error)


class Timmy(commands.Bot):
    """
    Generates a Timmy Instance.
    """

    def __init__(self, uptime: time.time):
        super().__init__(
            command_prefix=commands.when_mentioned_or(os.getenv("PREFIX")),
            intents=discord.Intents.all(),
            case_insensitive=True,
            tree_cls=TimmyCommandTree,
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="/help | ssimpl.org/timmy"
            ),
        )
        self.help_command = None
        self.before_invoke(self.analytics_before_invoke)
        self.add_check(self.check)
        self._start_time = uptime

    async def on_ready(self):
        await on_ready_(self)

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        await on_command_error_(self, ctx, error)

    async def on_command(self, ctx: commands.Context):
        await on_command_(self, ctx)

    async def analytics_before_invoke(self, ctx: commands.Context):
        await before_invoke_(ctx)

    async def check(self, ctx: commands.Context):
        return await main_mode_check_(ctx)

    async def setup_hook(self) -> None:
        with alive_bar(
            len(get_extensions()),
            ctrl_c=False,
            bar="bubbles",
            title="Initializing Cogs:",
        ) as bar:

            for ext in get_extensions():
                try:
                    await bot.load_extension(ext)
                except commands.ExtensionAlreadyLoaded:
                    await bot.unload_extension(ext)
                    await bot.load_extension(ext)
                except commands.ExtensionNotFound:
                    raise commands.ExtensionNotFound(ext)
                bar()
        # await bot.tree.set_translator(TimmyTranslator())

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
        """
        Returns the current version of the bot.
        """
        return __version__

    @property
    def start_time(self):
        """
        Returns the time the bot was started.
        """
        return self._start_time


bot = Timmy(time.time())

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        database.CommandAnalytics.create(
            command=interaction.command.name,
            guild_id=interaction.guild.id,
            user=interaction.user.id,
            date=datetime.now(),
            command_type="slash",
        ).save()


if os.getenv("DSN_SENTRY") is not None:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )

    # Traceback tracking, DO NOT MODIFY THIS
    use_sentry(
        bot,
        dsn=os.getenv("DSN_SENTRY"),
        traces_sample_rate=1.0,
        integrations=[FlaskIntegration(), sentry_logging],
    )


initializeDB(bot)

"""if not os.getenv("StartAPI"):
    bot.run(os.getenv("TOKEN"))"""


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot.start(os.getenv("TOKEN")))


@app.get("/")
async def root():
    current_time = float(time.time())
    difference = int(round(current_time - float(bot.start_time)))
    text = str(timedelta(seconds=difference))
    return {
        "uptime": text,
        "version": __version__,
        "author": __author__,
        "author_email": __author_email__,
        "start_time": bot.start_time,
        "latency": bot.latency,
    }


"""@app.post("/send")
@limiter.limit("5/minute")
async def send_route(token: str = Header(), payload: JSONPayload = Depends()):
    user = authenticate_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # check if user is authorized to use this route
    if payload.action not in user.authorized_routes:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to use this route",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.disabled:
        raise HTTPException(
            status_code=400, detail="Inactive user"
        )

    if payload.action == "route_send":
        print("Creating new record")
        print(payload.payload)
        return status.HTTP_200_OK

    elif payload.action == "gsuite":
        create_gsuite(payload)"""





if __name__ == "__main__":
    if os.getenv("StartAPI") == "True":
        uvicorn.run(app, host="0.0.0.0", port=80)
    else:
        bot.run(os.getenv("TOKEN"))
