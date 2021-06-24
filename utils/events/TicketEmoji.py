import datetime
import json
import logging
from datetime import datetime, timedelta

import discord
from chat_exporter.chat_exporter import Transcript
from core import database
from discord.ext import commands
from utils.bots.StaffInformation.cogs.ticketv2 import createChannel, rawExport


class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.authCategories = [836005981497327616, 836006081159102474, 836006123952930847, 836006174431379476, 836006227410419742, 836006262440460369, 836006311417348128, 836006373984436255 , 836006426497384449]


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.bot.user.id:
            ch = self.bot.get_channel(payload.channel_id)
            guild = self.bot.get_guild(payload.guild_id)
            message = await ch.fetch_message(payload.message_id)
            #chatHelperRole = discord.utils.get(guild.roles, name='Helper')
            database.db.connect(reuse_if_open=True)
            query = database.Response.select().where(database.Response.id == 1).get()



            if str(payload.emoji) == "🔒":
                if ch.category_id in self.authCategories:
                    TranscriptLOG = self.bot.get_channel(836005118679187497)
                    await message.remove_reaction("🔒", payload.member)

                    await rawExport(ch, TranscriptLOG)

                    await ch.delete()


                



            elif str(payload.emoji) == "⏳" and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "Community Service Hours", payload.member)

                
                await channel.send(query.CommunityService)
                
            elif str(payload.emoji) == "📝" and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "Request Letter of Recommendation", payload.member)
                await channel.send(query.Recommendation)
                
            elif str(payload.emoji) == "✍️" and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "Logging Academic Hours", payload.member)

                RN = discord.utils.get(guild.roles, id = 784128572335325194) 
                await channel.set_permissions(RN, send_messages = True, read_messages = True,reason="Ticket Perms (Manager)")


                await channel.send(query.AcademicHour)
                
            elif str(payload.emoji) == "🎨" and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "Design Commission", payload.member)

                RN = discord.utils.get(guild.roles, id = 838124415497535508) 
                await channel.set_permissions(RN, send_messages = True, read_messages = True,reason="Ticket Perms (Manager)")

                await channel.send(query.Design)
                
            elif str(payload.emoji) == "🤝" and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "PR Commission", payload.member)

                RN = discord.utils.get(guild.roles, id = 838124848663887902) 
                await channel.set_permissions(RN, send_messages = True, read_messages = True,reason="Ticket Perms (Manager)")

                
                await channel.send(query.PR)
                
            elif str(payload.emoji) == "💼" and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "Marketing Commission", payload.member)

                RN = discord.utils.get(guild.roles, id = 790009763500261396) 
                await channel.set_permissions(RN, send_messages = True, read_messages = True,reason="Ticket Perms (Manager)")

                await channel.send(query.Marketing)
                
            elif str(payload.emoji) == "📈" and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "Analytics Commission", payload.member)

                await channel.send(query.Analytics)
                
            elif str(payload.emoji) == "🧑‍💻" and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "Tech Commission", payload.member)

                RN = discord.utils.get(guild.roles, id = 793641881488588800) 
                await channel.set_permissions(RN, send_messages = True, read_messages = True,reason="Ticket Perms (Manager)")


                await channel.send(query.Tech)
                
            elif str(payload.emoji) == "👋" and ch.category_id == 835330150471434240:
                await message.remove_reaction(str(payload.emoji), payload.member)
                channel = await createChannel(self, payload, "Break Approval", payload.member)

                await channel.send(query.BreakApproval)
            database.db.close()

def setup(bot):
    bot.add_cog(SkeletonCMD(bot))



    