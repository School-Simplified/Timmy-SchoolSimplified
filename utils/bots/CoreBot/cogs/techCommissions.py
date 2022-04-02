import discord
from discord import ui
from discord.ext import commands, tasks
from core.common import TECH_ID, Emoji
from core.checks import is_botAdmin
from core import database


class BotRequestModal(ui.Modal, title="Bot Development Request"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    titleTI = ui.TextInput(
        label="What is a descriptive title for your project?",
        style=discord.TextStyle.long,
        max_length=1024,
    )

    teamTI = ui.TextInput(
        label="Which team is this project for?",
        style=discord.TextStyle.short,
        max_length=1024
    )

    descriptionTI = ui.TextInput(
        label="Write a brief description of the project.",
        style=discord.TextStyle.long,
        max_length=1024,
    )

    approvalTI = ui.TextInput(
        label="Do you have approval for this commission?",
        style=discord.TextStyle.long,
        max_length=1024,
    )

    anythingElseTI = ui.TextInput(
        label="Anything else?",
        style=discord.TextStyle.long,
        required=False,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="Got it! Please wait while I create your ticket.", ephemeral=True
        )

        embed = discord.Embed(
            title="Bot Developer Commission", color=discord.Color.blurple()
        )
        embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.avatar.url
        )
        embed.add_field(
            name="Project Title", value=self.titleTI.value, inline=False
        )
        embed.add_field(
            name="Team Requester", value=self.teamTI.value, inline=False
        )
        embed.add_field(
            name="Project Description", value=self.descriptionTI.value, inline=False
        )
        embed.add_field(name="Approval", value=self.approvalTI.value, inline=False)
        embed.add_field(
            name="Anything else?", value=self.anythingElseTI.value, inline=False
        )
        embed.set_footer(text="Bot Developer Commission")

        c_ch: discord.TextChannel = self.bot.get_channel(TECH_ID.ch_botreq)
        msg: discord.Message = await c_ch.send(interaction.user.mention, embed=embed)
        thread = await msg.create_thread(name=self.titleTI.value)
        q: database.TechCommissionArchiveLog = database.TechCommissionArchiveLog.create(ThreadID=thread.id)
        q.save()

        await thread.send(
            f"{interaction.user.mention} has requested a bot development project.\n<@&{TECH_ID.r_botDeveloper}>"
        )


class CommissionTechButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Start Commission",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:tech_pjt",
        emoji="📝",
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button,):
        modal = BotRequestModal(self.bot)
        return await interaction.response.send_modal(modal)


class TechProjectCMD(commands.Cog):
    """
    Commands for bot commissions
    """
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.__cog_name__ = "Bot Commissions"
        self.autoUnarchiveThread.start()


    @property
    def display_emoji(self) -> str:
        return Emoji.pythonLogo


    async def cog_unload(self):
        self.autoUnarchiveThread.cancel()

    @commands.command()
    @is_botAdmin
    async def techEmbed(self, ctx):
        embed = discord.Embed(
            title="Bot Developer Commissions", color=discord.Color.brand_green()
        )
        embed.add_field(
            name="Get Started",
            value="To get started, click the button below!\n*Please make sure you are authorized to make commissions!*",
        )
        embed.set_footer(
            text="The Bot Development Team has the right to cancel and ignore any commissions if deemed appropriate. "
                 "We also have the right to cancel and ignore any commissions if an improper deadline is given, "
                 "please make sure you create a commission ahead of time and not right before a due date",
        )
        view = CommissionTechButton(self.bot)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    async def closeThread(self, ctx: commands.Context):
        channel: discord.TextChannel = self.bot.get_channel(TECH_ID.ch_botreq)
        thread: discord.Thread = ctx.channel

        if thread in channel.threads:
            await ctx.send("Closed thread!")
            query = database.TechCommissionArchiveLog.create(ThreadID=thread.id)
            query.save()

            await thread.edit(archived=True)
        else:
            await ctx.send("Not a valid thread.")

    @commands.command()
    async def openThread(self, ctx: commands.Context):
        channel: discord.TextChannel = self.bot.get_channel(TECH_ID.ch_botreq)
        thread: discord.Thread = ctx.channel

        if thread in channel.threads:
            query = database.TechCommissionArchiveLog.select().where(
                database.TechCommissionArchiveLog.ThreadID == thread.id
            )
            if query.exists():
                query.delete_instance()

                await thread.edit(archived=False)
                await ctx.send("Re-opened thread!")
            else:
                await ctx.send("Unknown Error")
        else:
            await ctx.send("Not a valid thread.")

    @tasks.loop(seconds=60.0)
    async def autoUnarchiveThread(self):
        """
        Creates a task loop to make sure threads don't automatically archive due to inactivity.
        """

        guild = self.bot.get_guild(TECH_ID.g_tech)
        print(TECH_ID.g_tech, int(TECH_ID.g_tech))
        print(guild)
        query = database.TechCommissionArchiveLog.select()
        entries = [entry.id for entry in query]

        if entries:
            for entry in entries:
                thread: discord.Thread = guild.get_thread(entry.ThreadID)
                await thread.edit(archived=False)

    @autoUnarchiveThread.before_loop
    async def before_loop_(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(TechProjectCMD(bot))
