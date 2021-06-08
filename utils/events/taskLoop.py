import discord
import inspect
import io
import textwrap
import traceback
from contextlib import redirect_stdout
import os
import aiohttp
from discord.ext import commands, tasks
'''
Used by TutorVC
'''

class TasksLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voiceCheck.start()
        

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=3.0)
    async def voiceCheck(self):
        guild = await self.bot.fetch_guild(763119924385939498)
        #botVoiceState = guild.get_member(842468709406081034)

        voice = discord.utils.get(self.bot.voice_clients, guild=guild)

        if voice == None:
            voiceChannel = await self.bot.fetch_channel(784556875487248394)
            global vc
            try:
                vc = await voiceChannel.connect()
            except Exception as e:
                print(e)
        else:
            pass

    @voiceCheck.before_loop
    async def before_printer(self):
        print('Preparing Loop...')
        await self.bot.wait_until_ready()



def setup(bot):
    bot.add_cog(TasksLoop(bot))