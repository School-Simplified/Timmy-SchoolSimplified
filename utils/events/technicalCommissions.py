import asyncio
import io

import chat_exporter
import discord
from discord.ext import commands


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
            user = await self.bot.fetch_user(payload.user_id)

            if int(payload.message_id) == 873346089745514536:
            
                #developerE = discord.utils.get(guild.emojis, name = self.developerC["EmojiID"])
                discordE = discord.utils.get(guild.emojis, id = self.discordC["EmojiID"])

                    
                if payload.emoji == discordE:
                    await message.remove_reaction(str(payload.emoji), payload.member)
                    guild = self.bot.get_guild(payload.guild_id)
                    category = discord.utils.get(guild.categories, id=872911665035890708)
                    embed = discord.Embed(title = "Discord Ticket", description = f"Welcome {payload.member.mention}! A discord editor will be with you shortly.", color = discord.Color.green())

                    DE = discord.utils.get(guild.roles, name='Discord Editor')
                    DM = discord.utils.get(guild.roles, name='Discord Manager') 

                    num = len(category.channels) - 1
                    channel = await guild.create_text_channel(f'discord-{num}', category = category)

                    controlTicket = discord.Embed(title = "Control Panel", description = "To end this ticket, react to the lock emoji!", color = discord.Colour.gold())
                    await channel.send(payload.member.mention)
                    msg = await channel.send(embed = controlTicket)
                    await msg.add_reaction("🔒")

                    await channel.set_permissions(DE, send_messages = True, read_messages = True,reason="Ticket Perms")
                    await channel.set_permissions(DM, send_messages = True, read_messages = True, reason="Ticket Perms")

                    await channel.send(embed = embed)
                    return channel
            
            elif ch.category_id in self.authCategories:
                if str(payload.emoji) == "🔒":
                    TranscriptLOG = self.bot.get_channel(872915565600182282)
                    msg = await ch.send("Are you sure you want to close this ticket?")

                    reactions = ['✅', '❌']
                    for emoji in reactions:
                        await msg.add_reaction(emoji)

                    def check2(reaction, user):
                        return user == user and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌') and user is not self.bot

                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=150.0, check=check2)
                        if str(reaction.emoji) == "❌":
                            await ch.send("Canceled Ticket Removal.")

                            return await msg.delete()
                        else:
                            await message.remove_reaction("🔒", payload.member)
                            await rawExport(self, ch, TranscriptLOG)
                            await ch.delete()
                            
                    except asyncio.TimeoutError:
                        await ch.send("Looks like you didn't react in time, please try again later!")
                

            

def setup(bot):
    bot.add_cog(TechnicalTickets(bot))
