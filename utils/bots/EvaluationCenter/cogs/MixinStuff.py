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
        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        q.mode = "TickeySys"
        q.save()

        await ctx.guild.create_text_channel("🧧┃chat-help")
        ListofCat = [
            ["Math Tickets", "cat_mathticket"],
            ["Science Tickets", "cat_scienceticket"],
            ["Social Studies Tickets", "cat_socialstudiesticket"],
            ["Essay Tickets", "cat_essayticket"],
            ["English Tickets", "cat_englishticket"],
            ["Other Tickets", "cat_otherticket"],
        ]
        for cat in ListofCat:
            pos = 7
            category = ctx.guild.create_category(cat[0], position=pos)
            config_patch(cat[1], category.id)
            if cat[0] == "cat_otherticket":
                config_patch("cat_fineartsticket", category.id)
            pos += 1

    @classmethod
    async def cleanup_TicketSys(self, botself, ctx: commands.Context):
        catIDs = [
            SandboxConfig.cat_mathTicket,
            SandboxConfig.cat_scienceTicket,
            SandboxConfig.cat_socialStudiesTicket,
            SandboxConfig.cat_englishTicket,
            SandboxConfig.cat_essayTicket,
            SandboxConfig.cat_otherTicket,
            SandboxConfig.cat_otherTicket,
        ]
        for cat in catIDs:
            category = discord.utils.get(ctx.guild.categories, id=cat)
            for channel in category.channels:
                await channel.delete()
            await category.delete()
        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        q.mode = "None"
        q.save()


    @classmethod
    async def create_PrivVCSys(self, botself, ctx: commands.Context):
        category = discord.utils.get(ctx.guild.categories, id=SandboxConfig.cat_sandbox)
        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        q.mode = "TutorVC"
        q.save()

        cp = await ctx.guild.create_text_channel("control-panel", category=category)
        spv = await ctx.guild.create_voice_channel("Start Private VC", category=category)
        r=config_patch("ch_tv_console", cp.id)
        r2=config_patch("ch_tv_startvc", spv.id)

    @classmethod
    async def cleanup_PrivVCSys(self, botself, ctx: commands.Context):
        channels = [SandboxConfig.ch_TV_console, SandboxConfig.ch_TV_startVC]
        for channel in channels:
            ch = await botself.bot.fetch_channel(channel)
            await ch.delete()

        q: database.SandboxConfig = database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        q.mode = "None"
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
