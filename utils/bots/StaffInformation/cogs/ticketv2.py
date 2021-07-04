import datetime
import io
import json
from datetime import datetime, timedelta
from re import A

import chat_exporter
import discord
from chat_exporter.chat_exporter import Transcript
from core import database
from discord.channel import TextChannel
from discord.errors import InvalidArgument
from discord.ext import commands

authCategories = [836005981497327616, 836006081159102474, 836006123952930847, 836006174431379476, 836006227410419742, 836006262440460369, 836006311417348128, 836006373984436255 , 836006426497384449]



async def rawExport(channel, response):
    transcript = await chat_exporter.export(channel)

    if transcript is None:
        return

    embed = discord.Embed(title = "Channel Transcript", description = f"**Channel:** {channel.name}\n*Transcript Attached Below*", color = discord.Colour.green())
    transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{channel.name}.html")

    await response.send(embed = embed)
    await response.send(file=transcript_file)

async def createChannel(self, payload, topic, member):

    guild = self.bot.get_guild(payload.guild_id)
    VP = discord.utils.get(guild.roles, name='Executive (VP)')
    CO = discord.utils.get(guild.roles, name='Senior Executive (CO)') 
    IO = discord.utils.get(guild.roles, name='Information Bot') 
    BOT = discord.utils.get(guild.roles, name='Bots') 
    CSD = await self.bot.fetch_user(827317640196128799)

    roleName = None

    if topic == "Community Service Hours":
        st = "csh"
        category = discord.utils.get(guild.categories, name="Community Service Tickets")

    elif topic == "Request Letter of Recommendation":
        st = "rlr"
        category = discord.utils.get(guild.categories, name="Request Letter of Recommendation")

    elif topic == "Logging Academic Hours":
        st = "lah"
        category = discord.utils.get(guild.categories, name="Academic Tickets")
        roleName = "Academics Manager"

    elif topic == "Design Commission":
        st = "dc"
        category = discord.utils.get(guild.categories, name="Design Commission Tickets")
        roleName = "Design Team"

    elif topic == "PR Commission":
        st = "pr"
        category = discord.utils.get(guild.categories, name="PR Commission Tickets")
        roleName = "PR Team"

    elif topic == "Marketing Commission":
        st = "mc"
        category = discord.utils.get(guild.categories, name="Marketing Commission Tickets")
        roleName = "Marketing Team"

    elif topic == "Analytics Commission":
        st = "ac"
        category = discord.utils.get(guild.categories, name="Analytics Commission Tickets")

    elif topic == "Tech Commission":
        st = "tc"
        category = discord.utils.get(guild.categories, name="Tech Commission Tickets")
        roleName = "Tech Team"

    elif topic == "Break Approval":
        st = "ba"
        category = discord.utils.get(guild.categories, name="Break Approval Tickets")

    else:
        raise BaseException("Invalid Data")

    num = len(category.channels)

    channel = await guild.create_text_channel(f'open-{st}-{num}', category = category)

    



    controlTicket = discord.Embed(title = "Control Panel", description = "To end this ticket, react to the lock emoji!", color = discord.Colour.green())
    await channel.send(member.mention)
    msg = await channel.send(embed = controlTicket)
    await msg.add_reaction("🔒")

    await channel.set_permissions(VP, send_messages = True, read_messages = True,reason="Ticket Perms (VP)")

    await channel.set_permissions(CO, send_messages = True, read_messages = True, reason="Ticket Perms (CO)")

    await channel.set_permissions(guild.default_role, send_messages = False, read_messages = False, reason="Ticket Perms (CO)")

    await channel.set_permissions(IO, send_messages = True, read_messages = True, reason="Ticket Perms (CO)")

    await channel.set_permissions(BOT, send_messages = False, read_messages = False, reason="Ticket Perms (CO)")

    await channel.set_permissions(CSD, send_messages = True, read_messages = True,reason="Ticket Perms (VP)")

    await channel.set_permissions(member, send_messages = True, read_messages = True,reason="Ticket Perms (VP)")

    
    database.db.connect(reuse_if_open=True)

    q: database.ChannelInfo = database.ChannelInfo.create(channelID = channel.id, topic = st, authorID = payload.user_id, status = "OPEN")
    q.save()

    print(f"{q.authorID} has been added successfully.")
    database.db.close()

    return channel

class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def OfficialForm(self, ctx):
        database.db.connect(reuse_if_open=True)
        query = database.ExtraResponse.select().where(database.ExtraResponse.topic == 'cs').get()
        await ctx.send(query.field1)
        database.db.close()

    @commands.command()
    async def returns(self, ctx):
        database.db.connect(reuse_if_open=True)
        query = database.ExtraResponse.select().where(database.ExtraResponse.topic == 'cs').get()
        await ctx.send(query.field2)
        database.db.close()

    @commands.command()
    async def useofficalform(self, ctx):
        database.db.connect(reuse_if_open=True)
        query = database.ExtraResponse.select().where(database.ExtraResponse.topic == 'cs').get()
        await ctx.send(query.field3)
        database.db.close()

    @commands.command()
    async def responseTime(self, ctx):
        database.db.connect(reuse_if_open=True)
        query = database.ExtraResponse.select().where(database.ExtraResponse.topic == 'cs').get()
        await ctx.send(query.field4)
        database.db.close()



    @commands.command()
    async def setupEmbed(self, ctx, en = "no"):
        embed = discord.Embed(title = "Ticket Topics", description = "React with the appropriate emoji to open up a ticket!", color = discord.Colour.blue())
        embed.add_field(name = "Community Service", value = "⏳")

        embed.add_field(name = "Request Letter of Recommendation", value = "📝", inline = True)

        embed.add_field(name = "Academic Commissions", value = "✍️", inline = True)

        embed.add_field(name = "Design Commission", value = "🎨")

        embed.add_field(name = "PR Commission", value = "🤝", inline = True)

        embed.add_field(name = "Marketing Commission", value = "💼", inline = True)

        #embed.add_field(name = "Analytics Commission", value = "📈")

        embed.add_field(name = "Tech Commission", value = "🧑‍💻", inline = True)

        embed.add_field(name = "Breaks", value = "👋", inline = True)
        embed.set_footer(text = "Reach with the emoji below your desired topic!")
        msg = await ctx.send(embed = embed)
        if en == "no":
            listofStuff = ['⏳','✍️','🎨','🤝','💼','🧑‍💻','👋', '📝']
            for emoji in listofStuff:
                await msg.add_reaction(emoji)

    @commands.command()
    async def getEmail(self, ctx, target: discord.User):
        database.db.connect(reuse_if_open=True)
        try:
            query = database.EmailsVersion2.select().where(database.EmailsVersion2.supervisorID.contains(str(target.id))).get()
            embed = discord.Embed(title = "Supervisor Information", description = f"**Username:** {target.display_name}#{target.discriminator}\n**ID:** {target.id}\n**Email:** {query.supervisorEmail}", color = discord.Colour.green())
            await ctx.send(embed = embed)
            
        except Exception as e:
            print(e)
            embed = discord.Embed(title = "Supervisor Information", description = f"**No Results Found**\nPlease make sure you have provided a valid supervisor!\n\n*Failed Query:* {target.id}", color = discord.Colour.red())
            await ctx.send(embed = embed)

        finally:
            database.db.close()






def setup(bot):
    bot.add_cog(SkeletonCMD(bot))
