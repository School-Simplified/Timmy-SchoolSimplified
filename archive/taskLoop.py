import inspect
import io
import os
import textwrap
import traceback
from contextlib import redirect_stdout

import aiohttp
import discord
from discord.ext import commands, tasks

'''
Used by TutorVC
'''

class TasksLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #self.voiceCheck.start()
        self.MainServerID = 763119924385939498
        self.TutorVCStartCH = 784556875487248394
        

    def cog_unload(self):
        self.voiceCheck.cancel()

    @tasks.loop(seconds=15.0)
    async def voiceCheck(self):
        return
        
        # This is closed off due to voice instability
        
        guild = await self.bot.fetch_guild(self.MainServerID)

        voice = discord.utils.get(self.bot.voice_clients, guild=guild)
        if voice == None:
            voiceChannel = await self.bot.fetch_channel(self.TutorVCStartCH)
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
