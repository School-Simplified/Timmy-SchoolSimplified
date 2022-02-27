import json
import requests
import discord
from core.checks import is_botAdmin
from discord.ext import commands
from core.common import TECH_ID, ConfigcatClient, SandboxConfig, config_patch
from core.checks import is_botAdmin
from core import database


class SimulatorProfile:

    @classmethod
    async def create_TicketSys(self, botself, ctx: commands.Context):
        category = discord.utils.get(ctx.guild.categories, id=TECH_ID.cat_sandbox)
        query: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        query.mode = "TickeySys"

        await ctx.guild.create_text_channel("🧧┃chat-help")
        ListofCat = [
            ["Math Tickets", query.cat_mathticket],
            ["Science Tickets", query.cat_scienceticket],
            ["Social Studies Tickets", query.cat_socialstudiesticket],
            ["Essay Tickets", query.cat_essayticket],
            ["English Tickets", query.cat_englishticket],
            ["Language Tickets", query.cat_languageticket],
            ["Other Tickets", query.cat_otherticket],
        ]
        for cat in ListofCat:
            pos = 7
            category = ctx.guild.create_category(cat[0], position=pos)
            cat[1] = category.id
            if cat[0] == "Other Tickets":
                query.cat_fineartsticket = category.id
            pos += 1
        query.save()

    @classmethod
    async def cleanup_TicketSys(self, botself, ctx: commands.Context):
        query: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        ListofCat = [
            ["Math Tickets", query.cat_mathticket],
            ["Science Tickets", query.cat_scienceticket],
            ["Social Studies Tickets", query.cat_socialstudiesticket],
            ["Essay Tickets", query.cat_essayticket],
            ["English Tickets", query.cat_englishticket],
            ["Language Tickets", query.cat_languageticket],
            ["Other Tickets", query.cat_otherticket],
        ]
        for cat in ListofCat:
            cat[1] = None
            category = discord.utils.get(ctx.guild.categories, id=cat)
            for channel in category.channels:
                await channel.delete()
            await category.delete()
        query.mode = "None"
        query.save()


    @classmethod
    async def create_PrivVCSys(self, botself, ctx: commands.Context):
        category = discord.utils.get(ctx.guild.categories, id=SandboxConfig.cat_sandbox)
        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        q.mode = "TutorVC"

        cp = await ctx.guild.create_text_channel("control-panel", category=category)
        spv = await ctx.guild.create_voice_channel("Start Private VC", category=category)
        q.ch_tv_console = cp.id
        q.ch_tv_startvc = spv.id
        q.save()

    @classmethod
    async def cleanup_PrivVCSys(self, botself, ctx: commands.Context):
        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        channels = [q.ch_tv_console, q.ch_tv_startvc]
        for channel in channels:
            ch = await botself.bot.fetch_channel(channel)
            await ch.delete()

        q.mode = "None"
        q.ch_tv_console = None
        q.ch_tv_startvc = None
        q.save()
        



class SituationCreator(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.group(invoke_without_command=True)
    @commands.has_any_role()
    async def sim(self, ctx):
        pass

    @sim.command()
    async def create(self, ctx: commands.Context, profile):
        SP = SimulatorProfile()
        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        if q.mode == "None":
            if profile == "TicketSys":
                await SP.create_TicketSys(self, ctx)
            elif profile == "PrivateVC":
                await SP.create_PrivVCSys(self, ctx)

            await ctx.send("Done!")
        else:
            await ctx.send("Unable to initate simulation, a simulation is already active. Run the cleanup command first!")

    @sim.command()
    async def clear(self, ctx: commands.Context):
        SP = SimulatorProfile()
        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        if q.mode == "None":
            return await ctx.send("No simulation currently active.")
        elif q.mode == "TutorVC":
            await SP.cleanup_PrivVCSys(self, ctx)
        elif q.mode == "TicketSys":
            await SP.cleanup_TicketSys(self, ctx)
        
        await ctx.send("Cleared simulation.")

    @sim.command()
    async def identify(self, ctx: commands.Context):
        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        await ctx.send(f"**Current Simulation:** {q.mode}")

def setup(bot):
    bot.add_cog(SituationCreator(bot))
