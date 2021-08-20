import asyncio
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import chat_exporter
import discord
from discord.ext import commands
from discord_sentry_reporting import use_sentry
from dotenv import load_dotenv
from tqdm import tqdm

from core import database
from core.checks import is_botAdmin, is_botAdmin2, is_botAdmin4
from core.common import Emoji, bcolors

load_dotenv()

# Applying towards intents
intents = discord.Intents.all()

# Defining client
activity=discord.Activity(type=discord.ActivityType.watching, name="+help | timmy.schoolsimplified.org")

client = commands.Bot(command_prefix=commands.when_mentioned_or('+'), intents=intents, case_insensitive=True, activity = activity)
client.remove_command('help')

use_sentry(
    client,  # Traceback tracking, DO NOT MODIFY THIS
    dsn=os.getenv('DSN_SENTRY'),
    traces_sample_rate=1.0
)

publicCH = [763121170324783146, 800163651805773824, 774847738239385650, 805299289604620328, 796909060707319838, 787841402381139979, 830992617491529758, 763857608964046899, 808020719530410014]

#Start Check
UpQ = database.Uptime.select().where(database.Uptime.id == 1)
CIQ = database.CheckInformation.select().where(database.CheckInformation.id == 1)
if not UpQ.exists():
    database.Uptime.create(UpStart = "1")
    print("Created Uptime Entry.")

if not CIQ.exists():
    database.CheckInformation.create(MasterMaintenance = False, guildNone = False, externalGuild = True, ModRoleBypass = True, ruleBypass = True, publicCategory = True, elseSituation = True)
    print("Created Uptime Entry.")


database.db.connect(reuse_if_open=True)
q :database.Uptime =  database.Uptime.select().where(database.Uptime.id == 1).get()
q.UpStart = time.time()
q.save()
database.db.close()


def get_extensions():  # Gets extension list dynamically
    extensions = []
    blacklistedPrefix = ['!', "__", "DEV"]
    
    for file in Path("utils").glob("**/*.py"):
        if "!" in file.name or "__" in file.name or "DEV" in file.name:
            continue
        extensions.append(str(file).replace("/", ".").replace(".py", ""))
    return extensions


async def force_restart(ctx):
    p = subprocess.run("git status -uno",  shell=True, text=True, capture_output=True, check=True)

    embed = discord.Embed(title = "Restarting...", description = "Doing GIT Operation (1/3)", color = discord.Color.green())
    embed.add_field(name = "Checking GIT (1/3)", value = f"**Git Output:**\n```shell\n{p.stdout}\n```")

    msg = await ctx.send(embed = embed)
    try:
        result = subprocess.run("cd && cd Timmy-SchoolSimplified && nohup python3 main.py &", shell=True, text=True, capture_output=True,
                                check=True)

        embed.add_field(name = "Started Environment and Additional Process (2/3)", value = "Executed `source` and `nohup`.", inline = False)
        await msg.edit(embed = embed)

    except Exception as e:
        embed = discord.Embed(title = "Operation Failed", description = e, color = discord.Color.red())
        embed.set_footer(text = "Main bot process will be terminated.")

        await ctx.send(embed = embed)

    else:
        embed.add_field(name = "Killing Old Bot Process (3/3)", value = "Executing `sys.exit(0)` now...", inline = False)
        await msg.edit(embed = embed)
        sys.exit(0)

def get_branch():
    p = subprocess.run("git rev-parse --abbrev-ref HEAD",  shell=True, text=True, capture_output=True, check=True)
    output = p.stdout

    Branch = None
    MSG = None

    if output == "main":
        Branch = "Stable"
        MSG = "Running Stable Version"
    
    else:
        Branch = "UnStable"
        MSG = f"{bcolors.FAIL}WARNING: This Version is UnStable!{bcolors.ENDC}"
    
    return Branch, MSG

@client.event
async def on_ready():
    now = datetime.now()

    print(f"Logged in as: {client.user.name}")
    print(f"{bcolors.OKBLUE}CONNECTED TO DISCORD{bcolors.ENDC}")
    print(f"{bcolors.WARNING}Current Discord.py Version: {discord.__version__}{bcolors.ENDC}")
    print(f"{bcolors.WARNING}Current Time: {now}{bcolors.ENDC}")

    chat_exporter.init_exporter(client)




files = get_extensions()
i = 0 
capLimit = len(files)
ext = files[i]

for i in tqdm(range(capLimit - 1), ascii = True, desc =f"Loading Cogs..."):
    client.load_extension(ext)
    i+=1
    if i >= capLimit:
        break
    else:
        ext = files[i]


@client.check
async def mainModeCheck(ctx: commands.Context):
    MT = discord.utils.get(ctx.guild.roles, name= "Moderator")
    VP = discord.utils.get(ctx.guild.roles, name= "VP")
    CO = discord.utils.get(ctx.guild.roles, name= "CO")
    SS = discord.utils.get(ctx.guild.roles, name= "Secret Service")
    
    CheckDB : database.CheckInformation =  database.CheckInformation.select().where(database.CheckInformation.id == 1).get()

    blacklistedUsers = []
    for p in database.Blacklist:
        blacklistedUsers.append(p.discordID)

    print(blacklistedUsers)


    adminIDs = []
    query = database.Administrators.select().where(database.Administrators.TierLevel == 4)
    for admin in query:
        adminIDs.append(admin.discordID)

    #Permit 4 Check
    if ctx.author.id in adminIDs:
        return True


    #Maintenance Check
    elif CheckDB.MasterMaintenance:
        embed = discord.Embed(title = "Master Maintenance ENABLED", description = f"{Emoji.deny} The bot is currently unavailable as it is under maintenance, check back later!", color = discord.Colour.gold())
        embed.set_footer(text = "Need an immediate unlock? Message a Developer or SpaceTurtle#0001")
        await ctx.send(embed = embed)

        return False

    #Blacklist Check
    elif ctx.author.id in blacklistedUsers:
        return False
    
    #DM Check
    elif ctx.guild == None:
        return CheckDB.guildNone

    #External Server Check
    elif ctx.guild.id != 763119924385939498:
        return CheckDB.externalGuild

    #Mod Role Check
    elif MT in ctx.author.roles or VP in ctx.author.roles or CO in ctx.author.roles or SS in ctx.author.roles:
        return CheckDB.ModRoleBypass

    #Rule Command Check
    elif ctx.command.name == "rule":
        return CheckDB.ruleBypass

    #Public Category Check
    elif ctx.channel.category_id in publicCH:
        return CheckDB.publicCategories

    #Else...
    else:
        return CheckDB.elseSituation


@client.group()
async def w(ctx):
    pass


@w.command()
@is_botAdmin
async def list(ctx):
    adminList = []

    query1 = database.Administrators.select().where(database.Administrators.TierLevel == 1)
    for admin in query1:
        user = await client.fetch_user(admin.discordID)
        adminList.append(f"`{user.name}` -> `{user.id}`")

    adminLEVEL1 = "\n".join(adminList)

    adminList = []
    query2 = database.Administrators.select().where(database.Administrators.TierLevel == 2)
    for admin in query2:
        user = await client.fetch_user(admin.discordID)
        adminList.append(f"`{user.name}` -> `{user.id}`")

    adminLEVEL2 = "\n".join(adminList)

    adminList = []
    query3 = database.Administrators.select().where(database.Administrators.TierLevel == 3)
    for admin in query3:
        user = await client.fetch_user(admin.discordID)
        adminList.append(f"`{user.name}` -> `{user.id}`")

    adminLEVEL3 = "\n".join(adminList)

    adminList = []
    query4 = database.Administrators.select().where(database.Administrators.TierLevel == 4)
    for admin in query4:
        user = await client.fetch_user(admin.discordID)
        adminList.append(f"`{user.name}` -> `{user.id}`")

    adminLEVEL4 = "\n".join(adminList)

    embed = discord.Embed(title="Bot Administrators", description="Whitelisted Users that have Increased Authorization",
                        color=discord.Color.green())
    embed.add_field(name="Whitelisted Users",
                    value=f"Format:\n**Username** -> **ID**\n\n**Permit 4:** *Owners*\n{adminLEVEL4}\n\n**Permit 3:** *Sudo Administrators*\n{adminLEVEL3}\n\n**Permit 2:** *Administrators*\n{adminLEVEL2}\n\n**Permit 1:** *Bot Managers*\n{adminLEVEL1}")
    embed.set_footer(text="Only Owners/Permit 4's can modify Bot Administrators. | Permit 4 is the HIGHEST Authorization Level")

    await ctx.send(embed=embed)


@w.command()
@is_botAdmin4
async def remove(ctx, ID: discord.User):
    database.db.connect(reuse_if_open=True)

    query = database.Administrators.select().where(database.Administrators.discordID == ID.id)
    if query.exists():
        query = query.get()

        query.delete_instance()

        embed = discord.Embed(title="Successfully Removed User!",
                            description=f"{ID.name} has been removed from the database!", color=discord.Color.green())
        await ctx.send(embed=embed)


    else:
        embed = discord.Embed(title="Invalid User!", description="Invalid Provided: (No Record Found)",
                            color=discord.Color.red())
        await ctx.send(embed=embed)

    database.db.close()


@w.command()
@is_botAdmin4
async def add(ctx, ID: discord.User, level: int):
    database.db.connect(reuse_if_open=True)

    q: database.Administrators = database.Administrators.create(discordID=ID.id, TierLevel=level)
    q.save()

    embed = discord.Embed(title="Successfully Added User!",
                        description=f"{ID.name} has been added successfully with permit level `{str(level)}`.",
                        color=discord.Color.gold())
    await ctx.send(embed=embed)

    database.db.close()





@client.group(aliases=['cog'])
@is_botAdmin2
async def cogs(ctx):
    pass


@cogs.command()
@is_botAdmin2
async def unload(ctx, ext):
    if "cogs." not in ext:
        ext = f"cogs.{ext}"
    if ext in get_extensions():
        client.unload_extension(ext)
        embed = discord.Embed(
            title="Cogs - Unload", description=f"Unloaded cog: {ext}", color=0xd6b4e8)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Cogs Reloaded", description=f"Cog '{ext}' not found", color=0xd6b4e8)
        await ctx.send(embed=embed)


@cogs.command()
@is_botAdmin2
async def load(ctx, ext):
    if "cogs." not in ext:
        ext = f"cogs.{ext}"
    if ext in get_extensions():
        client.load_extension(ext)
        embed = discord.Embed(title="Cogs - Load",
                            description=f"Loaded cog: {ext}", color=0xd6b4e8)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Cogs - Load", description=f"Cog '{ext}' not found.", color=0xd6b4e8)
        await ctx.send(embed=embed)


@cogs.command(aliases=['restart'])
@is_botAdmin2
async def reload(ctx, ext):
    if ext == "all":
        embed = discord.Embed(
            title="Cogs - Reload", description="Reloaded all cogs", color=0xd6b4e8)
        for extension in get_extensions():
            client.reload_extension(extension)
        await ctx.send(embed=embed)
        return

    if "cogs." not in ext:
        ext = f"cogs.{ext}"

    if ext in get_extensions():
        client.reload_extension(ext)
        embed = discord.Embed(
            title="Cogs - Reload", description=f"Reloaded cog: {ext}", color=0xd6b4e8)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Cogs - Reload", description=f"Cog '{ext}' not found.", color=0xd6b4e8)
        await ctx.send(embed=embed)


@cogs.command()
@is_botAdmin2
async def view(ctx):
    msg = " ".join(get_extensions())
    embed = discord.Embed(title="Cogs - View", description=msg, color=0xd6b4e8)
    await ctx.send(embed=embed)


@client.command()
async def ping(ctx):
    database.db.connect(reuse_if_open=True)

    q : database.Uptime =  database.Uptime.select().where(database.Uptime.id == 1).get()
    current_time = float(time.time())
    difference = int(round(current_time - float(q.UpStart)))
    text = str(timedelta(seconds=difference))

    try:
        p = subprocess.run("git describe --always", shell=True, text=True, capture_output=True, check=True)
        output = p.stdout
    except subprocess.CalledProcessError:
        output = "ERROR"

    pingembed = discord.Embed(title="Pong! ⌛", color=discord.Colour.gold(), description="Current Discord API Latency")
    pingembed.add_field(name="Current Ping:", value=f'{round(client.latency * 1000)}ms')
    pingembed.add_field(name="Uptime", value = text, inline = False)
    pingembed.add_field(name="GitHub Commit Version", value = f"`{output}`", inline = False)
    await ctx.send(embed=pingembed)

    database.db.close()


@client.command()
async def help(ctx):
    embed = discord.Embed(title="Help Command",
                          color=discord.Colour.gold())
    embed.add_field(name="[BETA] Documentation Page",
                    value="[https://timmy.schoolsimplified.org](https://timmy.schoolsimplified.org \"Masa if you see "
                          "this, ur short\")\n**Check out our new documentation! This is still a WIP, please forward any typo's or errors to Space.**")
    embed.set_footer(text="DM SpaceTurtle#0001 for any questions or concerns!")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/875233489727922177/876603875329732618/timmy_book.png?width=411&height=533")
    await ctx.send(embed=embed)

@client.command()
async def errorout(ctx):
    embed = discord.Embed(title = "Traceback Detected!", description = "**Hey you!** *Timmy here has found an error.\nYou might also want to doublecheck what you sent and/or check out the help command!*", color = 0xfc3d03)
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/875233489727922177/876610305852051456/unknown.png")
    embed.set_footer(text = f"Error: masa is short")
    await ctx.send(embed = embed)

@client.command()
@is_botAdmin2
async def kill(ctx):
    embed = discord.Embed(title = "Confirm System Abortion", description = "Please react with the appropriate emoji to confirm your choice!", color=discord.Colour.dark_orange())
    embed.add_field(name="WARNING", value="Please not that this will kill the bot immediately and it will not be online unless a developer manually starts the proccess again!\nIf you don't respond in 5 seconds, the process will automatically abort.")
    embed.set_footer(text="Abusing this system will subject your authorization removal, so choose wisely you fucking pig.")

    message = await ctx.send(embed = embed)
    
    reactions = ['✅', '❌']
    for emoji in reactions:
        await message.add_reaction(emoji)

    def check2(reaction, user):
        return user == ctx.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=5.0, check=check2)
        if str(reaction.emoji) == "❌":
            await ctx.send("Aborted Exit Process")
            await message.delete()
            return

        else:
            await message.delete()
            database.db.connect(reuse_if_open=True)
            NE = database.AdminLogging.create(discordID=ctx.author.id, action="KILL")
            NE.save()
            database.db.close()

            embed = discord.Embed(title = "Initiating System Exit...", description = "Goodbye!", color=discord.Colour.dark_orange())
            message = await ctx.send(embed = embed)

            sys.exit(0)

            
    except asyncio.TimeoutError:
        await ctx.send("Looks like you didn't react in time, automatically aborted system exit!")
        await message.delete()

@client.command()
async def gitrestart(ctx):
    await force_restart(ctx)


client.run(os.getenv("TOKEN"))
