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


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def embed(self, ctx):
        empty = [None, "", " "]

        def check(m):
            return m.content is not None and m.channel == ctx.channel and m.author is not self.bot.user and m.author == ctx.author


        embed = discord.Embed(title = "⏳ Starting Interactive Embed Setup", description = "Enter the embeds title here:", color = discord.Color.gold())
        embed.set_footer(text = "If you don't need a specific element, just send a blank message!")
        msg = await ctx.send(embed = embed)

        title = await self.bot.wait_for('message', check=check)

        if title in empty:
            await ctx.send("Empty Message, removing element...", delete_after=3.0)
            title = None


        embed = discord.Embed(title = "📝 Interactive Embed Setup", description = "Enter the embeds description here:", color = discord.Color.gold())
        embed.set_footer(text = "If you don't need a specific element, just send a blank message!")
        await msg.edit(embed = embed)

        title = await self.bot.wait_for('message', check=check)

        if title in empty:
            await ctx.send("Empty Message, removing element...", delete_after=3.0)
            title = None
            

        

        





        

def setup(bot):
    bot.add_cog(SkeletonCMD(bot))



    