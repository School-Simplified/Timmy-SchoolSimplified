import datetime
import json
from datetime import datetime, timedelta

import discord
from core.checks import is_botAdmin
from core.common import *
from discord import embeds
from discord.ext import commands


class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def view(self, ctx):
        with open('utils/bots/RoleSync/equelRoles.json', 'r') as content_file:
            content = content_file.read()

        await ctx.send("**JSON File**")
        await ctx.send(f"```json\n{content}\n```")

def setup(bot):
    bot.add_cog(SkeletonCMD(bot))
