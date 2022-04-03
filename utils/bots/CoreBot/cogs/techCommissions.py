from typing import Literal

import discord
from discord import ui, app_commands
from discord.ext import commands, tasks
from core.common import TECH_ID, Emoji, get_active_or_archived_thread
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
    async def commission(self, ctx: commands.Context, action: Literal["close", "reopen"]):
        channel: discord.TextChannel = self.bot.get_channel(TECH_ID.ch_botreq)
        thread = ctx.channel

        if not isinstance(thread, discord.Thread):
            await ctx.send("Not a bot commission.")
            return

        if action == "close":
            query = database.TechCommissions.select().where(database.TechCommissions.ThreadID == thread.id)
            if thread not in channel.threads or not query.exists():
                await ctx.send("This commission is already closed.")
                return
            else:
                query.get()
                query.delete_instance()
                query.save()

                current_name = thread.name
                new_name = f"[CLOSED] {current_name}"
                await thread.edit(archived=True, name=new_name)

                await ctx.send("Commission closed! You can find the commission in the archived threads of that channel.")

        elif action == "reopen":
            query = database.TechCommissions.select().where(database.TechCommissions.ThreadID == thread.id)
            if query.exists() or thread in channel.threads:
                await ctx.send(
                    "This commission is already open. You can close it by doing `/commission-close`")
                return
            else:
                query = database.TechCommissions.create(ThreadID=thread.id)
                query.save()

                current_name = thread.name
                new_name = current_name.replace("[CLOSED]", "").strip()
                await thread.edit(archived=False, name=new_name)
                await ctx.send("Re-opened commission!")

        else:
            raise ValueError("Action is neither 'close' nor 'reopen'.")

    @tasks.loop(seconds=60.0)
    async def autoUnarchiveThread(self):
        """
        Creates a task loop to make sure threads don't automatically archive due to inactivity.
        """

        guild = self.bot.get_guild(TECH_ID.g_tech)
        query = database.TechCommissions.select()
        entries = [entry.id for entry in query]

        if entries:
            for entry in entries:
                query = query.select().where(database.TechCommissions.id == entry)
                query = query.get()

                thread = await get_active_or_archived_thread(guild, query.ThreadID)

                if thread is not None:
                    await thread.edit(archived=False)
                else:
                    raise ValueError(f"Thread with id {query.ThreadID} not found.")

    @autoUnarchiveThread.before_loop
    async def before_loop_(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(TechProjectCMD(bot))
