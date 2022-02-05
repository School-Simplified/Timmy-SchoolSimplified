import re

import discord
from core.common import Others, hexColors, MAIN_ID
from core.checks import is_botAdmin, predicate_LV1
from core.gmailapi import auth, create_message
from discord.ext import commands
from discord import Option, slash_command
from discord.commands import permissions

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def email_check(email):
    if re.fullmatch(regex, email):
        return True

    else:
        return False


class GmailAPI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @slash_command(
        guild_ids=[MAIN_ID.g_main]
    )
    @permissions.has_any_role(
        "Staff"
    )
    async def email(
            self,
            ctx: discord.ApplicationContext,
            to: Option(str, description="Who to send your email to"),
            subject: Option(str, description="Your email subject"),
            message: Option(str, description="Your email message")):
        """Send a message to a user via their email.
        """
        if not predicate_LV1(ctx):  # EXTRA CHECK
            return await ctx.respond("You do not have the required permissions!")
        if not email_check(to):
            await ctx.respond("That is not a valid email address!")
            return

        message = message + f"\nSent from: {ctx.author}"

        service = auth()
        create_message(service, "timmy@schoolsimplified.org", to, subject, message)
        await ctx.respond("Message sent via gmail!")


def setup(bot):
    bot.add_cog(GmailAPI(bot))
