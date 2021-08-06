import datetime
import io
import json
import logging
from datetime import datetime, timedelta

import chat_exporter
import discord
from chat_exporter.chat_exporter import Transcript
from core import database
from discord.ext import commands


async def createChannel(self, payload, type, *args):
    
    if type == "Developer":
        guild = await self.bot.fetch_guild(payload.guild_id)
        category = discord.utils.get(guild.categories, id= 873261268495106119)
        embed = discord.Embed(title = "Developer Ticket", description = f"Welcome {payload.member.mention}! A developer will be with you shortly.", color = discord.Color.green())

    elif type == "Discord":
        guild = await self.bot.fetch_guild(payload.guild_id)
        category = discord.utils.get(guild.categories, id= 872911665035890708)
        embed = discord.Embed(title = "Discord Ticket", description = f"Welcome {payload.member.mention}! A discord editor will be with you shortly.", color = discord.Color.green())

    else:
        return BaseException("ERROR: unknown type")

    DE = discord.utils.get(guild.roles, name='Discord Editor')
    DM = discord.utils.get(guild.roles, name='Discord Manager') 

    DDM = discord.utils.get(guild.roles, name='Developer Manager')
    ADT = discord.utils.get(guild.roles, name='Assistant Developer Manager')
    DT = discord.utils.get(guild.roles, name='Developer')

    num = len(category.channels)
    channel = await guild.create_text_channel(f'{type}-{num}', category = category)

    controlTicket = discord.Embed(title = "Control Panel", description = "To end this ticket, react to the lock emoji!", color = discord.Colour.gold())
    await channel.send(payload.member.mention)
    msg = await channel.send(embed = controlTicket)
    await msg.add_reaction("🔒")

    await channel.set_permissions(DE, send_messages = True, read_messages = True,reason="Ticket Perms")
    await channel.set_permissions(DM, send_messages = True, read_messages = True, reason="Ticket Perms")

    await channel.set_permissions(DDM, send_messages = True, read_messages = True, reason="Ticket Perms")
    await channel.set_permissions(ADT, send_messages = True, read_messages = True, reason="Ticket Perms")
    await channel.set_permissions(DT, send_messages = True, read_messages = True, reason="Ticket Perms")

    await channel.send(embed = embed)
    return channel


async def rawExport(self, channel, response):
    transcript = await chat_exporter.export(channel)

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


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.bot.user.id:
            ch = self.bot.get_channel(payload.channel_id)
            guild = self.bot.get_guild(payload.guild_id)
            message = await ch.fetch_message(payload.message_id)
            
            developerE = discord.utils.get(guild.emojis, name = self.developerC["EmojiID"])
            discordE = discord.utils.get(guild.emojis, name = self.discordC["EmojiID"])
            
            if str(payload.emoji) == "🔒":
                if ch.category_id in self.authCategories:
                    TranscriptLOG = self.bot.get_channel(872915565600182282)
                    
                    await message.remove_reaction("🔒", payload.member)
                    await rawExport(ch, TranscriptLOG)
                    await ch.delete()


            elif payload.emoji == developerE and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "Developer")

                await channel.send()

                
            elif payload.emoji == discordE and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "Discord")

                await channel.send()
                

            

def setup(bot):
    bot.add_cog(TechnicalTickets(bot))
