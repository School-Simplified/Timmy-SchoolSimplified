import discord
from core import database
from discord.ext import commands, tasks
from datetime import datetime
import pytz

class TutorBotLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=60.0)
    async def voiceCheck(self):
        now = datetime.now()
        query = database.TutorBot_Sessions.select().where()

def setup(bot):
    bot.add_cog(TutorBotLoop(bot))


