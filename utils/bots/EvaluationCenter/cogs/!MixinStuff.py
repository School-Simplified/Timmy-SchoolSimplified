import json
import discord
from core.checks import is_botAdmin
from discord.ext import commands
from core.common import TECH_ID
from core.checks import is_botAdmin
from core import database


class SimulatorProfile:
    async def create_TicketSys(self, ctx: commands.Context):
        category = discord.utils.get(ctx.guild.categories, id=TECH_ID.cat_sandbox)
        await ctx.guild.create_text_channel("🧧┃chat-help")

    async def create_PrivVCSys(self, ctx: commands.Context):
        category = discord.utils.get(ctx.guild.categories, id=TECH_ID.cat_sandbox)
        await ctx.guild.create_text_channel("control-panel")
        await ctx.guild.create_voice_channel("Start Private VC")


class SituationCreator(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_any_role()
    async def sim(self, ctx):
        pass

    @sim.command()
    async def create(self, ctx: commands.Context):
        pass


def setup(bot):
    bot.add_cog(SituationCreator(bot))
