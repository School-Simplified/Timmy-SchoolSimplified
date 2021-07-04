import asyncio
import datetime
import json
import logging
from datetime import datetime, timedelta
import random

import discord
from core import database
from core.checks import is_botAdmin
from discord.ext import commands
from redbot.core.utils.tunnel import Tunnel


class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.interaction = []

        self.YolkRole = "Discord Editor"
        self.YolkID = 359029243415494656


    @commands.group(aliases=['egg'])
    @commands.has_any_role("Discord Editor", "CO")
    async def yolk(self, ctx):
        await ctx.message.delete()

        lines = open('utils/bots/CoreBot/LogFiles/yolkGIF.txt').read().splitlines()
        myline = random.choice(lines)
        await ctx.send(myline)



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





        

def setup(bot):
    bot.add_cog(SkeletonCMD(bot))



    