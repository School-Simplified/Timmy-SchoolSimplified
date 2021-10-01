import json
import logging
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from difflib import get_close_matches
from pathlib import Path

import chat_exporter
import discord
import requests
from discord.app import Option
from discord.ext import commands
from discord_sentry_reporting import use_sentry
from dotenv import load_dotenv
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from tqdm import tqdm

from core import database
from core.common import Emoji, LockButton, bcolors, getGuildList
from core.WebServer import keep_alive
from utils.bots.CoreBot.cogs.tictactoe import TicTacToe, TicTacToeButton
from utils.events.VerificationStaff import VerifyButton

load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class Timmy(commands.Bot):
    async def is_owner(self, user: discord.User):
        adminIDs = []

        query = database.Administrators.select().where(database.Administrators.TierLevel >= 3)
        for admin in query:
            adminIDs.append(admin.discordID)

        if user.id in adminIDs:
            return True

        return await super().is_owner(user)

bot = Timmy(
    command_prefix=commands.when_mentioned_or('+'), 
    intents=discord.Intents.all(), 
    case_insensitive=True, 
    activity = discord.Activity(type=discord.ActivityType.watching, name="+help | timmy.schoolsimplified.org")
)
bot.remove_command('help')

if os.getenv('DSN_SENTRY') != None:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )

    use_sentry(
        bot,  # Traceback tracking, DO NOT MODIFY THIS
        dsn=os.getenv('DSN_SENTRY'),
        traces_sample_rate=1.0,
        integrations=[FlaskIntegration(), sentry_logging]
    )

publicCH = [763121170324783146, 800163651805773824, 774847738239385650, 805299289604620328, 796909060707319838, 787841402381139979, 830992617491529758, 763857608964046899, 808020719530410014]
TechGuild = 805593783684562965
TracebackChannel = 851949397533392936

#Start Check
UpQ = database.Uptime.select().where(database.Uptime.id == 1)
CIQ = database.CheckInformation.select().where(database.CheckInformation.id == 1)
if not UpQ.exists():
    database.Uptime.create(UpStart = "1")
    print("Created Uptime Entry.")

if not CIQ.exists():
    database.CheckInformation.create(MasterMaintenance = False, guildNone = False, externalGuild = True, ModRoleBypass = True, ruleBypass = True, publicCategory = True, elseSituation = True, PersistantChange = False)
    print("Created CheckInformation Entry.")

if len(database.Administrators) == 0:
    database.Administrators.create(discordID = 13, TierLevel = 4)
    print("Added you as a bot administrator")

database.db.connect(reuse_if_open=True)
q :database.Uptime =  database.Uptime.select().where(database.Uptime.id == 1).get()
q.UpStart = time.time()
q.save()

query: database.CheckInformation = database.CheckInformation.select().where(database.CheckInformation.id == 1).get()
query.PersistantChange = False
query.save()
database.db.close()


keep_alive()

def get_extensions():
    extensions = []
    extensions.append('jishaku')
    for file in Path("utils").glob("**/*.py"):
        if "!" in file.name or "DEV" in file.name:
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



@bot.slash_command(description = "Play a game of TicTacToe with someone!", guild_ids=getGuildList(bot, exemptServer=[876651621826834473]))
async def tictactoe(ctx: discord.InteractionContext, user: Option(discord.Member, "Enter an opponent you want")):
    if user == None:
        return await ctx.send("lonely :(, sorry but you need a person to play against!")
    elif user == bot.user:
        return await ctx.send("i'm good.")
    elif user == ctx.author:
        return await ctx.send("lonely :(, sorry but you need an actual person to play against, not yourself!")

    if ctx.channel.id == 763121180173271040:
        return await ctx.send(f"{ctx.author.mention}\nMove to <#783319554322989067> to play Tic Tac Toe!", ephemeral=True)
        

    await ctx.send(f'Tic Tac Toe: {ctx.author.mention} goes first', view=TicTacToe(ctx.author, user))



@bot.user_command(name = "Are they short?", guild_ids=getGuildList(bot, exemptServer=[876651621826834473]))  
async def short(ctx, member: discord.Member):  
    if member.id == 736765405728735232 or member.id == 518581570152693771 or member.id == 544724467709116457:
        await ctx.respond(f"{member.mention} is short!")
    else:
        await ctx.respond(f"{member.mention} is tall!")


@bot.slash_command(description = "Check's if a user is short!", guild_ids=getGuildList(bot, exemptServer=[876651621826834473]))  
async def short_detector(ctx, member: Option(discord.Member, "Enter a user you want to check!")):  
    if member.id == 736765405728735232 or member.id == 518581570152693771 or member.id == 544724467709116457:
        await ctx.respond(f"{member.mention} is short!")
    else:
        await ctx.respond(f"{member.mention} is tall!")


@bot.user_command(name = "Play TicTacToe with them!", guild_ids=getGuildList(bot, exemptServer=[876651621826834473]))  
async def tictactoeCTX(ctx, member: discord.Member):  
    if member == None:
        return await ctx.send("lonely :(, sorry but you need a person to play against!")
    elif member == bot.user:
        return await ctx.send("i'm good.")
    elif member == ctx.author:
        return await ctx.send("lonely :(, sorry but you need an actual person to play against, not yourself!")

    if ctx.channel.id == 763121180173271040:
        return await ctx.send(f"{ctx.author.mention}\nMove to <#783319554322989067> to play Tic Tac Toe!", ephemeral=True)
        

    await ctx.send(f'Tic Tac Toe: {ctx.author.mention} goes first', view=TicTacToe(ctx.author, member))


@bot.event
async def on_ready():
    now = datetime.now()
    query: database.CheckInformation = database.CheckInformation.select().where(database.CheckInformation.id == 1).get()
    
    if not query.PersistantChange:
        bot.add_view(LockButton(bot))
        bot.add_view(VerifyButton())
        query.PersistantChange = True
        query.save()
        

    print(f"Logged in as: {bot.user.name}")
    print(f"{bcolors.OKBLUE}CONNECTED TO DISCORD{bcolors.ENDC}")
    print(f"{bcolors.WARNING}Current Discord.py Version: {discord.__version__}{bcolors.ENDC}")
    print(f"{bcolors.WARNING}Current Time: {now}{bcolors.ENDC}")

    chat_exporter.init_exporter(bot)




files = get_extensions()
i = 0 
capLimit = len(files)
ext = files[i]

for i in tqdm(range(capLimit - 1), ascii = True, desc =f"Loading Cogs..."):
    try:
        bot.load_extension(ext)
    except (commands.errors.ExtensionAlreadyLoaded, commands.ExtensionAlreadyLoaded):
        bot.unload_extension(ext)
        bot.load_extension(ext)
    except commands.ExtensionNotFound:
        raise commands.ExtensionNotFound(ext)

    i+=1
    if i >= capLimit:
        break
    else:
        ext = files[i]


@bot.check
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

@bot.event
async def on_command_error(ctx, error: Exception):
    tb = error.__traceback__
    etype = type(error)
    exception = traceback.format_exception(etype, error, tb, chain=True)
    exception_msg = ""
    for line in exception:
        exception_msg += line
    
    error = getattr(error, 'original', error)
    if ctx.command != None:
        if ctx.command.name == "rule":
            return "No Rule..."
    
    if isinstance(error, (commands.CheckFailure, commands.CheckAnyFailure)):
        return

    if hasattr(ctx.command, 'on_error'):
        return

    elif isinstance(error, (commands.CommandNotFound, commands.errors.CommandNotFound)):
        cmd = ctx.invoked_with
        cmds = [cmd.name for cmd in bot.commands]

        #embed = discord.Embed(title = "Slash Commands", description = "<:slash:881421972607758346> Please use slash commands! Simply hit `/` in your chat bar and type out a command you want to execute.\n**Demo:** https://gyazo.com/eda5bb58c17d2e50d6e52efc314cdee2", color = discord.Color.blue())
        #return await ctx.send(embed = embed)
        #await ctx.send("Woah! Timmy no longer supports commands with the `+` prefix. ")
        matches = get_close_matches(cmd, cmds)

        if len(matches) > 0:
            return await ctx.send(f'Command "{cmd}" not found, maybe you meant "{matches[0]}"?')
        else:
            return await ctx.send(f'Command "{cmd}" not found, use the help command to know what commands are available')

    elif isinstance(error, (commands.MissingRequiredArgument, commands.TooManyArguments)):
        signature = f"{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}"

        if ctx.command.name == "schedule":
            em = discord.Embed(title = "Missing/Extra Required Arguments Passed In!", description = "Looks like you messed up an argument somewhere here!\n\n**Check the following:**\n-> If you seperated the time and the AM/PM. (Eg; 5:00 PM)\n-> If you provided a valid student's ID\n-> If you followed the MM/DD Format.\n-> Keep all the arguments in one word.\n-> If you followed the [documentation for schedule.](https://timmy.schoolsimplified.org/tutorbot#schedule)", color = 0xf5160a)
            em.set_thumbnail(url = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
            em.set_footer(text = "Consult the Help Command if you are having trouble or call over a Bot Manager!")
            return await ctx.send(embed = em)
        else:
            em = discord.Embed(title = "Missing/Extra Required Arguments Passed In!",
                               description = "You have missed one or several arguments in this command"
                                             "\n\nUsage:"
                                             f"\n`{signature}`", color = 0xf5160a)
            em.set_thumbnail(url = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
            em.set_footer(text = "Consult the Help Command if you are having trouble or call over a Bot Manager!")
            return await ctx.send(embed = em)

    elif isinstance(error, (commands.MissingAnyRole, commands.MissingRole, commands.MissingPermissions, commands.errors.MissingAnyRole, commands.errors.MissingRole, commands.errors.MissingPermissions)):
        em = discord.Embed(title = "Invalid Permissions!", description = "You do not have the associated role in order to successfully invoke this command! Contact an administrator/developer if you believe this is invalid.", color = 0xf5160a)
        em.set_thumbnail(url = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
        em.set_footer(text = "Consult the Help Command if you are having trouble or call over a Bot Manager!")
        await ctx.send(embed = em)
        return

    elif isinstance(error, commands.BadArgument):
        print(ctx.command.name)
        if ctx.command.name == "schedule":
            em = discord.Embed(title = "Bad Argument!", description = "Looks like you messed up an argument somewhere here!\n\n**Check the following:**\n-> If you seperated the time and the AM/PM. (Eg; 5:00 PM)\n-> If you provided a valid student's ID\n-> If you followed the MM/DD Format.\n-> Keep all the arguments in one word.\n-> If you followed the [documentation for schedule.](https://timmy.schoolsimplified.org/tutorbot#schedule)", color = 0xf5160a)
            em.set_thumbnail(url = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
            em.set_footer(text = "Consult the Help Command if you are having trouble or call over a Bot Manager!")
            return await ctx.send(embed = em)
        else:
            em = discord.Embed(title = "Bad Argument!", description = "Unable to parse arguments, check what arguments you provided.", color = 0xf5160a)
            em.set_thumbnail(url = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
            em.set_footer(text = "Consult the Help Command if you are having trouble or call over a Bot Manager!")
            return await ctx.send(embed = em)

    elif isinstance(error, (commands.CommandOnCooldown, commands.errors.CommandOnCooldown)):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)

        msg = "This command cannot be used again for {} minutes and {} seconds" \
            .format(round(m), round(s))

        embed = discord.Embed(title = "Command On Cooldown", description = msg, color = discord.Color.red())
        return await ctx.send(embed = embed)
        


    else:
        error_file = Path("error.txt")
        error_file.touch()
        with error_file.open("w") as f:
            f.write(exception_msg)
        with error_file.open("r") as f:
            #config, _ = core.common.load_config()
            data = "\n".join([l.strip() for l in f])

            GITHUB_API="https://api.github.com"
            API_TOKEN= os.getenv('GIST')
            url=GITHUB_API+"/gists"
            print(f"Request URL: {url}")                    
            headers={'Authorization':'token %s'%API_TOKEN}
            params={'scope':'gist'}
            payload={"description":"Timmy encountered a Traceback!","public":True,"files":{"error":{"content": f"{data}"}}}
            res=requests.post(url,headers=headers,params=params,data=json.dumps(payload))
            j=json.loads(res.text)
            ID = j['id']
            gisturl = f"https://gist.github.com/{ID}"
            print(gisturl)

            permitlist = []
            query = database.Administrators.select().where(database.Administrators.TierLevel >= 3)
            for user in query:
                permitlist.append(user.discordID)

            if ctx.author.id not in permitlist:
                embed = discord.Embed(title = "Traceback Detected!", description = "Timmy here has ran into an error!\nPlease check what you sent and/or check out the help command!", color = 0xfc3d03)
                embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/875233489727922177/876610305852051456/unknown.png")
                embed.set_footer(text = f"Error: {str(error)}")
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(title = "Traceback Detected!", description = "Timmy here has ran into an error!\nTraceback has been attached below.", color = 0xfc3d03)
                embed.add_field(name = "GIST URL", value = gisturl)
                embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/875233489727922177/876610305852051456/unknown.png")
                embed.set_footer(text = f"Error: {str(error)}")
                await ctx.send(embed = embed)

            guild = bot.get_guild(TechGuild)
            channel = guild.get_channel(TracebackChannel)

            embed2 = discord.Embed(title = "Traceback Detected!", description = f"**Information**\n**Server:** {ctx.message.guild.name}\n**User:** {ctx.message.author.mention}\n**Command:** {ctx.command.name}", color= 0xfc3d03)
            embed2.add_field(name = "Gist URL", value = f"[Uploaded Traceback to GIST](https://gist.github.com/{ID})")
            await channel.send(embed = embed2)

            error_file.unlink()

    raise error

bot.run(os.getenv('TOKEN'))
