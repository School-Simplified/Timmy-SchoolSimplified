import asyncio
import sys
import time
from datetime import timedelta

import discord
import psutil
from discord.ext import commands
from dotenv import load_dotenv
from sentry_sdk import Hub

from core import database
from core.checks import is_botAdmin2
from core.common import Emoji, Others, MainID
from core.logging_module import get_log


_log = get_log(__name__)
load_dotenv()


class MiscCMD(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.__cog_name__ = "General"
        self.bot = bot
        self.interaction = []

        self.client = Hub.current.client

        self.whitelistedRoles = [
            MainID.r_coding_club,
            MainID.r_debate_club,
            MainID.r_music_club,
            MainID.r_cooking_club,
            MainID.r_chess_club,
            MainID.r_book_club,
            MainID.r_advocacy_club,
            MainID.r_speech_club,
        ]

        self.decodeDict = {
            "['Simplified Coding Club']": 883169286665936996,
            "['Simplified Debate Club']": 883170141771272294,
            "['Simplified Music Club']": 883170072355561483,
            "['Simplified Cooking Club']": 883162279904960562,
            "['Simplified Chess Club']": 883564455219306526,
            "['Simplified Book Club']": 883162511560560720,
            "['Simplified Advocacy Club']": 883169000866070539,
            "['Simplified Speech Club']": 883170166161149983,
        }

        self.options = [
            discord.SelectOption(
                label="Simplified Coding Club", description="", emoji="💻"
            ),
            discord.SelectOption(
                label="Simplified Debate Club", description="", emoji="💭"
            ),
            discord.SelectOption(
                label="Simplified Music Club", description="", emoji="🎵"
            ),
            discord.SelectOption(
                label="Simplified Cooking Club", description="", emoji="🍱"
            ),
            discord.SelectOption(
                label="Simplified Chess Club", description="", emoji="🏅"
            ),
            discord.SelectOption(
                label="Simplified Book Club", description="", emoji="📚"
            ),
            discord.SelectOption(
                label="Simplified Advocacy Club", description="", emoji="📰"
            ),
            discord.SelectOption(
                label="Simplified Speech Club", description="", emoji="🎤"
            ),
        ]

    @property
    def display_emoji(self) -> str:
        return Emoji.schoolsimplified

    @commands.command(aliases=["ttc", "tictactoe"])
    async def tic(self, ctx):
        return

    @commands.command()
    async def suggest(self, ctx):
        return

    @commands.command(aliases=["donation"])
    async def donate(self, ctx):
        return

    @commands.command()
    async def pingmasa(self, ctx):
        return

    @commands.command()
    async def join(self, ctx):
        return

    # BACKUP
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
        pingembed.add_field(name="Status Page", value="[Click here](https://status.timmy.ssimpl.org/)")
        pingembed.set_footer(
            text=f"TimmyOS Version: {self.bot.version}", icon_url=ctx.author.avatar.url
        )

        await ctx.send(embed=pingembed)

        database.db.close()

    @commands.command()
    async def help(self, ctx):
        return

    # BACKUP
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

    @commands.command()
    async def role(self, ctx):
        return

    @commands.command()
    async def clubping(self, ctx):
        return

    @commands.command()
    async def say(self, ctx):
        return

    @commands.command()
    async def sayvc(self, ctx):
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(MiscCMD(bot))
