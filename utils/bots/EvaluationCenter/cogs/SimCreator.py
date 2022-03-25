import discord
from core import database
from core.common import TECH_ID, SandboxConfig, get_extensions
from discord.ext import commands


class SimulatorProfile:
    @staticmethod
    async def create_TicketSys(ctx: commands.Context):
        # category = discord.utils.get(ctx.guild.categories, id=TECH_ID.cat_sandbox)
        query: database.SandboxConfig = (
            database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        )
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
            category = await ctx.guild.create_category(cat[0], position=pos)
            cat[1] = category.id
            if cat[0] == "Other Tickets":
                query.cat_fineartsticket = category.id
            pos += 1
        query.save()

    @staticmethod
    async def cleanup_ticket_sys(ctx: commands.Context):
        query: database.SandboxConfig = (
            database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        )
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
            cat[1] = "None"
            category = discord.utils.get(ctx.guild.categories, id=cat)
            for channel in category.channels:
                await channel.delete()
            await category.delete()
        query.mode = "None"
        query.save()

    @staticmethod
    async def create_PrivVCSys(ctx: commands.Context):
        category = discord.utils.get(ctx.guild.categories, id=SandboxConfig.cat_sandbox)
        q: database.SandboxConfig = (
            database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        )
        q.mode = "TutorVC"

        cp = await ctx.guild.create_text_channel("control-panel", category=category)
        spv = await ctx.guild.create_voice_channel(
            "Start Private VC", category=category
        )
        q.ch_tv_console = cp.id
        q.ch_tv_startvc = spv.id
        q.save()

    @staticmethod
    async def cleanup_PrivVCSys(ctx: commands.Context):
        q: database.SandboxConfig = (
            database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        )
        channels = [q.ch_tv_console, q.ch_tv_startvc]
        for channel in channels:
            ch = await ctx.bot.fetch_channel(channel)
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
        q: database.SandboxConfig = (
            database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        )
        if q.mode == "None":
            if profile == "TicketSys":
                await SP.create_TicketSys(ctx)
            elif profile == "PrivateVC":
                await SP.create_PrivVCSys(ctx)

            for ext in get_extensions():
                try:
                    await self.bot.load_extension(ext)
                except commands.ExtensionAlreadyLoaded:
                    await self.bot.unload_extension(ext)
                    await self.bot.load_extension(ext)
                except commands.ExtensionNotFound:
                    raise commands.ExtensionNotFound(ext)

            await ctx.send("Done!")
        else:
            await ctx.send(
                "Unable to initiate simulation, a simulation is already active. Run the cleanup command first!"
            )

    @sim.command()
    async def clear(self, ctx: commands.Context):
        SP = SimulatorProfile()
        q: database.SandboxConfig = (
            database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        )
        if q.mode == "None":
            return await ctx.send("No simulation currently active.")
        elif q.mode == "TutorVC":
            await SP.cleanup_PrivVCSys(ctx)
        elif q.mode == "TicketSys":
            await SP.cleanup_ticket_sys(ctx)

        for ext in get_extensions():
            try:
                await self.bot.load_extension(ext)
            except commands.ExtensionAlreadyLoaded:
                await self.bot.unload_extension(ext)
                await self.bot.load_extension(ext)
            except commands.ExtensionNotFound:
                raise commands.ExtensionNotFound(ext)

        await ctx.send("Cleared simulation.")

    @sim.command()
    async def identify(self, ctx: commands.Context):
        q: database.SandboxConfig = (
            database.SandboxConfig.select().where(database.SandboxConfig.id == 1).get()
        )
        await ctx.send(f"**Current Simulation:** {q.mode}")


async def setup(bot):
    await bot.add_cog(SituationCreator(bot))
