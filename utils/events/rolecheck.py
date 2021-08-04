import discord
from discord import embeds
from discord.ext import commands
import json
import datetime
from datetime import timedelta, datetime
from core.common import *

messageDict = {"Math": 866904767568543744, "Science": 866904901174427678, "English": 866905061182930944, "Language": 866905971519389787, "Art": 866906016602652743, "Social Studies": 866905205094481951, "Computer Science": 867550791635566623}

config, _ = load_config("equelRoles")

configA, _A = load_config("acadRoles")
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

def getAcadRole(query):
    print(query)
    if query not in configA:
        return None, None
    else:
        print(configA[query])

        value = messageDict[configA[query]]
        return value, configA[query]

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
        self.ValidRoles = ['Pre-Algebra Tutor','Algebra 1 Tutor','Geometry Tutor','Algebra 2/Trigonometry Tutor','Pre-Calculus Tutor','AP Calculus AB Tutor','AP Calculus BC Tutor','AP Statistics Tutor','Multi-variable Calculus Tutor',    'Biology Tutor','Chemistry Tutor','Physics Tutor','Earth Science Tutor','AP Biology Tutor','AP Chemistry Tutor','AP Physics 1 Tutor','AP Physics 2 Tutor','AP Physics C: Mechanics Tutor','AP Environmental Science Tutor',    'English Tutor','AP Literature Tutor','AP Language Tutor',    'AP Chinese Tutor','AP Spanish Tutor','AP French Tutor','AP German Tutor','AP Japanese Tutor','AP Latin Tutor','American Sign Language Tutor',    'AP 2D Art & Design Tutor','AP 3D Art & Design Tutor','AP Art History Tutor','AP Drawing Tutor','AP Capstone Tutor','AP Research Tutor','AP Seminar Tutor','World History Tutor','AP World History Tutor','US History Tutor','AP US History Tutor','AP European History Tutor','US Government Tutor']

        self.testRoles = ["Math", "Science", "Biology"]

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        '''
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
        '''
        pass




    @commands.Cog.listener('on_member_update')
    async def roleSyncAcad(self, before, after):
        if before.guild.id == 860897711334621194:
            channel = await self.bot.fetch_channel(865716647083507733)

            #New Role
            if len(before.roles) < len(after.roles):
                newRole = next(role for role in after.roles if role not in before.roles)
                if newRole.name in configA:
                    role = discord.utils.get(before.guild.roles, name=newRole.name)

                    if role is None:
                        raise BaseException(f"Invalid Data/Role {newRole.name}")

                    fieldValue = []
                    for member in before.guild.members:
                        if role in member.roles:
                            fieldValue.append(member.mention)

                    listOfMembers = ", ".join(fieldValue)

                    ID, subject = getAcadRole(newRole.name)
                    
                    msg = await channel.fetch_message(ID) 
                    embedORG : discord.Embed = msg.embeds[0]

                    embedNEW = discord.Embed(title = embedORG.title, description = "** **", color = 0x6c7dfe)
                    embedNEW.set_footer(text = "Any tutor that does not have AP in the title is a tutor for a normal College Prep/Honors class.")  
                    
                    
                    for field in embedORG.fields:
                        if field.name == newRole.name:
                            embedNEW.add_field(name = field.name, value = listOfMembers, inline = False)
                        else:
                            embedNEW.add_field(name = field.name, value = field.value, inline = False)

                    await msg.edit(embed = embedNEW)



            #Old Role
            elif len(before.roles) > len(after.roles):
                oldRole = (set(before.roles) - set(after.roles))

                for role in oldRole:
                    if role.name in configA:
                        #role = discord.utils.get(before.guild.roles, name=oldRole)
                        if role is None:
                            raise BaseException(f"Invalid Data/Role {oldRole.name}")

                        fieldValue = []
                        for member in before.guild.members:
                            if role in member.roles:
                                fieldValue.append(member.mention)

                        listOfMembers = ", ".join(fieldValue)
                        if listOfMembers == None or listOfMembers == "" or listOfMembers == " ":
                            listOfMembers = "** **"

                        ID, subject = getAcadRole(role.name)
                        print(ID, subject)
                        print(listOfMembers)
                        if ID == None:
                            return print(oldRole, role.name, role)


                        msg = await channel.fetch_message(ID) 

                        embedORG : discord.Embed = msg.embeds[0]

                        embedNEW = discord.Embed(title = embedORG.title, description = "** **", color = 0x6c7dfe)
                        embedNEW.set_footer(text = "Any tutor that does not have AP in the title is a tutor for a normal College Prep/Honors class.")  
                        
                        for field in embedORG.fields:
                            if field.name == role.name:
                                embedNEW.add_field(name = field.name, value = listOfMembers, inline = False)
                            else:
                                embedNEW.add_field(name = field.name, value = field.value, inline = False)
                                
                        await msg.edit(embed = embedNEW)




    @commands.Cog.listener('on_member_update')
    async def serverbooster(self, before, after):
        if before.guild.id == 763119924385939498:
            if len(before.roles) < len(after.roles):
                altServerBooster = discord.utils.get(before.guild.roles, name = "VIP")
                serverbooster = before.guild.premium_subscriber_role

                level35 = discord.utils.get(before.guild.roles, name = "〚Level 35〛Experienced")
                DJ = discord.utils.get(before.guild.roles,name ="DJ")

                newRole = next(role for role in after.roles if role not in before.roles)
                if newRole.id == serverbooster.id:
                    before.add_roles(altServerBooster)
                
                if newRole.id == level35.id:
                    before.add_roles(DJ)



            elif len(before.roles) > len(after.roles):
                altServerBooster = discord.utils.get(before.guild.roles, name = "VIP")
                serverbooster = before.guild.premium_subscriber_role

                level35 = discord.utils.get(before.guild.roles, name = "〚Level 35〛Experienced")
                DJ = discord.utils.get(before.guild.roles,name ="DJ")
                
                oldRole = (set(before.roles) - set(after.roles))
                for role in oldRole:
                    if role.id == serverbooster.id:
                        before.remove_roles(altServerBooster)


        

def setup(bot):
    bot.add_cog(SkeletonCMD(bot))