import asyncio
import os
import random
import subprocess
import sys
import time
from datetime import timedelta

import discord
from core import database
from core.checks import is_botAdmin, is_botAdmin2
from core.common import ClubPingDropdownView, Emoji, HelpView, NitroConfirmFake
from discord.ext import commands
from dotenv import load_dotenv
from main import force_restart2
from sentry_sdk import Hub
import psutil

load_dotenv()

class MiscCMD(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.interaction = []

        self.YolkRole = "Discord Editor"
        self.YolkID = 359029243415494656

        self.myID = 852251896130699325
        self.client = Hub.current.client

        self.whitelistedRoles = [883169286665936996, 883170141771272294, 883170072355561483, 883162279904960562, 883564455219306526, 883564487813234738, 883162511560560720, 883169000866070539, 883170166161149983]

        self.decodeDict = {
            "['Simplified Coding Club']": 883169286665936996,
            "['Simplified Debate Club']": 883170141771272294,
            "['Simplified Music Club']": 883170072355561483,
            "['Simplified Cooking Club']": 883162279904960562,
            "['Simplified Chess Club']": 883564455219306526,
            "['Simplified GameDev Club']": 883564487813234738,
            "['Simplified Book Club']": 883162511560560720,
            "['Simplified Advocacy Club']": 883169000866070539,
            "['Simplified Speech Club']": 883170166161149983
        }


    @commands.group(aliases=['egg'])
    @commands.has_any_role("Discord Editor", "CO")
    async def yolk(self, ctx):
        await ctx.message.delete()

        lines = open('utils/bots/CoreBot/LogFiles/yolkGIF.txt').read().splitlines()
        myline = random.choice(lines)
        await ctx.send(myline)

    @commands.command()
    @is_botAdmin
    async def pingmasa(self,ctx, *, msg = None):
        masa = await self.bot.fetch_user(736765405728735232)
        if msg is not None:
            await ctx.send(masa.mention + f" {msg}")
        else:
            await ctx.send(masa.mention)


    @yolk.command(invoke_without_command=True)
    async def add(self, ctx, *, line):
        #await ctx.message.delete()

        if ctx.author.id != self.YolkID:
            return

        file_object = open('utils/bots/CoreBot/LogFiles/yolkGIF.txt', 'a')
        file_object.write(line)

        await ctx.send(f"Added {line}")

    
    @commands.command()
    async def obama(self,ctx):
        await ctx.message.delete()

        lines = open('utils/bots/CoreBot/LogFiles/obamaGIF.txt').read().splitlines()
        myline = random.choice(lines)
        await ctx.send(myline)


    @commands.command()
    @commands.has_any_role("Moderator")
    async def countban(self, ctx, member: discord.Member, *, reason = None):
        NoCount = discord.utils.get(ctx.guild.roles, name = "NoCounting")
    

        if member.id == self.myID:
            embed = discord.Embed(title = "Unable to CountBan this User", description = "Why are you trying to CountBan me?", color = 0xed1313)
            return await ctx.send(embed = embed)
            

        if member.id == ctx.author.id:
            embed = discord.Embed(title = "Unable to CountBan this User", description = "Why are you trying to CountBan yourself?", color = 0xed1313)
            return await ctx.send(embed = embed)

            

        
        if NoCount not in member.roles:
            try:
                if reason == None:
                    await ctx.send("Please specify a reason for this Count Ban!")
                    return

                UpdateReason = f"CountBan requested by {ctx.author.display_name} | Reason: {reason}"
                await member.add_roles(NoCount, reason = UpdateReason)
            except Exception as e:
                await ctx.send(f"ERROR:\n{e}")
                print(e)
            else:
                embed = discord.Embed(title = "Count Banned!", description = f"{Emoji.confirm} {member.display_name} has been count banned!\n{Emoji.barrow} **Reason:** {reason}", color = 0xeffa16)
                await ctx.send(embed = embed)

        else:
            try:
                if reason == None:
                    reason = "No Reason Given"

                UpdateReason = f"Count UnBan requested by {ctx.author.display_name} | Reason: {reason}"
                await member.remove_roles(NoCount, reason = UpdateReason)
            except Exception as e:
                await ctx.send(f"ERROR:\n{e}")
            else:
                embed = discord.Embed(title = "Count Unbanned!", description = f"{Emoji.confirm} {member.display_name} has been count unbanned!\n{Emoji.barrow} **Reason:** {reason}", color = 0xeffa16)
                await ctx.send(embed = embed)

    @commands.command()
    async def join(self, ctx, vc:discord.VoiceChannel):
        await vc.connect()
        await ctx.send("ok i did join")   
        

    @commands.command()
    async def ping(self, ctx):
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
        pingembed.set_author(name = "Timmy", url = "https://i.gyazo.com/5cffb6cd45e5e1ee9b1d015bccbdf9e6.png", icon_url = "https://i.gyazo.com/a0b221679db0f980504e64535885a5fd.png")
        pingembed.add_field(name="Ping & Uptime:", value=f'```diff\n+ Ping: {round(self.bot.latency * 1000)}ms\n+ Uptime: {text}\n```')

        pingembed.add_field(name="System Resource Usage", value = f"```diff\n- CPU Usage: {psutil.cpu_percent()}%\n- Memory Usage: {psutil.virtual_memory().percent}%\n```", inline = False)
        pingembed.set_footer(text = f"GitHub Commit Version: {output}", icon_url = ctx.author.avatar.url)
    
        await ctx.send(embed=pingembed)

        database.db.close()


    @commands.command()
    async def help(self, ctx):
        emoji = discord.utils.get(self.bot.emojis, id = 880875405962264667)

        embed = discord.Embed(title="Help Command",
                            color=discord.Colour.gold())
        embed.add_field(name="Documentation Page",
                        value="Click the button below to visit the documentation!")
        embed.set_footer(text="DM SpaceTurtle#0001 for any questions or concerns!")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/875233489727922177/876603875329732618/timmy_book.png?width=411&height=533")
        await ctx.send(embed=embed, view = HelpView(emoji))

    @commands.command()
    async def nitro(self, ctx: commands.Context):
        await ctx.message.delete()

        embed = discord.Embed(title = "A WILD GIFT APPEARS!", description = "**Nitro:**\nExpires in 48 hours.", color = 0x2F3136)
        embed.set_thumbnail(url = "https://i.imgur.com/w9aiD6F.png")
        await ctx.send(embed = embed, view = NitroConfirmFake())


    @commands.command()
    @is_botAdmin2
    async def kill(self, ctx):
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
            reaction, user = await self.bot.wait_for('reaction_add', timeout=5.0, check=check2)
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

                if self.client is not None:
                    self.client.close(timeout=2.0)

                embed = discord.Embed(title = "Initiating System Exit...", description = "Goodbye!", color=discord.Colour.dark_orange())
                message = await ctx.send(embed = embed)

                sys.exit(0)

                
        except asyncio.TimeoutError:
            await ctx.send("Looks like you didn't react in time, automatically aborted system exit!")
            await message.delete()


    @commands.command()
    @is_botAdmin2
    async def gitpull(self, ctx, mode = "-a"):
        output = ''

        try:
            p = subprocess.run("git fetch --all", shell=True, text=True, capture_output=True, check=True)
            output += p.stdout
        except Exception as e:
            await ctx.send("⛔️ Unable to fetch the Current Repo Header!")
            await ctx.send(f"**Error:**\n{e}")
        try:
            p = subprocess.run("git reset --hard origin/main", shell=True, text=True, capture_output=True, check=True)
            output += p.stdout
        except Exception as e:
            await ctx.send("⛔️ Unable to apply changes!")
            await ctx.send(f"**Error:**\n{e}")

        embed = discord.Embed(title = "GitHub Local Reset", description = "Local Files changed to match Timmy/main", color = 0x3af250)
        embed.add_field(name = "Shell Output", value = f"```shell\n$ {output}\n```")
        embed.set_footer(text = "Attempting to restart the bot...")
        await ctx.send(embed=embed)

        if mode == "-a":
            await force_restart2(ctx)
        elif mode == "-c":
            await ctx.invoke(self.bot.get_command('cogs reload'), ext='all')



    @commands.command()
    @is_botAdmin2
    async def numbergame(self, ctx):
        await ctx.message.delete()
        def check(m):
            return m.content is not None and m.channel == ctx.channel and m.author is not self.bot.user

        randomnum = random.randint(0,10)
        print(randomnum)

        userinput = None
        userObj = None

        await ctx.send("Guess my number (between 0 and 10) and if you get it right you can change my status to whatever you want!")

        while userinput != str(randomnum):
            inputMSG = await self.bot.wait_for('message', check=check)
            userinput = inputMSG.content
            userObj = inputMSG.author

        await ctx.send(f"{userObj.mention}, you guessed it!\nWhat do you want my status to be?")


    @commands.command()
    @commands.has_role(883160826180173895)
    async def role(self, 
        ctx: commands.Context, 
        users: commands.Greedy[discord.Member], 
        roles: commands.Greedy[discord.Role]
    ):
        """Role Command
        Gives an authorized role to every user provided.

        Requires: 
            Club President Role to be present on the user.

        Args:
            ctx (commands.Context): Context
            users (commands.Greedy[discord.User]): List of Users
            roles (commands.Greedy[discord.Role]): List of Roles
        """
        embed = discord.Embed(
            title = "Starting Mass Role Function",
            description = "Please wait until I finish the role operation, you'll see this message update when I am finished!", 
            color = discord.Color.gold()
        )

        msg = await ctx.send(embed = embed)

        for role in roles:
            if role.id not in self.whitelistedRoles:
                await ctx.send(f"Role: `{role}` is not whitelisted for this command, removing `{role}`.")

                roles = [value for value in roles if value != role]
                break

        for user in users:
            for role in roles:
                await user.add_roles(role, reason = f"Mass Role Operation requested by {ctx.author.name}.")
                
        embed = discord.Embed(
            title = "Mass Role Operation Complete", 
            description = f"I have given `{str(len(users))}` users `{str(len(roles))}` roles.", 
            color = discord.Color.green()
        )

        UserList = []
        RoleList = []
        
        for user in users:
            UserList.append(user.mention)
        for role in roles:
            RoleList.append(role.mention)
        
        UserList = ", ".join(UserList)
        RoleList = ", ".join(RoleList)

        embed.add_field(
            name = "Detailed Results", 
            value = f"{Emoji.person}: {UserList}\n\n{Emoji.activity}: {RoleList}\n\n**Status:**  {Emoji.confirm}"
        )
        embed.set_footer(text = "Completed Operation")

        await msg.edit(embed = embed)

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.role)
    async def clubping(self, ctx: commands.Context, *, message = ""):
        view = ClubPingDropdownView()
        msg = await ctx.send("Select a role you want to ping!", view = view)
        await view.wait()
        await msg.delete()

        ViewResponse = str(view.children[0].values)
        RoleID = self.decodeDict[ViewResponse]
        await ctx.send(f"<@&{RoleID}>\n{message}")



def setup(bot):
    bot.add_cog(MiscCMD(bot))



    