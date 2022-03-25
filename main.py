import faulthandler
import logging
import os
import time
from typing import Any, Optional, Union

from alive_progress import alive_bar

import discord
from discord.app_commands import AppCommandError, Command, ContextMenu

from discord.ext import commands
from discord_sentry_reporting import use_sentry
from dotenv import load_dotenv
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from core import database
from core.special_methods import before_invoke_, main_mode_check_, on_command_error_, on_ready_
from core.common import get_extensions

load_dotenv()
faulthandler.enable()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

logger.warning("Started Timmy")
print("Starting Timmy...")


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

        with alive_bar(len(get_extensions()), ctrl_c=False, bar="bubbles", title=f"Initializing Cogs:") as bar:
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



# class TimmyCommandTree(discord.app_commands.CommandTree):
#     def __init__(self, client: commands.Bot):
#         super().__init__(client)
#
#     async def on_error(
#             self,
#             interaction: discord.Interaction,
#             command: Optional[Union[ContextMenu, Command[Any, ..., Any]]],
#             error: AppCommandError,
#     ) -> None:
#         ...
@bot.event
async def on_guild_join(guild: discord.Guild):
    query = database.AuthorizedGuilds.select().where(database.AuthorizedGuilds.guildID == guild.id)
    if not query.exists():
        embed = discord.Embed(title="Unable to join guild!", description="This guild is not authorized to use Timmy!", color=discord.Color.brand_red())
        embed.set_thumbnail(url=Others.timmyDog_png)
        embed.set_footer(text="Please contact an IT administrator for help.")
        for channel in guild.channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(embed=embed)
                break
        await guild.leave()



bot.run(os.getenv("TOKEN"))
