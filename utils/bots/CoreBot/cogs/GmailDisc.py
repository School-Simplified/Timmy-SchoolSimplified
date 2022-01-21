import re

import discord
from core.common import Others, hexColors
from core.checks import is_botAdmin
from core.gmailapi import auth, create_message
from discord.ext import commands

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def email_check(email):
    if(re.fullmatch(regex, email)):
        return True

    else:
        return False

class GmailAPI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["email"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @is_botAdmin
    async def send(self, ctx: commands.Context, to: str, subject: str, *, message: str):
        """Send a message to a user via their email.
        """
        if not email_check(to):
            await ctx.send("That is not a valid email address!")
            return

        message = message + f"\nSent from: {ctx.author.name}#{ctx.author.discriminator}"

        service = auth()
        message = create_message(service, "timmy@schoolsimplified.org", to, subject, message)
        await ctx.send("Message sent via gmail!")


        


        

def setup(bot):
    bot.add_cog(GmailAPI(bot))
