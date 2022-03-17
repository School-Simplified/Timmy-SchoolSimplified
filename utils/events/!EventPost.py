from datetime import datetime

import discord
import pytz
from core import database
from core.common import eventGIFs
from discord.ext import commands, tasks

class EventsTeam(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.EVENT_POST.start()

    def cog_unload(self):
        self.EVENT_POST.cancel()

    @tasks.loop(minutes=30.0)
    async def EVENT_POST(self):
        """
        Create a task loop to make sure threads don't automatically archive due to inactivity.
        """
        datetime_NY = datetime.now(pytz.timezone('America/New_York'))
        hour = int(datetime_NY.strftime("%H"))
        print(hour)

        if hour >= 10:
            channel: discord.TextChannel = await self.bot.fetch_channel(
                951302954965692436
            )

            q = database.BaseQueue.select().where(database.BaseQueue.id == 1)
            if q.exists(): 
                q = q.get()
                if q.queueID > 19:
                    return
                ML_ID = int(q.queueID)
                print(ML_ID)
                await channel.send(eventGIFs[ML_ID])
                q.queueID = q.queueID + 1
                q.save()



def setup(bot):
    bot.add_cog(EventsTeam(bot))
