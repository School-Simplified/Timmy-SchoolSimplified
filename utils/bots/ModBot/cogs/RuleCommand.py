import inspect
import io
import textwrap
import traceback
from contextlib import redirect_stdout
import os
import aiohttp
from discord.ext import commands
import discord
from discord.ext import tasks
from datetime import timedelta, datetime


MESSAGEC = "Go chit chat somewhere else, this is for commands only."
MESSAGEMASA = "Hey you ||~~short~~|| *I mean* tall mf, go chit chat somewhere you twat."

rulesDict = {
    1: "All Terms of Service and Community Guidelines apply.",
    2: "English only discussion.",
    3: "No trolling or disruptive behavior.",
    4: "No verbal abuse, insults, or threats.",
    5: "No excessive or harmful use of profanity.",
    6: "No toxic behavior or harassment.",
    7: "No discriminatory jokes or language towards an individual or group.",
    8: "No content that does not belong in a school server.",
    9: "No sexism, racism, homophobia, etc.",
    10: "No pedophilia or creeping behavior.",
    11: "No cheating in any form.",
    12: "No self-promotion of any form. ",
    13: "No evading punishments.",
    14: "No spamming.",
    15: "No hopping between voice chats.",
    16: "No mic/stream spamming in voice chats.",
    17: "No sharing of private content without the owner’s active consent.",
    18: "No impersonation.",
    19: "Keep debates in <#861813108758413323>.",
    20: "Keep chats and conversations relevant.",
    21: "Maintain a positive atmosphere."
}

class CommandsOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rules = rulesDict
        

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rule(self, ctx, num):
        try:
            num = int(num)
        except ValueError:
            return print("Invalid Number")
        else:
            if num > 21 or num <= 0:
                return print("Invalid Number")
            else:
                embed = discord.Embed(title = f"Rule Number {str(num)}:", description = self.rules[int(num)], color = discord.Colour.green())
                embed.set_footer(text = "Contact a Moderator for more information.")
                await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(CommandsOnly(bot))