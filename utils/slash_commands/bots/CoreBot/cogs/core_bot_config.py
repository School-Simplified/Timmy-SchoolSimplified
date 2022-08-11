import subprocess
import sys
from pathlib import Path
from threading import Thread
from typing import Literal

import discord
from discord.app_commands import command
from discord.ext import commands
from dotenv import load_dotenv

from core import database
from core.checks import (
    is_botAdmin,
    is_botAdmin2,
    is_botAdmin3,
    is_botAdmin4,
    slash_is_bot_admin_2,
)
from core.common import CheckDB_CC
from core.common import Emoji, Colors
from core.common import get_host_dir, force_restart

load_dotenv()


def get_extensions():
    extensions = ["jishaku"]
    for file in Path("utils").glob("**/*.py"):
        if "!" in file.name or "DEV" in file.name:
            continue
        extensions.append(str(file).replace("/", ".").replace(".py", ""))
    return extensions


class CoreBotConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.__cog_name__ = "Core Bot Config"
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return "⚙️"

    @commands.group(aliases=["f"])
    async def filters(self, ctx):
        pass

    @commands.command()
    @is_botAdmin4
    async def Fmodify(self, ctx, num: int, val: bool):
        CheckDB: database.CheckInformation = (
            database.CheckInformation.select()
            .where(database.CheckInformation.id == 1)
            .get()
        )

        databaseValues = {
            1: "CheckDB.MasterMaintenance",
            2: "CheckDB.guildNone",
            3: "CheckDB.externalGuild",
            4: "CheckDB.ModRoleBypass",
            5: "CheckDB.ruleBypass",
            6: "CheckDB.publicCategories",
            7: "CheckDB.elseSituation",
        }

        if num == 1:
            CheckDB.MasterMaintenance = val
            CheckDB.save()
        elif num == 2:
            CheckDB.guildNone = val
            CheckDB.save()
        elif num == 3:
            CheckDB.externalGuild = val
            CheckDB.save()
        elif num == 4:
            CheckDB.ModRoleBypass = val
            CheckDB.save()
        elif num == 5:
            CheckDB.ruleBypass = val
            CheckDB.save()
        elif num == 6:
            CheckDB.publicCategories = val
            CheckDB.save()
        elif num == 7:
            CheckDB.elseSituation = val
            CheckDB.save()
        else:
            return await ctx.send(f"Not a valid option\n```py\n{databaseValues}\n```")

        await ctx.send(f"Field: {databaseValues[num]} has been set to {str(val)}")

    @filters.command()
    async def list(self, ctx):
        CheckDB: database.CheckInformation = (
            database.CheckInformation.select()
            .where(database.CheckInformation.id == 1)
            .get()
        )

        embed = discord.Embed(
            title="Command Filters",
            description="Bot Filters that the bot is subjected towards.",
            color=discord.Colour.gold(),
        )
        embed.add_field(
            name="Checks",
            value=f"1) `Maintenance Mode`\n{Emoji.barrow} {CheckDB_CC.MasterMaintenance}"
            f"\n\n2) `NoGuild`\n{Emoji.barrow} {CheckDB_CC.guild_None}"
            f"\n\n3) `External Guilds`\n{Emoji.barrow} {CheckDB_CC.external_guild}"
            f"\n\n4) `ModBypass`\n{Emoji.barrow} {CheckDB_CC.mod_role_bypass}"
            f"\n\n5) `Rule Command Bypass`\n{Emoji.barrow} {CheckDB_CC.rule_bypass}"
            f"\n\n6) `Public Category Lock`\n{Emoji.barrow} {CheckDB_CC.public_categories}"
            f"\n\n7) `Else Conditions`\n{Emoji.barrow} {CheckDB_CC.else_situation}",
        )
        await ctx.send(embed=embed)

    @commands.group(aliases=["pre"])
    async def prefix(self, ctx):
        pass

    @prefix.command()
    @is_botAdmin3
    async def delete(self, ctx, num: int):
        WhitelistedPrefix: database.WhitelistedPrefix = (
            database.WhitelistedPrefix.select()
            .where(database.WhitelistedPrefix.id == num)
            .get()
        )
        WhitelistedPrefix.delete_instance()
        await ctx.send(f"Field: {WhitelistedPrefix.prefix} has been deleted")

    @prefix.command()
    @is_botAdmin3
    async def add(self, ctx, prefix):
        WhitelistedPrefix = database.WhitelistedPrefix.create(
            prefix=prefix, status=True
        )
        await ctx.send(f"Field: {WhitelistedPrefix.prefix} has been added!")

    @prefix.command()
    async def list(self, ctx):

        PrefixDB = database.WhitelistedPrefix
        response = []

        for entry in PrefixDB:

            if entry.status is True:
                statusFilter = "ACTIVE"
            else:
                statusFilter = "DISABLED"

            response.append(f"Prefix `{entry.prefix}`:\n{Emoji.barrow} {statusFilter}")

        embed = discord.Embed(
            title="Whitelisted Prefix's",
            description="Bot Prefix's that are whitelisted in staff commands.",
            color=discord.Colour.gold(),
        )
        embed.add_field(name="Prefix List", value="\n\n".join(response))
        await ctx.send(embed=embed)

    @commands.group(aliases=["cog"])
    @is_botAdmin2
    async def cogs(self, ctx):
        pass

    @cogs.command()
    @is_botAdmin2
    async def unload(self, ctx, ext):
        if "tickets." not in ext:
            ext = f"tickets.{ext}"
        if ext in get_extensions():
            await self.bot.unload_extension(ext)
            embed = discord.Embed(
                title="Cogs - Unload",
                description=f"Unloaded cog: {ext}",
                color=Colors.light_purple,
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Cogs Reloaded",
                description=f"Cog '{ext}' not found",
                color=Colors.light_purple,
            )
            await ctx.send(embed=embed)

    @cogs.command()
    @is_botAdmin2
    async def load(self, ctx, ext):
        if "tickets." not in ext:
            ext = f"tickets.{ext}"
        if ext in get_extensions():
            await self.bot.load_extension(ext)
            embed = discord.Embed(
                title="Cogs - Load",
                description=f"Loaded cog: {ext}",
                color=Colors.light_purple,
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Cogs - Load",
                description=f"Cog '{ext}' not found.",
                color=Colors.light_purple,
            )
            await ctx.send(embed=embed)

    @cogs.command(aliases=["restart"])
    @is_botAdmin2
    async def reload(self, ctx, ext):
        if ext == "all":
            embed = discord.Embed(
                title="Cogs - Reload",
                description="Reloaded all tickets",
                color=Colors.light_purple,
            )
            for extension in get_extensions():
                await self.bot.reload_extension(extension)
            await ctx.send(embed=embed)
            return

        if "tickets." not in ext:
            ext = f"tickets.{ext}"

        if ext in get_extensions():
            await self.bot.reload_extension(ext)
            embed = discord.Embed(
                title="Cogs - Reload",
                description=f"Reloaded cog: {ext}",
                color=Colors.light_purple,
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Cogs - Reload",
                description=f"Cog '{ext}' not found.",
                color=Colors.light_purple,
            )
            await ctx.send(embed=embed)

    @cogs.command()
    @is_botAdmin2
    async def view(self, ctx):
        msg = " ".join(get_extensions())
        embed = discord.Embed(
            title="Cogs - View", description=msg, color=Colors.light_purple
        )
        await ctx.send(embed=embed)

    @commands.command(name="gitpull")
    @is_botAdmin2
    async def _gitpull(self, ctx, mode="-a", branch=None):
        output = ""
        hostDir = get_host_dir()

        if branch is not None:
            if hostDir == "/home/timmya":
                branch = "origin/main"
                directory = "TimmyMain-SS"

            elif hostDir == "/home/timmy-beta":
                branch = "origin/beta"
                directory = "TimmyBeta-SS"

            else:
                raise ValueError("Host directory is neither 'timmya' nor 'timmy-beta'.")
        else:
            if hostDir == "/home/timmya":
                raise ValueError("Branch can not be changed when running production.")
            branch = branch
            directory = "TimmyBeta-SS"

        try:
            p = subprocess.run(
                "git fetch --all",
                shell=True,
                text=True,
                capture_output=True,
                check=True,
            )
            output += p.stdout
        except Exception as e:
            await ctx.send("⛔️ Unable to fetch the Current Repo Header!")
            await ctx.send(f"**Error:**\n{e}")
        try:
            p = subprocess.run(
                f"git reset --hard {branch}",
                shell=True,
                text=True,
                capture_output=True,
                check=True,
            )
            output += p.stdout
        except Exception as e:
            await ctx.send("⛔️ Unable to apply changes!")
            await ctx.send(f"**Error:**\n{e}")

        embed = discord.Embed(
            title="GitHub Local Reset",
            description=f"Local Files changed to match {branch}",
            color=Colors.green,
        )
        embed.add_field(name="Shell Output", value=f"```shell\n$ {output}\n```")
        if mode == "-a":
            embed.set_footer(text="Attempting to restart the bot...")
        elif mode == "-c":
            embed.set_footer(text="Attempting to reloading tickets...")

        await ctx.send(embed=embed)

        if mode == "-a":
            await force_restart(ctx, directory)
        elif mode == "-c":
            await ctx.invoke(self.bot.get_command("tickets reload"), ext="all")

    @command()
    @slash_is_bot_admin_2()
    async def gitpull(
        self,
        interaction: discord.Interaction,
        mode: Literal["-a", "-c"] = "-a",
        sync_commands: bool = False,
    ) -> None:
        output = ""

        hostDir = get_host_dir()
        if hostDir == "/home/timmya":
            branch = "origin/main"
            directory = "TimmyMain-SS"

        elif hostDir == "/home/timmy-beta":
            branch = "origin/beta"
            directory = "TimmyBeta-SS"

        else:
            return await interaction.response.send_message(
                "Host directory is neither 'timmya' nor "
                "'timmy-beta'.\nSomeone else is currently hosting the bot."
            )

        try:
            p = subprocess.run(
                "git fetch --all",
                shell=True,
                text=True,
                capture_output=True,
                check=True,
            )
            output += p.stdout
        except Exception as e:
            await interaction.response.send_message(
                f"⛔️ Unable to fetch the Current Repo Header!\n**Error:**\n{e}"
            )
        try:
            p = subprocess.run(
                f"git reset --hard {branch}",
                shell=True,
                text=True,
                capture_output=True,
                check=True,
            )
            output += p.stdout
        except Exception as e:
            await interaction.response.send_message(
                f"⛔️ Unable to apply changes!\n**Error:**\n{e}"
            )

        embed = discord.Embed(
            title="GitHub Local Reset",
            description=f"Local Files changed to match {branch}",
            color=discord.Color.brand_green(),
        )
        embed.add_field(name="Shell Output", value=f"```shell\n$ {output}\n```")
        if mode == "-a":
            embed.set_footer(text="Attempting to restart the bot...")
        elif mode == "-c":
            embed.set_footer(text="Attempting to reloading tickets...")

        await interaction.response.send_message(embed=embed)

        if mode == "-a":
            await self._force_restart(interaction, directory)
        elif mode == "-c":
            try:
                embed = discord.Embed(
                    title="Cogs - Reload",
                    description="Reloaded all tickets",
                    color=discord.Color.brand_green(),
                )
                for extension in get_extensions():
                    await self.bot.reload_extension(extension)
                return await interaction.channel.send(embed=embed)
            except commands.ExtensionError:
                embed = discord.Embed(
                    title="Cogs - Reload",
                    description="Failed to reload tickets",
                    color=discord.Color.brand_red(),
                )
                return await interaction.channel.send(embed=embed)

        if sync_commands:
            await self.bot.tree.sync()

    @commands.group()
    async def w(self, ctx):
        pass

    @w.command()
    @is_botAdmin
    async def list(self, ctx):
        adminList = []

        query1 = database.Administrators.select().where(
            database.Administrators.TierLevel == 1
        )
        for admin in query1:
            user = self.bot.get_user(admin.discordID)
            if user is None:
                try:
                    user = await self.bot.fetch_user(admin.discordID)
                except:
                    continue
            adminList.append(f"`{user.name}` -> `{user.id}`")

        adminLEVEL1 = "\n".join(adminList)

        adminList = []
        query2 = database.Administrators.select().where(
            database.Administrators.TierLevel == 2
        )
        for admin in query2:
            user = self.bot.get_user(admin.discordID)
            if user is None:
                try:
                    user = await self.bot.fetch_user(admin.discordID)
                except:
                    continue
            adminList.append(f"`{user.name}` -> `{user.id}`")

        adminLEVEL2 = "\n".join(adminList)

        adminList = []
        query3 = database.Administrators.select().where(
            database.Administrators.TierLevel == 3
        )
        for admin in query3:
            user = self.bot.get_user(admin.discordID)
            if user is None:
                try:
                    user = await self.bot.fetch_user(admin.discordID)
                except:
                    continue
            adminList.append(f"`{user.name}` -> `{user.id}`")

        adminLEVEL3 = "\n".join(adminList)

        adminList = []
        query4 = database.Administrators.select().where(
            database.Administrators.TierLevel == 4
        )
        for admin in query4:
            user = self.bot.get_user(admin.discordID)
            if user is None:
                try:
                    user = await self.bot.fetch_user(admin.discordID)
                except:
                    continue
            adminList.append(f"`{user.name}` -> `{user.id}`")

        adminLEVEL4 = "\n".join(adminList)

        embed = discord.Embed(
            title="Bot Administrators",
            description="Whitelisted Users that have Increased Authorization",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Whitelisted Users",
            value=f"Format:\n**Username** -> **ID**"
            f"\n\n**Permit 4:** *Owners*\n{adminLEVEL4}"
            f"\n\n**Permit 3:** *Sudo Administrators*\n{adminLEVEL3}"
            f"\n\n**Permit 2:** *Administrators*\n{adminLEVEL2}"
            f"\n\n**Permit 1:** *Bot Managers*\n{adminLEVEL1}",
        )
        embed.set_footer(
            text="Only Owners/Permit 4's can modify Bot Administrators. | Permit 4 is the HIGHEST Authorization Level"
        )

        await ctx.send(embed=embed)

    @w.command()
    @is_botAdmin4
    async def remove(self, ctx, ID: discord.User):
        database.db.connect(reuse_if_open=True)

        query = database.Administrators.select().where(
            database.Administrators.discordID == ID.id
        )
        if query.exists():
            query = query.get()

            query.delete_instance()

            embed = discord.Embed(
                title="Successfully Removed User!",
                description=f"{ID.name} has been removed from the database!",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid User!",
                description="Invalid Provided: (No Record Found)",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)

        database.db.close()

    @w.command()
    @is_botAdmin4
    async def add(self, ctx, ID: discord.User, level: int):
        database.db.connect(reuse_if_open=True)

        q: database.Administrators = database.Administrators.create(
            discordID=ID.id, TierLevel=level
        )
        q.save()

        embed = discord.Embed(
            title="Successfully Added User!",
            description=f"{ID.name} has been added successfully with permit level `{str(level)}`.",
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)

        database.db.close()

    @staticmethod
    async def _force_restart(interaction: discord.Interaction, main_or_beta):
        p = subprocess.run(
            "git status -uno", shell=True, text=True, capture_output=True, check=True
        )

        embed = discord.Embed(
            title="Restarting...",
            description="Doing GIT Operation (1/3)",
            color=discord.Color.brand_green(),
        )
        embed.add_field(
            name="Checking GIT (1/3)",
            value=f"**Git Output:**\n```shell\n{p.stdout}\n```",
        )

        msg = await interaction.channel.send(embed=embed)
        try:

            result = subprocess.run(
                f"cd && cd {main_or_beta}",
                shell=True,
                text=True,
                capture_output=True,
                check=True,
            )
            theproc = subprocess.Popen([sys.executable, "main.py"])

            runThread = Thread(target=theproc.communicate)
            runThread.start()

            embed.add_field(
                name="Started Environment and Additional Process (2/3)",
                value="Executed `source` and `nohup`.",
                inline=False,
            )
            await msg.edit(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Operation Failed", description=e, color=discord.Color.brand_red()
            )
            embed.set_footer(text="Main bot process will be terminated.")

            await interaction.channel.send(embed=embed)

        else:
            embed.add_field(
                name="Killing Old Bot Process (3/3)",
                value="Executing `sys.exit(0)` now...",
                inline=False,
            )
            await msg.edit(embed=embed)
            sys.exit(0)


async def setup(bot):
    await bot.add_cog(CoreBotConfig(bot))
