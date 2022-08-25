import asyncio
import sys
import time
from datetime import timedelta
from typing import Union, Literal

import discord
import psutil
from discord import ui, ButtonStyle
from discord.ext import commands
from dotenv import load_dotenv
from sentry_sdk import Hub

from core import database
from core.checks import is_botAdmin2
from core.checks import is_botAdmin3
from core.common import Colors, ButtonHandler
from core.common import Others
from core.logging_module import get_log

_log = get_log(__name__)
load_dotenv()


class BackupRegularCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = Hub.current.client

    @commands.command()
    @is_botAdmin3
    async def sync(
        self,
        ctx: commands.Context,
        action: Union[Literal["global"], Literal["all"], discord.Guild],
    ):
        if isinstance(action, discord.Guild):
            guild = action

            embed_processing = discord.Embed(
                color=Colors.yellow,
                title="Sync",
                description=f"Syncing slash commands for guild `{guild.name}`...",
            )
            message_sync = await ctx.send(embed=embed_processing)

            await self.bot.tree.sync(guild=discord.Object(guild.id))

            embed_done = discord.Embed(
                color=Colors.green,
                title="Sync",
                description=f"Successfully synced slash commands for guild `{guild.name}`!",
            )
            await message_sync.edit(embed=embed_done)

        elif action == "global":

            view = ui.View(timeout=30)
            button_confirm = ButtonHandler(
                style=ButtonStyle.green,
                label="Confirm",
                emoji="✅",
                button_user=ctx.author,
            )
            button_cancel = ButtonHandler(
                style=ButtonStyle.red, label="Cancel", emoji="❌", button_user=ctx.author
            )
            view.add_item(button_confirm)
            view.add_item(button_cancel)

            embed_confirm = discord.Embed(
                color=Colors.yellow,
                title="Sync Confirmation",
                description=f"Are you sure you want to sync globally? This may take 1 hour.",
            )
            message_confirm = await ctx.send(embed=embed_confirm, view=view)

            timeout = await view.wait()
            if not timeout:
                if view.value == "Confirm":

                    embed_processing = discord.Embed(
                        color=Colors.yellow,
                        title="Sync",
                        description=f"Syncing slash commands globally..."
                        f"\nThis may take a while.",
                    )
                    await message_confirm.edit(embed=embed_processing, view=None)

                    await self.bot.tree.sync()

                    embed_processing = discord.Embed(
                        color=Colors.green,
                        title="Sync",
                        description=f"Successfully synced slash commands globally!",
                    )
                    await message_confirm.edit(embed=embed_processing)

                elif view.value == "Cancel":
                    embed_cancel = discord.Embed(
                        color=Colors.red, title="Sync", description="Sync canceled."
                    )
                    await message_confirm.edit(embed=embed_cancel, view=None)

            else:
                embed_timeout = discord.Embed(
                    color=Colors.red,
                    title="Sync",
                    description="Sync canceled due to timeout.",
                )
                await message_confirm.edit(embed=embed_timeout, view=None)

        elif action == "all":

            view = ui.View(timeout=30)
            button_confirm = ButtonHandler(
                style=ButtonStyle.green,
                label="Confirm",
                emoji="✅",
                button_user=ctx.author,
            )
            button_cancel = ButtonHandler(
                style=ButtonStyle.red, label="Cancel", emoji="❌", button_user=ctx.author
            )
            view.add_item(button_confirm)
            view.add_item(button_cancel)

            embed_confirm = discord.Embed(
                color=Colors.yellow,
                title="Sync Confirmation",
                description=f"Are you sure you want to sync all local guild commands?",
            )
            message_confirm = await ctx.send(embed=embed_confirm, view=view)

            timeout = await view.wait()
            if not timeout:
                if view.value == "Confirm":

                    embed_processing = discord.Embed(
                        color=Colors.yellow,
                        title="Sync",
                        description=f"Syncing all local guild slash commands ..."
                        f"\nThis may take a while.",
                    )
                    await message_confirm.edit(embed=embed_processing, view=None)

                    for guild in self.bot.guilds:
                        await self.bot.tree.sync(guild=discord.Object(guild.id))

                    embed_processing = discord.Embed(
                        color=Colors.green,
                        title="Sync",
                        description=f"Successfully synced slash commands in all servers!",
                    )
                    await message_confirm.edit(embed=embed_processing)

                elif view.value == "Cancel":
                    embed_cancel = discord.Embed(
                        color=Colors.red, title="Sync", description="Sync canceled."
                    )
                    await message_confirm.edit(embed=embed_cancel, view=None)

            else:
                embed_timeout = discord.Embed(
                    color=Colors.red,
                    title="Sync",
                    description="Sync canceled due to timeout.",
                )
                await message_confirm.edit(embed=embed_timeout, view=None)

    @commands.command()
    async def ping(self, ctx):
        database.db.connect(reuse_if_open=True)

        current_time = float(time.time())
        difference = int(round(current_time - float(self.bot.start_time)))
        text = str(timedelta(seconds=difference))

        pingembed = discord.Embed(
            title="Pong! ⌛",
            color=discord.Colour.gold(),
            description="Current Discord API Latency",
        )
        pingembed.set_author(
            name="Timmy", url=Others.timmy_laptop_png, icon_url=Others.timmy_happy_png
        )
        pingembed.add_field(
            name="Ping & Uptime:",
            value=f"```diff\n+ Ping: {round(self.bot.latency * 1000)}ms\n+ Uptime: {text}\n```",
        )

        pingembed.add_field(
            name="System Resource Usage",
            value=f"```diff\n- CPU Usage: {psutil.cpu_percent()}%\n- Memory Usage: {psutil.virtual_memory().percent}%\n```",
            inline=False,
        )
        pingembed.add_field(
            name="Status Page", value="[Click here](https://status.timmy.ssimpl.org/)"
        )
        pingembed.set_footer(
            text=f"TimmyOS Version: {self.bot.version}", icon_url=ctx.author.avatar.url
        )

        await ctx.send(embed=pingembed)

        database.db.close()

    @commands.command()
    @is_botAdmin2
    async def kill(self, ctx):
        embed = discord.Embed(
            title="Confirm System Abortion",
            description="Please react with the appropriate emoji to confirm your choice!",
            color=discord.Colour.dark_orange(),
        )
        embed.add_field(
            name="WARNING",
            value="Please not that this will kill the bot immediately and it will not be online unless a "
            "developer manually starts the proccess again!"
            "\nIf you don't respond in 5 seconds, the process will automatically abort.",
        )
        embed.set_footer(
            text="Abusing this system will subject your authorization removal, so choose wisely you fucking pig."
        )

        message = await ctx.send(embed=embed)

        reactions = ["✅", "❌"]
        for emoji in reactions:
            await message.add_reaction(emoji)

        def check2(reaction, user):
            return user == ctx.author and (
                str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌"
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=5.0, check=check2
            )
            if str(reaction.emoji) == "❌":
                await ctx.send("Aborted Exit Process")
                await message.delete()
                return

            else:
                await message.delete()
                database.db.connect(reuse_if_open=True)
                NE = database.AdminLogging.create(
                    discordID=ctx.author.id, action="KILL"
                )
                NE.save()
                database.db.close()

                if self.client is not None:
                    self.client.close(timeout=2.0)

                embed = discord.Embed(
                    title="Initiating System Exit...",
                    description="Goodbye!",
                    color=discord.Colour.dark_orange(),
                )
                message = await ctx.send(embed=embed)

                sys.exit(0)

        except asyncio.TimeoutError:
            await ctx.send(
                "Looks like you didn't react in time, automatically aborted system exit!"
            )
            await message.delete()


async def setup(bot):
    await bot.add_cog(BackupRegularCommands(bot))
