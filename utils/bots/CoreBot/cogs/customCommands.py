import random

import discord
from core.checks import is_botAdmin
from core.common import Emoji
from discord.ext import commands


class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.interaction = []

        self.YolkRole = "Discord Editor"
        self.YolkID = 359029243415494656

        self.myID = 852251896130699325


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





        

def setup(bot):
    bot.add_cog(SkeletonCMD(bot))



    