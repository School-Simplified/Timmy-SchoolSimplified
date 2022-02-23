import inspect
import io
import discord
from core import database
from core.common import rulesDict
from discord import Option, slash_command
from discord.ext import commands
from core.common import MAIN_ID
from discord.commands import permissions

MESSAGEC = "Go chit chat somewhere else, this is for commands only."
MESSAGEMASA = "Hey you ||~~short~~|| *I mean* tall mf, go chit chat somewhere you twat."


class CommandsOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.masa_id = 736765405728735232
        self.rules = rulesDict

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == MAIN_ID.ch_modCommands and not message.author.bot:
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
                        color=discord.Colour.red(),
                    )
                else:
                    embed = discord.Embed(
                        title="Commands ONLY",
                        description=MESSAGEC,
                        color=discord.Colour.red(),
                    )

                await message.channel.send(
                    message.author.mention, embed=embed, delete_after=5.0
                )

    @slash_command(guild_ids=[MAIN_ID.g_main])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rule(self, ctx, num: Option(int, max_value=14, min_value=1)):
        RuleNumber = str(num)
        RuleTitle, RuleDesc = self.rules[int(num)].split(" && ")

        embed = discord.Embed(
            title=f"Rule {RuleNumber}: {RuleTitle}",
            description=RuleDesc,
            color=discord.Colour.green(),
        )
        embed.set_footer(text="Have a question? Feel free to DM a Moderator!")
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(CommandsOnly(bot))
