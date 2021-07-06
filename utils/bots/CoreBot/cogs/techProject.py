import asyncio
import datetime
import json
import logging
from datetime import datetime, timedelta
import random

import discord
from core import database
from core.checks import is_botAdmin
from discord.ext import commands
from redbot.core.utils.tunnel import Tunnel


class SkeletonCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
                    await channel.send("Submitted response...")


        except asyncio.TimeoutError:
            await channel.send("Looks like you didn't react in time, please try again later!")





def setup(bot):
    bot.add_cog(SkeletonCMD(bot))



    