import os

import discord
from core import database
from core.checks import is_botAdmin
from discord.ext import commands
from google.cloud import texttospeech
from gtts import gTTS
from oauth2client.service_account import ServiceAccountCredentials

from core.common import access_secret


class SayCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_botAdmin
    async def say(self, ctx, *, message):
        NE = database.AdminLogging.create(
            discordID=ctx.author.id, action="SAY", content=message
        )
        NE.save()

        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    @is_botAdmin
    async def sayvc(self, ctx, *, text=None):
        await ctx.message.delete()

        if not text:
            # We have nothing to speak
            await ctx.send(
                f"Hey {ctx.author.mention}, I need to know what to say please."
            )
            return

        vc = ctx.voice_client  # We use it more then once, so make it an easy variable
        if not vc:
            # We are not currently in a voice channel
            await ctx.send(
                "I need to be in a voice channel to do this, please use the connect command."
            )
            return

        NE = database.AdminLogging.create(
            discordID=ctx.author.id, action="SAYVC", content=text
        )
        NE.save()

        # Lets prepare our text, and then save the audio file
        TTSClient = texttospeech.TextToSpeechClient(
            credentials=access_secret("ttscreds", True, 2)
        )

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = TTSClient.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with open("text.mp3", "wb") as out:
            out.write(response.audio_content)

        try:
            vc.play(
                discord.FFmpegPCMAudio("text.mp3"),
                after=lambda e: print(f"Finished playing: {e}"),
            )

            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = 1

        except discord.ClientException as e:
            await ctx.send(f"A client exception occurred:\n`{e}`")

        except TypeError as e:
            await ctx.send(f"TypeError exception:\n`{e}`")


def setup(bot):
    bot.add_cog(SayCMD(bot))
