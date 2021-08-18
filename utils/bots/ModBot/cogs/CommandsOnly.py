import inspect
import io
import discord
from core import database
from core.common import rulesDict
from discord.ext import commands

MESSAGEC = "Go chit chat somewhere else, this is for commands only."
MESSAGEMASA = "Hey you ||~~short~~|| *I mean* tall mf, go chit chat somewhere you twat."

class CommandsOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.masa_id = 736765405728735232
        self.channelID = 786057630383865858
        self.rules = rulesDict

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == 786057630383865858 and not message.author.bot:
            prefix = []
            for p in database.WhitelistedPrefix:
                prefix.append(p.prefix)

            res = list(filter(message.content.startswith, prefix)) != []

            if not res:
                await message.delete()
                if message.author.id == self.masa_id:
                    embed = discord.Embed(
                        title="Commands ONLY", description=MESSAGEMASA, color=discord.Colour.red())
                else:
                    embed = discord.Embed(
                        title="Commands ONLY", description=MESSAGEC, color=discord.Colour.red())

                await message.channel.send(message.author.mention, embed=embed, delete_after=5.0)
                    


    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rule(self, ctx, num):
        try:
            num = int(num)
        except ValueError:
            await ctx.message.add_reaction("❌")
        else:
            if num > 14 or num <= 0:
                await ctx.message.add_reaction("❌")
            else:
                RuleNumber = str(num)
                RuleTitle, RuleDesc = self.rules[int(num)].split(" && ")

                embed = discord.Embed(title = f"Rule {RuleNumber}: {RuleTitle}", description = RuleDesc, color = discord.Colour.green())
                embed.set_footer(text = "Have a question? Feel free to DM a Moderator!")
                await ctx.send(embed = embed)

    

def setup(bot):
    bot.add_cog(CommandsOnly(bot))
