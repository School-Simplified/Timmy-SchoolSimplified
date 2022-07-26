import discord
from discord.ext import commands

from core import database
from core.common import MainID
from core.common import rulesDict

MESSAGEC = "Go chit chat somewhere else, this is for commands only."
MESSAGEMASA = "Hey you ||~~short~~|| *I mean* tall mf, go chit chat somewhere you twat."


class CommandsOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.masa_id = 736765405728735232
        self.rules = rulesDict

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == MainID.ch_mod_commands and not message.author.bot:
            prefix = []
            for p in database.WhitelistedPrefix:
                prefix.append(p.prefix)

            res = list(filter(message.content.startswith, prefix)) != []

            if not res:
                await message.delete()
                if message.author.id == self.masa_id:
                    embed = discord.Embed(
                        title="Commands ONLY",
                        description=MESSAGEMASA,
                        color=discord.Colour.brand_red(),
                    )
                else:
                    embed = discord.Embed(
                        title="Commands ONLY",
                        description=MESSAGEC,
                        color=discord.Colour.brand_red(),
                    )

                await message.channel.send(
                    message.author.mention, embed=embed, delete_after=5.0
                )


async def setup(bot):
    await bot.add_cog(CommandsOnly(bot))
