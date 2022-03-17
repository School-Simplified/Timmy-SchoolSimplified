from datetime import datetime

import discord
import pytz
from core import database
from discord.ext import commands, tasks

eventGIFs = ['https://cdn.discordapp.com/attachments/953650689731592282/953716378601390080/IMG_0011.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953716378894999642/IMG_0013.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953716379104727090/IMG_0012.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953711617466564718/IMG_0017.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953711636575846420/IMG_0016.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953711644184289360/IMG_0015.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953711689902198824/IMG_0014.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953711052363816991/IMG_0021.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953711052623867974/IMG_0020.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953711053240414279/IMG_0019.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953711053471088680/IMG_0018.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953710650591436810/IMG_0024.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953710650859855922/IMG_0025.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953710656379564102/IMG_0022.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953710656580898906/IMG_0023.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953710126227935232/IMG_0029.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953710126467014686/IMG_0028.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953710126664151120/IMG_0026.png', 'https://cdn.discordapp.com/attachments/953650689731592282/953710126911590400/IMG_0027.png']

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
        hour = int(datetime_NY.strftime("%I"))
        amORpm = datetime_NY.strftime("%p")
        print(hour)

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
