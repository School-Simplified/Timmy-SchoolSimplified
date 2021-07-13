import discord
from discord import embeds
from discord.ext import commands
import json
import datetime
from datetime import timedelta, datetime
from core.common import *
config, _ = load_config()

'''
Used by RoleSync
'''

def getEquelRank(query):
    print(query)
    if query not in config:
        return None
    else:
        print(config[query])
        return config[query]



async def roleNameCheck(name, before, after, guild, user ,type):
    check = getEquelRank(name)
    if check != None:
        if name in [role.name for role in before.roles] or name in [role.name for role in after.roles]:
            helper = discord.utils.get(guild.roles, name=check)

            if type == "+":
                await user.add_roles(helper)
            elif type == "-":
                await user.remove_roles(helper)
            else:
                raise BaseException("Invalid Type Syntax: roleNameCheck (type) only supports + or -.")
        else:
            print("Not found. (Error 2)")

    else:
        print("Not in JSON")







class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staffServer = 778406166735880202
        self.mainServer = 763119924385939498
        self.ValidRoles = ['Pre-Algebra','Algebra 1','Geometry','Algebra 2/Trigonometry','Pre-Calculus','AP Calculus AB','AP Calculus BC','AP Statistics','Multi-variable Calculus',    'Biology','Chemistry','Physics','Earth Science','AP Biology','AP Chemistry','AP Physics 1','AP Physics 2','AP Physics C: Mechanics','AP Environmental Science',    'English','AP Literature','AP Language',    'AP Chinese','AP Spanish','AP French','AP German','AP Japanese','AP Latin','American Sign Language',    'AP 2D Art & Design','AP 3D Art & Design','AP Art History','AP Drawing','AP Capstone','AP Research','AP Seminar','World History','AP World History','US History','AP US History','AP European History','US Government']

        self.MathRoles = ['Pre-Algebra','Algebra 1','Geometry','Algebra 2/Trigonometry','Pre-Calculus','AP Calculus AB','AP Calculus BC','AP Statistics','Multi-variable Calculus']
        self.ScienceRoles = ['Biology','Chemistry','Physics','Earth Science','AP Biology','AP Chemistry','AP Physics 1','AP Physics 2','AP Physics C: Mechanics','AP Environmental Science']
        self.LARoles = ['English','AP Literature','AP Language']
        self.LanguageRoles = ['AP Chinese','AP Spanish','AP French','AP German','AP Japanese','AP Latin','American Sign Language']
        self.ArtRoles = ['AP 2D Art & Design','AP 3D Art & Design','AP Art History','AP Drawing','AP Capstone','AP Research','AP Seminar']
        self.SSRoles = ['World History','AP World History','US History','AP US History','AP European History','US Government']

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        #sub server id: 827568748163760139
        mainServer = self.bot.get_guild(self.staffServer)
        user = mainServer.get_member(before.id)

        if mainServer == None:
            return

        if before.guild.id != self.staffServer:
            return
            
        if len(before.roles) < len(after.roles):
            #New Role
            if before.guild.id == 778406166735880202:
                return

            list_difference = []
            for item in after.roles:
                if item not in before.roles:
                    list_difference.append(item)

            item = list_difference[0]


            await roleNameCheck(item.name, before, after, mainServer, user, "+")

            
        elif len(before.roles) > len(after.roles):
            if before.guild.id == 778406166735880202:
                return

            list_difference = []
            for item in before.roles:
                if item not in after.roles:
                    list_difference.append(item)

            item = list_difference[0]

            await roleNameCheck(item.name, before, after, mainServer, user, "-")

    @commands.Cog.listener('on_member_update')
    async def roleSyncAcad(self, before, after):
        if before.guild.id == self.mainServer:
            channel = await self.bot.fetch_channel(786057630383865858)

            if len(before.roles) < len(after.roles):
                newRole = next(role for role in after.roles if role not in before.roles)
                if newRole.name in self.ValidRoles:

                    role = discord.utils.get(before.guild.roles, name=newRole.name)
                    if role is None:
                        raise BaseException(f"Invalid Data/Role {newRole.name}")

                    fieldValue = []
                    for member in before.guild.members:
                        if role in member.roles:
                            await fieldValue.append(member.mention)

                    listOfMembers = ", ".join(fieldValue)

                    if newRole.name in self.MathRoles:
                        topic = "MATH"
                        ID = 123
                    elif newRole.name in self.ScienceRoles:
                        topic = "SCIENCE"
                        ID = 123
                    elif newRole.name in self.LARoles:
                        topic = "LA"
                        ID = 123
                    elif newRole.name in self.LanguageRoles:
                        topic = "LANGUAGE"
                        ID = 123
                    elif newRole.name in self.ArtRoles:
                        topic = "ART"
                        ID = 123
                    elif newRole.name in self.SSRoles:
                        topic = "SS"
                        ID = 123
                    else:
                        return print(newRole.name)
                    
                    msg = await channel.fetch_message(ID) 

                    
                    embed = discord.Embed(title = "Test Embed", description = "Test")
                    embed.add_field(name = "Value", value = listOfMembers)
                    await msg.edit(embed = embed)

            elif len(before.roles) > len(after.roles):
                oldRole = str(set(before.roles) - set(after.roles))
                if oldRole.name in self.ValidRoles:
                    role = discord.utils.get(before.guild.roles, name="VP")
                    if role is None:
                        raise BaseException(f"Invalid Data/Role {oldRole.name}")

                    fieldValue = []
                    for member in before.guild.members:
                        if role in member.roles:
                            await fieldValue.append(member.mention)

                    listOfMembers = ", ".join(fieldValue)

                    if oldRole.name in self.MathRoles:
                        topic = "MATH"
                        ID = 123
                    elif oldRole.name in self.ScienceRoles:
                        topic = "SCIENCE"
                        ID = 123
                    elif oldRole.name in self.LARoles:
                        topic = "LA"
                        ID = 123
                    elif oldRole.name in self.LanguageRoles:
                        topic = "LANGUAGE"
                        ID = 123
                    elif oldRole.name in self.ArtRoles:
                        topic = "ART"
                        ID = 123
                    elif oldRole.name in self.SSRoles:
                        topic = "SS"
                        ID = 123
                    else:
                        return print(oldRole.name)


                    msg = await channel.fetch_message(ID) 

                    embed = discord.Embed(title = "Test Embed", description = "Test")
                    embed.add_field(name = "Value", value = listOfMembers)
                    await msg.edit(embed = embed)


            
        

def setup(bot):
    bot.add_cog(SkeletonCMD(bot))