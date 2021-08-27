import asyncio
import io

import chat_exporter
import discord
from discord.ext import commands
from core.common import TempConfirm

async def rawExport(self, channel, response):
    transcript = await chat_exporter.export(channel, None, "EST")

    if transcript is None:
        return

    embed = discord.Embed(title = "Channel Transcript", description = f"**Channel:** {channel.name}\n*Transcript Attached Below*", color = discord.Colour.green())
    transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{channel.name}.html")

    await response.send(embed = embed)
    await response.send(file=transcript_file)


class TechnicalTickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.authCategories = [873261268495106119, 872911665035890708]
        
        self.developerC = {
            "EmojiID": 805614192865837117,
            "CategoryID": 873261268495106119
        }

        self.discordC = {
            "EmojiID": 812757175465934899,
            "CategoryID": 873261268495106119
        }


    @commands.Cog.listener("on_interaction")
    async def LockEmojiHandler(self, interaction: discord.Interaction):
        ch = self.bot.get_channel(interaction.channel_id)

        InteractionResponse = interaction.data
        print(InteractionResponse)
        if InteractionResponse['custom_id'] == 'persistent_view:tempconfirm':
            return

        if isinstance(interaction.channel, discord.PartialMessage):
            return
        
        if int(interaction.channel.category.id) in self.authCategories:
            TranscriptLOG = self.bot.get_channel(872915565600182282)
            TempConfirmInstance = TempConfirm()

            msg = await ch.send("Are you sure you want to close this ticket?", view = TempConfirmInstance)
            await TempConfirmInstance.wait()

            if TempConfirmInstance.value is None:
                await msg.delete()
                return await ch.send("Timed out, try again later.")
                
            elif not TempConfirmInstance.value:
                return await msg.delete()

            elif TempConfirmInstance.value:
                await rawExport(self, ch, TranscriptLOG)
                await ch.delete()


        
def setup(bot):
    bot.add_cog(TechnicalTickets(bot))
