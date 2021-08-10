import asyncio
import datetime
import json
import logging
from datetime import datetime, timedelta

import discord
from core import database
from core.checks import is_botAdmin
from discord.ext import commands
from gtts import gTTS


class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_botAdmin
    async def say(self, ctx, *, message):
        NE = database.AdminLogging.create(discordID = ctx.author.id, action = "SAY", content = message)
        NE.save()

        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    @is_botAdmin
    async def sayvc(self, ctx, *, text=None):
        NE = database.AdminLogging.create(discordID = ctx.author.id, action = "SAYVC", content = text)
        NE.save()
        
        await ctx.message.delete()

        if not text:
            # We have nothing to speak
            await ctx.send(f"Hey {ctx.author.mention}, I need to know what to say please.")
            return

        vc = ctx.voice_client # We use it more then once, so make it an easy variable
        if not vc:
            # We are not currently in a voice channel
            await ctx.send("I need to be in a voice channel to do this, please use the connect command.")
            return

        # Lets prepare our text, and then save the audio file
        tts = gTTS(text=text, lang="en")
        tts.save("text.mp3")

        try:
            # Lets play that mp3 file in the voice channel
            vc.play(discord.FFmpegPCMAudio('text.mp3'), after=lambda e: print(f"Finished playing: {e}"))

            # Lets set the volume to 1
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = 1

        # Handle the exceptions that can occur
        except discord.ClientException as e:
            await ctx.send(f"A client exception occured:\n`{e}`")

        except TypeError as e:
            await ctx.send(f"TypeError exception:\n`{e}`")

def setup(bot):
    bot.add_cog(SkeletonCMD(bot))



    