import inspect
import io
import logging
import os
import textwrap
import traceback
from contextlib import redirect_stdout

import aiohttp
import discord
from core import database
from core.checks import is_botAdmin, is_botAdmin3, is_botAdmin4
from core.common import Emoji
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class CoreBotConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group(aliases=['w'])
    @is_botAdmin
    async def whitelist(self, ctx):
        pass


    @whitelist.command()
    @is_botAdmin
    async def list(self, ctx):
        adminList = []

        query1 = database.Administrators.select().where(database.Administrators.TierLevel == 1)
        for admin in query1:
            user = await self.bot.fetch_user(admin.discordID)
            adminList.append(f"`{user.name}` -> `{user.id}`")

        adminLEVEL1 = "\n".join(adminList)

        adminList = []
        query2 = database.Administrators.select().where(database.Administrators.TierLevel == 2)
        for admin in query2:
            user = await self.bot.fetch_user(admin.discordID)
            adminList.append(f"`{user.name}` -> `{user.id}`")

        adminLEVEL2 = "\n".join(adminList)

        adminList = []
        query3 = database.Administrators.select().where(database.Administrators.TierLevel == 3)
        for admin in query3:
            user = await self.bot.fetch_user(admin.discordID)
            adminList.append(f"`{user.name}` -> `{user.id}`")

        adminLEVEL3 = "\n".join(adminList)

        adminList = []
        query4 = database.Administrators.select().where(database.Administrators.TierLevel == 4)
        for admin in query4:
            user = await self.bot.fetch_user(admin.discordID)
            adminList.append(f"`{user.name}` -> `{user.id}`")

        adminLEVEL4 = "\n".join(adminList)

        embed = discord.Embed(title="Bot Administrators", description="Whitelisted Users that have Increased Authorization",
                            color=discord.Color.green())
        embed.add_field(name="Whitelisted Users",
                        value=f"Format:\n**Username** -> **ID**\n\n**Permit 4:** *Owners*\n{adminLEVEL4}\n\n**Permit 3:** *Sudo Administrators*\n{adminLEVEL3}\n\n**Permit 2:** *Administrators*\n{adminLEVEL2}\n\n**Permit 1:** *Bot Managers*\n{adminLEVEL1}")
        embed.set_footer(text="Only Owners/Permit 4's can modify Bot Administrators. | Permit 4 is the HIGHEST Authorization Level")

        await ctx.send(embed=embed)


    @whitelist.command()
    @is_botAdmin4
    async def remove(self, ctx, ID: discord.User):
        database.db.connect(reuse_if_open=True)

        query = database.Administrators.select().where(database.Administrators.discordID == ID.id)
        if query.exists():
            query = query.get()

            query.delete_instance()

            embed = discord.Embed(title="Successfully Removed User!",
                                description=f"{ID.name} has been removed from the database!", color=discord.Color.green())
            await ctx.send(embed=embed)


        else:
            embed = discord.Embed(title="Invalid User!", description="Invalid Provided: (No Record Found)",
                                color=discord.Color.red())
            await ctx.send(embed=embed)

        database.db.close()


    @whitelist.command()
    @is_botAdmin4
    async def add(self, ctx, ID: discord.User, level: int):
        database.db.connect(reuse_if_open=True)

        q: database.Administrators = database.Administrators.create(discordID=ID.id, TierLevel=level)
        q.save()

        embed = discord.Embed(title="Successfully Added User!",
                            description=f"{ID.name} has been added successfully with permit level `{str(level)}`.",
                            color=discord.Color.gold())
        await ctx.send(embed=embed)

        database.db.close()


        


    @commands.group(aliases=['bl'])
    async def blacklist(self, ctx):
        pass


    @blacklist.command()
    @is_botAdmin4
    async def add(self, ctx, user: discord.User):
        database.db.connect(reuse_if_open=True)

        q: database.Blacklist = database.Blacklist.create(discordID=user.id)
        q.save()

        embed = discord.Embed(title="Successfully Blacklisted User!",
            description=f"{user.mention} has been added to the blacklist.",color=discord.Color.gold())
        await ctx.send(embed=embed)

    database.db.close()


    @blacklist.command()
    @is_botAdmin4
    async def remove(self, ctx, user: discord.User):
        database.db.connect(reuse_if_open=True)

        query = database.Blacklist.select().where(database.Blacklist.discordID == user.id)
        if query.exists():
            query = query.get()

            query.delete_instance()

            embed = discord.Embed(title="Successfully Removed User!",
                                description=f"{user.mention} has been removed from the blacklist!", color=discord.Color.green())
            await ctx.send(embed=embed)


        else:
            embed = discord.Embed(title="Invalid User!", description="Invalid Provided: (No Record Found)",
                                color=discord.Color.red())
            await ctx.send(embed=embed)

        database.db.close()


    @blacklist.command()
    @is_botAdmin3
    async def list(self, ctx):
        emptylist = []

        for p in database.Blacklist:
            user = await self.bot.fetch_user(p.id)
            emptylist.append(f"`{user.name}` -> `{user.id}`")

        blacklistList = "\n".join(emptylist)

        embed = discord.Embed(title="Current Blacklist", description = blacklistList, color = discord.Color.red())
        await ctx.send(embed = embed)







    @commands.group(aliases=['f'])
    async def filter(self, ctx):
        pass

    @filter.command()
    @is_botAdmin4
    async def modify(self, ctx, num: int, val: bool):
        CheckDB : database.CheckInformation =  database.CheckInformation.select().where(database.CheckInformation.id == 1).get()
        
        databaseValues = {
            1: "CheckDB.MasterMaintenance",
            2: "CheckDB.guildNone",
            3: "CheckDB.externalGuild",
            4: "CheckDB.ModRoleBypass",
            5: "CheckDB.ruleBypass",
            6: "CheckDB.publicCategories",
            7: "CheckDB.elseSituation"
        }


        if num == 1:
            CheckDB.MasterMaintenance = val
            CheckDB.save()
        elif num == 2:
            CheckDB.guildNone = val
            CheckDB.save()
        elif num == 3:
            CheckDB.externalGuild = val
            CheckDB.save()
        elif num == 4:
            CheckDB.ModRoleBypass = val
            CheckDB.save()
        elif num == 5:
            CheckDB.ruleBypass = val
            CheckDB.save()
        elif num == 6:
            CheckDB.publicCategories = val
            CheckDB.save()
        elif num == 7:
            CheckDB.elseSituation = val
            CheckDB.save()
        else:
            return await ctx.send(f"Not a valid option\n```py\n{databaseValues}\n```")

            
        await ctx.send(f"Field: {databaseValues[num]} has been set to {str(val)}")



    @filter.command()
    async def list(self, ctx):
        CheckDB : database.CheckInformation =  database.CheckInformation.select().where(database.CheckInformation.id == 1).get()

        embed = discord.Embed(title = "Command Filters", description = "Bot Filters that the bot is subjected towards.", color = discord.Colour.gold())
        embed.add_field(name = "Checks", value = f"1) `Maintenance Mode`\n{Emoji.barrow} {CheckDB.MasterMaintenance}\n\n2) `NoGuild`\n{Emoji.barrow} {CheckDB.guildNone}\n\n3) `External Guilds`\n{Emoji.barrow} {CheckDB.externalGuild}\n\n4) `ModBypass`\n{Emoji.barrow} {CheckDB.ModRoleBypass}\n\n5) `Rule Command Bypass`\n{Emoji.barrow} {CheckDB.ruleBypass}\n\n6) `Public Category Lock`\n{Emoji.barrow} {CheckDB.publicCategories}\n\n7) `Else Conditions`\n{Emoji.barrow} {CheckDB.elseSituation}")
        await ctx.send(embed = embed)



def setup(bot):
    bot.add_cog(CoreBotConfig(bot))
