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
 

def setup(bot):
    bot.add_cog(SkeletonCMD(bot))