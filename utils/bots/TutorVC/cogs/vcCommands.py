import asyncio
import datetime
import json
from datetime import datetime, timedelta

import discord
from core import database
from discord.ext import commands, tasks
from peewee import _truncate_constraint_name

#from main import vc

#Variables
'''
channel_id = 843637802293788692
categoryID = 776988961087422515

staticChannels = [784556875487248394, 784556893799448626]
presetChannels = [843637802293788692, 784556875487248394, 784556893799448626]
'''
time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}

def convert_time_to_seconds(time):
    try:
        value = int(time[:-1]) * time_convert[time[-1]]
    except:
        value = time
    finally:
        if value < 60:
            return None
        else:
            return value
    

def showFutureTime(time):
    now = datetime.now()
    output = convert_time_to_seconds(time)
    if output == None:
        return None

    add = timedelta(seconds = int(output))
    now_plus_10 = now + add
    print(now_plus_10)

    return now_plus_10.strftime(r"%I:%M %p")

def showTotalMinutes(dateObj: datetime):
    now = datetime.now()

    deltaTime = now - dateObj

    seconds = deltaTime.seconds
    minutes = (seconds % 3600) // 60
    return minutes
    

class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 843637802293788692
        self.categoryID = 776988961087422515
        self.staticChannels = [784556875487248394, 784556893799448626]
        self.presetChannels = [843637802293788692, 784556875487248394, 784556893799448626]
        
    @commands.command()
    async def rename(self, ctx, *, name = None):
        database.db.connect(reuse_if_open=True)
        team = discord.utils.get(ctx.guild.roles, name='Academics Team')
        SB = discord.utils.get(ctx.guild.roles, name='Server Booster')
        legend = discord.utils.get(ctx.guild.roles, name='Legend')

        member = ctx.guild.get_member(ctx.author.id)
            
        if ctx.author.id != 415629932798935040:
            if SB not in ctx.author.roles and team not in ctx.author.roles and legend not in ctx.author.roles:
                return await ctx.send("Sorry! Only Server Boosters/Academic Members/Legends may change their channels names!")

        voice_state = member.voice

        if voice_state == None:
            await ctx.send("You need to be in a voice channel you own to use this!")

        else:
            if member.voice.channel.category_id == self.categoryID:
                query = database.VCChannelInfo.select().where(database.VCChannelInfo.authorID == ctx.author.id)

                if query.exists():
                    q: database.VCChannelInfo = database.VCChannelInfo.select().where(database.VCChannelInfo.authorID == ctx.author.id).get()
                    
                    print(member.voice.channel.id)
                    print(q.ChannelID)
                    if member.voice.channel.id == int(q.ChannelID):
                        if name != None:
                            embed = discord.Embed(title = "ReNamed Channel", description = f"I have changed the channel's name to:\n**{name}**", color = discord.Colour.green())
                            
                            print(name)
                            await member.voice.channel.edit(name = name)
                            await ctx.send(embed = embed)

                            q.name = name
                            q.save()
                        else:
                            embed = discord.Embed(title = "ReNamed Channel", description = f"I have changed the channel's name to:\n**{name}**", color = discord.Colour.green())
                            
                            await member.voice.channel.edit(name = f"{member.display_name}'s Tutoring Channel")
                            await ctx.send(embed = embed)
                            q.name = f"{member.display_name}'s Tutoring Channel"
                            q.save()

                    else:
                        embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to rename it!", color = discord.Colour.red())
                        
                        await ctx.send(embed = embed)

                else:
                    q = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == member.voice.channel.id)
                    embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to rename it!", color = discord.Colour.dark_red())
                        
                    await ctx.send(embed = embed)
            else:
                embed = discord.Embed(title = "Unknown Channel", description = "You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a channel you own!", color = discord.Colour.red())
                        
                await ctx.send(embed = embed)
        database.db.close()

    @commands.command()
    async def end(self, ctx):
        database.db.connect(reuse_if_open=True)
        team = discord.utils.get(ctx.guild.roles, name='Academics Team')
        member = ctx.guild.get_member(ctx.author.id)
        timestamp2 = datetime.now()

        voice_state = member.voice
        if voice_state == None:

            query = database.VCChannelInfo.select().where(database.VCChannelInfo.authorID == ctx.author.id)
            if query.exists():
                query = database.VCChannelInfo.select().where(database.VCChannelInfo.authorID == ctx.author.id).get()

                day = showTotalMinutes(query.datetimeObj)
                print(query.ChannelID)

                channel = await self.bot.fetch_channel(int(query.ChannelID))

                await channel.delete()
                embed = discord.Embed(title = "Ended Session", description = "I have successfully ended the session!", color = discord.Colour.blue())
                embed.add_field(name = "Time Spent", value = f"{member.mention} you have spent a total of `{day} minutes` in voice channel, **{query.name}**.")
                await ctx.send(embed = embed)

                query.delete_instance()
                return

            else:
                print("Ignore VC Leave")


        if voice_state.channel.id in self.presetChannels:
            embed = discord.Embed(title = "UnAuthorized Channel Deletion", description = "You are not allowed to delete these channels!\n\n**Error Detection:**\n**1)** Detected Static Channels", color = discord.Colour.dark_red())
            return await ctx.send(embed = embed)

        if member.voice.channel.category_id == self.categoryID:
            query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id))

            if query.exists():
                q: database.VCChannelInfo = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id)).get()
                
                tag: database.IgnoreThis = database.IgnoreThis.create(channelID = voice_state.channel.id, authorID = member.id)
                tag.save()

                day = showTotalMinutes(q.datetimeObj)

                print("In VC")   
                await voice_state.channel.delete()

                embed = discord.Embed(title = "Ended Session", description = "I have successfully ended the session!", color = discord.Colour.blue())
                embed.add_field(name = "Time Spent", value = f"{member.mention} you have spent a total of `{day} minutes` in voice channel, **{q.name}**.")
                await ctx.send(embed = embed)

                q.delete_instance()


            else:
                try:
                    q = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == voice_state.channel.id).get()
                except:
                    embed = discord.Embed(title = "Ownership Check Failed", description = "This isn't a tutoring channel! Please use the command on an actual tutoring channel!", color = discord.Colour.red())
                else:
                    embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to end it!", color = discord.Colour.red())
                finally:
                    await ctx.send(embed = embed)
        else:
            embed = discord.Embed(title = "Unknown Channel", description = "You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a channel you own!", color = discord.Colour.red())
                    
            await ctx.send(embed = embed)
        database.db.close()

    @commands.command()
    @commands.has_any_role(784202171825913856, 786610369988263976, 763420686890565641, 767580143010840616, 784202204323905546) #Acad Manager
    async def forceend(self, ctx, channel: discord.VoiceChannel):
        database.db.connect(reuse_if_open=True)
        team = discord.utils.get(ctx.guild.roles, name='Academics Team')
        member = ctx.guild.get_member(ctx.author.id)

        if channel.id in self.presetChannels:
            embed = discord.Embed(title = "UnAuthorized Channel Deletion", description = "You are not allowed to delete these channels!\n\n**Error Detection:**\n**1)** Detected Static Channels", color = discord.Colour.dark_red())
            return await ctx.send(embed = embed)

        if channel.category_id == self.categoryID:
            query = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == channel.id)
            print(query)

            if query.exists():
                q: database.VCChannelInfo = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == channel.id).get()

                day = showTotalMinutes(q.datetimeObj)


                for VCMember in channel.members:
                    if VCMember.id == q.authorID:
                        tag: database.IgnoreThis = database.IgnoreThis.create(channelID = channel.id, authorID = VCMember.id)
                        tag.save()
                        print(f"Added: {VCMember.id}")
                    
                
                await channel.delete()
                q.delete_instance()
                embed = discord.Embed(title = "Ended Session", description = "I have successfully ended the session!", color = discord.Colour.blue())
                embed.add_field(name = "Time Spent", value = f"<@{q.authorID}> you have spent a total of `{day} minutes` in voice channel, **{q.name}**.")
                await ctx.send(embed = embed)

                

            else:
                await channel.delete()
                embed = discord.Embed(title = "Partial Completion", description = "The database indicates there is no owner or data related to this voice channel but I have still deleted the channel!", color = discord.Colour.gold())
                    
                await ctx.send(embed = embed)
                print(query.authorID)
                
        else:
            embed = discord.Embed(title = "Unknown Channel", description = "You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a tutoring channel!", color = discord.Colour.red())
                    
            await ctx.send(embed = embed)

        database.db.close()


    @commands.command()
    async def lock(self, ctx):
        database.db.connect(reuse_if_open=True)
        member = ctx.guild.get_member(ctx.author.id)

        BOT = ctx.guild.get_member(842468709406081034)
        OWNER = ctx.guild.get_member(409152798609899530)
        TMOD = discord.utils.get(ctx.guild.roles, name='Mod Trainee')
        MOD = discord.utils.get(ctx.guild.roles, name='Moderator')
        SMOD = discord.utils.get(ctx.guild.roles, name='Senior Moderator')
        CO = discord.utils.get(ctx.guild.roles, name='CO')
        VP = discord.utils.get(ctx.guild.roles, name='VP')

        voice_state = member.voice

        if voice_state == None:
            embed = discord.Embed(title = "Unknown Voice Channel", description = "You have to be in a voice channel you own in order to use this!", color = discord.Colour.dark_red())
            return await ctx.send(embed = embed)
        
        else:
            if voice_state.channel.id in self.presetChannels:
                embed = discord.Embed(title = "UnAuthorized Channel Modification", description = "You are not allowed to modify these channels!\n\n**Error Detection:**\n**1)** Detected Static Channels", color = discord.Colour.dark_red())
                return await ctx.send(embed = embed)

            if member.voice.channel.category_id == self.categoryID:
                query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id))

                if query.exists():
                    LOCK : database.VCChannelInfo = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id)).get()
                    LOCK.lockStatus = "1"
                    LOCK.save()

                    await member.voice.channel.set_permissions(BOT, connect = True, manage_channels = True, manage_permissions = True)
                    await member.voice.channel.set_permissions(OWNER, connect = True, manage_channels = True, manage_permissions = True)
                    await member.voice.channel.set_permissions(member, connect = True)

                    await member.voice.channel.set_permissions(ctx.guild.default_role, connect = False)
                    await member.voice.channel.set_permissions(TMOD, connect = True)
                    await member.voice.channel.set_permissions(MOD, connect = True)
                    await member.voice.channel.set_permissions(SMOD, connect = True)
                    await member.voice.channel.set_permissions(VP, connect = True, manage_channels = True, manage_permissions = True)
                    

                    embed = discord.Embed(title = "Locked Voice Channel", description = "Your voice channel has been locked and now only authorized users can join it!\n\n**NOTE:** Moderators and other Administrators will always be allowed into your voice channels!", color = discord.Colour.green())
                    await ctx.send(embed = embed)

                else:
                    try:
                        q = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == voice_state.channel.id).get()
                    except:
                        embed = discord.Embed(title = "Ownership Check Failed", description = "This isn't a tutoring channel! Please use the command on an actual tutoring channel!", color = discord.Colour.red())
                    else:
                        embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to end it!", color = discord.Colour.red())
                    finally:
                        await ctx.send(embed = embed)
            else:
                embed = discord.Embed(title = "Unknown Channel", description = "You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a channel you own!", color = discord.Colour.red())
                        
                await ctx.send(embed = embed)
        
        database.db.close()

                    




    @commands.command()
    async def unlock(self, ctx):
        database.db.connect(reuse_if_open=True)
        member = ctx.guild.get_member(ctx.author.id)
        timestamp2 = datetime.now()

        voice_state = member.voice

        if voice_state == None:
            embed = discord.Embed(title = "Unknown Voice Channel", description = "You have to be in a voice channel you own in order to use this!", color = discord.Colour.dark_red())
            return await ctx.send(embed = embed)

        else:
            if voice_state.channel.id in self.presetChannels:
                embed = discord.Embed(title = "UnAuthorized Channel Modification", description = "You are not allowed to modify these channels!\n\n**Error Detection:**\n**1)** Detected Static Channels", color = discord.Colour.dark_red())
                return await ctx.send(embed = embed)

            if member.voice.channel.category_id == self.categoryID:
                query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id))

                if query.exists():
                    LOCK : database.VCChannelInfo = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id)).get()
                    LOCK.lockStatus = "0"
                    LOCK.save()

                    query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id)).get()
                    print(query.lockStatus)

                    await member.voice.channel.edit(sync_permissions=True)

                    embed = discord.Embed(title = "Unlocked Voice Channel", description = "Your voice channel has been unlocked and now anyone can join it!", color = discord.Colour.green())
                    await ctx.send(embed = embed)

                else:
                    try:
                        q = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == voice_state.channel.id).get()
                    except:
                        embed = discord.Embed(title = "Ownership Check Failed", description = "This isn't a tutoring channel! Please use the command on an actual tutoring channel!", color = discord.Colour.red())
                    else:
                        embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to end it!", color = discord.Colour.red())
                    finally:
                        await ctx.send(embed = embed)

            else:
                embed = discord.Embed(title = "Unknown Channel", description = "You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a channel you own!", color = discord.Colour.red())
                        
                await ctx.send(embed = embed)

        database.db.close()



    @commands.command()
    async def permit(self, ctx, typeAction, user: discord.Member = None):
        database.db.connect(reuse_if_open=True)
        member = ctx.guild.get_member(ctx.author.id)
        timestamp2 = datetime.now()

        voice_state = member.voice

        if voice_state == None:
            embed = discord.Embed(title = "Unknown Voice Channel", description = "You have to be in a voice channel you own in order to use this!", color = discord.Colour.dark_red())
            return await ctx.send(embed = embed)

        else:
            if voice_state.channel.id in self.presetChannels:
                embed = discord.Embed(title = "UnAuthorized Channel Modification", description = "You are not allowed to modify these channels!\n\n**Error Detection:**\n**1)** Detected Static Channels", color = discord.Colour.dark_red())
                return await ctx.send(embed = embed)

            if member.voice.channel.category_id == self.categoryID:
                query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id))

                if query.exists():
                    query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id)).get()
                    print(query.lockStatus)

                    if query.lockStatus == "0":
                        embed = discord.Embed(title = "Invalid Setup", description = "Hey there! This voice channel is already open to the public, if you want to limit its access to certain people. Then consider using `+lock` and then come back this command!", color = discord.Colour.blurple())
                        return await ctx.send(embed = embed)

                    else:
                        if typeAction == "+" or typeAction.lower() == "add":
                            if user == None:
                                return await ctx.send("Invalid User Provided...")
                            await member.voice.channel.set_permissions(user, connect = True)
                            embed = discord.Embed(title = "Permit Setup", description = f"{user.mention} now has access to this channel!", color = discord.Colour.blurple())
                            return await ctx.send(embed = embed)
                            
                        elif typeAction == "-" or typeAction.lower() == "remove":
                            if user == None:
                                return await ctx.send("Invalid User Provided...")

                            if user.id == int(query.authorID):
                                return await ctx.send("You can't modify your own access!")

                            await member.voice.channel.set_permissions(user, overwrite=None)
                            embed = discord.Embed(title = "Permit Setup", description = f"{user.mention}'s access has been removed from this channel!", color = discord.Colour.blurple())
                            return await ctx.send(embed = embed)

                        elif typeAction == "=" or typeAction.lower() == "list":
                            ch = member.voice.channel
                            randomlist = []
                            for x in ch.overwrites:
                                if isinstance(x, discord.Member):
                                    randomlist.append(x.display_name)

                            formatVer = "\n".join(randomlist)
                            
                            embed = discord.Embed(title = "Permit List", description = f"**Users Authorized:**\n\n{formatVer}", color = discord.Color.gold())
                            await ctx.send(embed = embed)
                        
                        else:
                            return await ctx.send("Invalid Operation Type")

                else:
                    try:
                        q = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == voice_state.channel.id).get()
                    except:
                        embed = discord.Embed(title = "Ownership Check Failed", description = "This isn't a tutoring channel! Please use the command on an actual tutoring channel!", color = discord.Colour.red())
                    else:
                        embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to end it!", color = discord.Colour.red())
                    finally:
                        await ctx.send(embed = embed)
            else:
                embed = discord.Embed(title = "Unknown Channel", description = "You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a channel you own!", color = discord.Colour.red())
                        
                await ctx.send(embed = embed)




    @commands.command()
    async def voicelimit(self, ctx, new_voice_limit):
        #database.db.connect(reuse_if_open=True)
        member = ctx.guild.get_member(ctx.author.id)
        timestamp2 = datetime.now()
        MT = discord.utils.get(ctx.guild.roles, name='Moderation Team')
        MAT = discord.utils.get(ctx.guild.roles, name='Marketing Team')
        TT = discord.utils.get(ctx.guild.roles, name='Technical Team')
        AT = discord.utils.get(ctx.guild.roles, name='Academics Team')
        VP = discord.utils.get(ctx.guild.roles, name='VP')
        CO = discord.utils.get(ctx.guild.roles, name='CO')

        voice_state = member.voice

        if voice_state == None:
            embed = discord.Embed(title = "Unknown Voice Channel", description = "You have to be in a voice channel you own in order to use this!", color = discord.Colour.dark_red())
            return await ctx.send(embed = embed)

        else:
            if voice_state.channel.id in self.presetChannels:
                embed = discord.Embed(title = "UnAuthorized Channel Modification", description = "You are not allowed to modify these channels!\n\n**Error Detection:**\n**1)** Detected Static Channels", color = discord.Colour.dark_red())
                return await ctx.send(embed = embed)

            if member.voice.channel.category_id == self.categoryID:
                query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id))

                if query.exists():
                    try:
                        voiceLIMIT = int(new_voice_limit)
                    except:
                        return await ctx.send("Not a valid number!")
                    else:
                        if voiceLIMIT == 0:
                            return await ctx.send("Sorry, you can't set your voice channel to `0`!")

                        if voiceLIMIT < 0:
                            return await ctx.send("Sorry, you can't set your voice channel to something below `-1`!")
                            
                        if MT not in ctx.author.roles and MAT not in ctx.author.roles and TT not in ctx.author.roles and AT not in ctx.author.roles and VP not in ctx.author.roles and CO not in ctx.author.roles and ctx.author.id != 682715516456140838:
                            if voiceLIMIT > 4:
                                return await ctx.send("You can't increase the voice limit to something bigger then 4 members!")
                            
                            else:
                                await member.voice.channel.edit(user_limit = voiceLIMIT)
                                return await ctx.send("Successfully modified voice limit!")

                        else:
                            if voiceLIMIT > 10:
                                return await ctx.send("You can't increase the voice limit to something bigger then 10 members!")
                            
                            else:
                                await member.voice.channel.edit(user_limit = voiceLIMIT)
                                return await ctx.send("Successfully modified voice limit!")
                    


                else:
                    try:
                        q = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == voice_state.channel.id).get()
                    except:
                        embed = discord.Embed(title = "Ownership Check Failed", description = "This isn't a tutoring channel! Please use the command on an actual tutoring channel!", color = discord.Colour.red())
                    else:
                        embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to end it!", color = discord.Colour.red())
                    finally:
                        await ctx.send(embed = embed)
            else:
                embed = discord.Embed(title = "Unknown Channel", description = "You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a channel you own!", color = discord.Colour.red())
                        

    @commands.command()
    async def disconnect(self, ctx, user: discord.Member):
        database.db.connect(reuse_if_open=True)
        member = ctx.guild.get_member(ctx.author.id)
        timestamp2 = datetime.now()

        voice_state = member.voice

        if voice_state == None:
            embed = discord.Embed(title = "Unknown Voice Channel", description = "You have to be in a voice channel you own in order to use this!", color = discord.Colour.dark_red())
            return await ctx.send(embed = embed)

        else:
            if voice_state.channel.id in self.presetChannels:
                embed = discord.Embed(title = "UnAuthorized Channel Modification", description = "You are not allowed to modify these channels!\n\n**Error Detection:**\n**1)** Detected Static Channels", color = discord.Colour.dark_red())
                return await ctx.send(embed = embed)

            if member.voice.channel.category_id == self.categoryID:
                query = database.VCChannelInfo.select().where((database.VCChannelInfo.authorID == ctx.author.id) & (database.VCChannelInfo.ChannelID == voice_state.channel.id))

                if query.exists():
                    await user.move_to(None)
                    embed = discord.Embed(title = "Disconnected User", description = f"Disconnected {user.mention}!", color = discord.Colour.green())
                    return await ctx.send(embed = embed)


                else:
                    try:
                        q = database.VCChannelInfo.select().where(database.VCChannelInfo.ChannelID == voice_state.channel.id).get()
                    except:
                        embed = discord.Embed(title = "Ownership Check Failed", description = "This isn't a tutoring channel! Please use the command on an actual tutoring channel!", color = discord.Colour.red())
                    else:
                        embed = discord.Embed(title = "Ownership Check Failed", description = f"You are not the owner of this voice channel, please ask the original owner <@{q.authorID}>, to end it!", color = discord.Colour.red())
                    finally:
                        await ctx.send(embed = embed)
            else:
                embed = discord.Embed(title = "Unknown Channel", description = "You are not the owner of this voice channel nor is this a valid channel. Please execute the command under a channel you own!", color = discord.Colour.red())
                        
                await ctx.send(embed = embed)










        


def setup(bot):
    bot.add_cog(SkeletonCMD(bot))


