import asyncio
from contextlib import redirect_stdout
from datetime import datetime

import aiohttp
import discord
from core import database
from core.checks import is_botAdmin3
from core.common import Emoji
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.inputdict = {1: "Quote", 2: "Inspirational Message"}
        self.reactions = ['✅', '❌']

    @commands.command()
    async def quotesend(self, ctx):
        channel = await ctx.author.create_dm()

        def check(m):
            return m.content is not None and m.channel == channel and m.author is not self.bot.user

        def check2(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

        embed = discord.Embed(title = "1) What will you be Sending in?", description = f"Respond with the following key:\n{Emoji.barrow} Respond with **1** if you are sending in a `quote`.\n{Emoji.barrow} Respond with **2** if you are sending in a `inspirational message`.", color = discord.Colour.green())
        await channel.send(embed = embed)

        answer1 = await self.bot.wait_for('message', check=check)
        try: 
            int(answer1.content)
        except:
            return await channel.send("Are you sure you sent either *1* or *2*?\nCanceling Database Input, please try again!")
        
        if int(answer1.content) in [1, 2]:
            embed = discord.Embed(title = f"2) Send in your {self.inputdict[int(answer1.content)]}", description = f"Respond with the {self.inputdict[int(answer1.content)]}.\n{Emoji.barrow} Markdown **is** supported!\n{Emoji.barrow} Keep the message short (less then 1000 characters)!\n{Emoji.barrow} Some emojis are supported. (Emojis that are on the main server or any server that I am in!)", color = discord.Colour.green())
            await channel.send(embed = embed)
            answer2 = await self.bot.wait_for('message', check=check)

            query = database.MotivationalQuotes.select().where(database.MotivationalQuotes.item == answer2.content)
            if query.exists():
                embed = discord.Embed(title = "ERROR: Code 1", description = f"This item is already located in the database!\n{Emoji.barrow} Try rephrasing this message or contact SpaceTurtle#0001 if you would like it removed or modified!", color = discord.Colour.red())
                return await channel.send(embed = embed)
                
            embed = discord.Embed(title = f"3) Confirm your {self.inputdict[int(answer1.content)]}", description = f"Respond with the appropriate reactions.\n{Emoji.barrow} You have **150** seconds to react.", color = discord.Colour.green())
            message = await channel.send(embed = embed)
            answer3 = await self.bot.wait_for('message', check=check)

            
            for emoji in self.reactions:
                await message.add_reaction(emoji)

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=150.0, check=check2)

                if str(reaction.emoji) == "❌":
                    await channel.send("Canceled Form...")
                    await message.delete()
                    return
                else:

                    database.db.connect(reuse_if_open=True)
                    q: database.MotivationalQuotes = database.MotivationalQuotes.create(discordID = ctx.author.id, item = answer2.content, type = self.inputdict[int(answer1.content)])
                    q.save()
                    await channel.send(f"Your quote has been added successfully.\nItem #: `{q.id}`")
                    database.db.close()

                    await message.delete()
                    

            except asyncio.TimeoutError:
                await channel.send("Looks like you didn't react in time, please try again later!")



        else:
            return await channel.send("Are you sure you sent either *1* or *2*?\nCanceling Database Input, please try again!")


def setup(bot):
    bot.add_cog(Quotes(bot))
