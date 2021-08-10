import asyncio
import datetime
import json
import logging
import random
from datetime import datetime, timedelta

import discord
from core import database
from core.checks import is_botAdmin, is_botAdmin3
from discord.ext import commands

async def createChannel(self, ctx, type, member):
    
    if type == "Developer":
        category = discord.utils.get(ctx.guild.categories, id= 873261268495106119)
        embed = discord.Embed(title = "Developer Ticket", description = f"Welcome {member.mention}! A developer will be with you shortly.", color = discord.Color.green())

    else:
        return BaseException("ERROR: unknown type")


    DDM = discord.utils.get(ctx.guild.roles, name='Developer Manager')
    ADT = discord.utils.get(ctx.guild.roles, name='Assistant Dev Manager')
    DT = discord.utils.get(ctx.guild.roles, name='Developer')

    num = len(category.channels)
    channel = await ctx.guild.create_text_channel(f'developer-{num}', category = category)

    controlTicket = discord.Embed(title = "Control Panel", description = "To end this ticket, react to the lock emoji!", color = discord.Colour.gold())
    await channel.send(member.mention)
    msg = await channel.send(embed = controlTicket)
    await msg.add_reaction("🔒")

    await channel.set_permissions(DDM, send_messages = True, read_messages = True, reason="Ticket Perms")
    await channel.set_permissions(ADT, send_messages = True, read_messages = True, reason="Ticket Perms")
    await channel.set_permissions(DT, send_messages = True, read_messages = True, reason="Ticket Perms")

    await channel.send(embed = embed)
    return channel

class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def techembedc(self, ctx):
        embed = discord.Embed(title = "Technical Team Commissions", color = discord.Color.green())
        embed.add_field(name = "Developer Commissions", value = "If you'd like to start a Developer Commission, please fill out the form via `+request` and a ticket will autoamtically be created for you!")
        embed.add_field(name = "Discord Commissions", value = "If you'd like to start a Discord Commission, please react with <:discord:812757175465934899> !", inline = False)
        await ctx.send(embed = embed)


    @commands.command()
    async def request(self, ctx):
        if ctx.guild.id != 805593783684562965:
            return

        await ctx.message.delete()

        channel = await ctx.author.create_dm()
        await ctx.send("Check DMs!")

        def check(m):
            return m.content is not None and m.channel == channel and m.author is not self.bot.user

        embed = discord.Embed(title = "Reminders", description = "1) Please remember that you need to have prior permission (if you aren't a manager) before requesting a tech team project!\n\n2) Make sure the responses you provide are **short** and **to the point!**\n3) **If you have any questions, DM a Technical VP!**", color = discord.Colour.red())
        await channel.send(embed = embed)

        embed = discord.Embed(title = "Q1: What is a descriptive title for your project?", color = discord.Colour.gold())
        await channel.send(embed = embed)
        answer1 = await self.bot.wait_for('message', check=check)

        embed = discord.Embed(title = "Q2: Which of these categories does your project suggestion fit under?", description = "**Options:**\n-> Discord Bot\n-> Database\n-> Webpage\n-> Other...", color = discord.Colour.gold())
        await channel.send(embed = embed)
        answer2 = await self.bot.wait_for('message', check=check)

        embed = discord.Embed(title = "Q3: Which team is this project for?", color = discord.Colour.gold())
        await channel.send(embed = embed)
        answer3 = await self.bot.wait_for('message', check=check)

        embed = discord.Embed(title = "Q4: Please write a brief description of the project. ", color = discord.Colour.gold())
        await channel.send(embed = embed)
        answer4 = await self.bot.wait_for('message', check=check)

        embed = discord.Embed(title = "Q5: Have you received approval from a manager for this project (or are you a manager yourself)?", color = discord.Colour.gold())
        await channel.send(embed = embed)
        answer5 = await self.bot.wait_for('message', check=check)

        embed = discord.Embed(title = "Q6: Anything else?", color = discord.Colour.gold())
        await channel.send(embed = embed)
        answer6 = await self.bot.wait_for('message', check=check)

        embed = discord.Embed(title = "Confirm Responses...", description = "Are you ready to submit these responses?" ,color = discord.Colour.gold())
        message = await channel.send(embed = embed)

        reactions = ['✅', '❌']
        for emoji in reactions:
            await message.add_reaction(emoji)

        def check2(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=150.0, check=check2)
            if str(reaction.emoji) == "❌":
                await channel.send("Canceled Form...")
                await message.delete()
                return
            else:
                embed = discord.Embed(title = "New Project Request", description = f"Project Requested by {ctx.author.mention}", color = discord.Colour.green())
                embed.add_field(name = "Q1: What is a descriptive title for your project?", value = answer1.content)
                embed.add_field(name = "Q2: Which of these categories does your project suggestion fit under?", value = answer2.content)
                embed.add_field(name = "Q3: Which team is this project for?", value = answer3.content)
                embed.add_field(name = "Q4: Please write a brief description of the project.", value = answer4.content)
                embed.add_field(name = "Q5: Have you received approval from a manager for this project (or are you a manager yourself)?", value = answer5.content)
                embed.add_field(name = "Q6: Anything else?", value = answer6.content)

                PJC = await self.bot.fetch_channel(849722616880300061)
                try:
                    await PJC.send(embed = embed)
                except:
                    await ctx.send("Error sending the response, maybe you hit the character limit?")
                else:
                    category = discord.utils.get(ctx.guild.categories, name="Tech Commission Tickets")
                    await channel.send("Submitted response...")

                    member = ctx.guild.get_member(ctx.author.id)
                    TicketCH = await createChannel(self, ctx, "Developer", member)

                    await TicketCH.send("Submitted Report:", embed = embed)
                    await channel.send(f"Please use {TicketCH.mention} if you wish to follow up on your commission!")

        except asyncio.TimeoutError:
            await channel.send("Looks like you didn't react in time, please try again later!")


    @commands.command()
    @is_botAdmin3
    async def projectR(self, ctx, user: discord.User, type, projectname, *, notes = None):
        embed = discord.Embed(title = "Project Announcement", description = "The assignee that has taken up your project request has an update for you!", color =discord.Color.green())
        embed.add_field(name = "Status", value = f"Project Status: `{type}`\n-> Project: {projectname}\n-> Project Assignee: {ctx.author.mention}")
        embed.set_footer(text = "DM's are not monitored, DM your Project Requester for more information.")
        if notes != None:
            embed.add_field(name = "Notes", value = notes)

        await user.send(embed = embed)
        await ctx.send("Sent report!\n", embed = embed)

def setup(bot):
    bot.add_cog(SkeletonCMD(bot))



    