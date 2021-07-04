import inspect
import io
import textwrap
import traceback
from contextlib import redirect_stdout
import os
import aiohttp
from discord.ext import commands
import discord
from discord.ext import tasks
from datetime import timedelta, datetime


MESSAGEC = "Go chit chat somewhere else, this is for commands only."
MESSAGEMASA = "Hey you ||~~short~~|| *I mean* tall mf, go chit chat somewhere you twat."


class CommandsOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.masa_id = 736765405728735232
        self.channelID = 786057630383865858

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == 786057630383865858 and not message.author.bot:

            if message.content.startswith('?') or message.content.startswith('+'):
                pass


            else:
                await message.delete()
                if message.author.id == self.masa_id:
                    embed = discord.Embed(
                        title="Commands ONLY", description=MESSAGEMASA, color=discord.Colour.red())
                else:
                    embed = discord.Embed(
                        title="Commands ONLY", description=MESSAGEC, color=discord.Colour.red())

                await message.channel.send(message.author.mention, embed=embed, delete_after=5.0)



def setup(bot):
    bot.add_cog(CommandsOnly(bot))