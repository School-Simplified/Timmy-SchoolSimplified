from typing import Literal

import discord
from discord import ui, app_commands
from discord.ext import commands, tasks

from core import database
from core.checks import slash_is_bot_admin_3, slash_is_bot_admin
from core.common import TechID, Emoji, StaffID, LeaderID


class BotRequestModal(ui.Modal, title="Bot Development Request"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    titleTI = ui.TextInput(
        label="What is a descriptive title for your project?",
        style=discord.TextStyle.short,
        max_length=1024,
        placeholder="Do not explain the project in detail here: just a descriptive title.",
    )

    teamTI = ui.TextInput(
        label="Which team is this project for?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    descriptionTI = ui.TextInput(
        label="Write a description of the project.",
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
        member = interaction.guild.get_member(interaction.user.id)
        c_ch: discord.ForumChannel = self.bot.get_channel(LeaderID.ch_bot_commissions)
        role = discord.utils.get(interaction.guild.roles, id=LeaderID.r_bot_whitelist_commission)

        await interaction.response.send_message(
            content="Got it! Please wait while I create your ticket.", ephemeral=True
        )

        embed = discord.Embed(
            title="Bot Developer Commission", color=discord.Color.blurple()
        )
        embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.avatar.url
        )
        embed.add_field(name="Project Title", value=self.titleTI.value, inline=False)
        embed.add_field(name="Team Requester", value=self.teamTI.value, inline=False)
        embed.add_field(
            name="Project Description", value=self.descriptionTI.value, inline=False
        )
        embed.add_field(name="Approval", value=self.approvalTI.value, inline=False)
        embed.add_field(
            name="Anything else?", value=f"E: {self.anythingElseTI.value}", inline=False
        )
        embed.set_footer(text="Bot Developer Commission")

        thread_with_message = await c_ch.create_thread(name=f"⚪-{self.titleTI.value}", content=interaction.user.mention, embed=embed)
        thread = thread_with_message.thread
        await thread.add_tags(discord.Object(LeaderID.t_pending_claim), discord.Object(LeaderID.t_bot_commission))

        await member.add_roles(role, reason="Bot Developer Commission")
        await thread.send(
            f"{interaction.user.mention} has requested a bot development project.\n<@ {TechID.r_bot_developer}>"
        )


class SubdomainForm(ui.Modal, title="Custom Subdomain Request"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    subdomain = ui.TextInput(
        label="What Subdomain are you requesting?",
        style=discord.TextStyle.short,
        max_length=50,
        default="REPLACE_WANTED_SUBDOMAIN_HERE.ssimpl.org",
    )

    reason = ui.TextInput(
        label="Reason/Usage for the subdomain?",
        style=discord.TextStyle.long,
        max_length=1024,
    )

    team = ui.TextInput(
        label="What team/dept. is this subdomain for?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    approval = ui.TextInput(
        label="Do you have approval for this commission?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    anything_else = ui.TextInput(
        label="Anything else?",
        style=discord.TextStyle.long,
        required=False,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        c_ch: discord.ForumChannel = self.bot.get_channel(LeaderID.ch_bot_commissions)
        role = discord.utils.get(interaction.guild.roles, id=LeaderID.r_bot_whitelist_commission)
        member = interaction.guild.get_member(interaction.user.id)

        await interaction.response.send_message(
            content="Got it! Please wait while I create your ticket.", ephemeral=True
        )

        embed = discord.Embed(
            title="Subdomain Commission", color=discord.Color.blurple()
        )
        embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.avatar.url
        )
        embed.add_field(
            name="Subdomain Requested:", value=self.subdomain.value, inline=False
        )
        embed.add_field(name="Team Requester:", value=self.team.value, inline=False)
        embed.add_field(name="Subdomain Usage:", value=self.reason.value, inline=False)
        embed.add_field(name="Approval", value=self.approval.value, inline=False)
        embed.add_field(
            name="Anything else?", value=f"E: {self.anything_else.value}", inline=False
        )
        embed.set_footer(text="Bot Developer Commission")
        thread_with_message = await c_ch.create_thread(name=f"⚪-{self.subdomain.value}", content=interaction.user.mention, embed=embed)
        thread = thread_with_message.thread

        await thread.add_tags(discord.Object(LeaderID.t_pending_claim), discord.Object(LeaderID.t_subdomain_commission))
        await member.add_roles(role, reason="Bot Developer Commission")
        await thread.send(
            f"{interaction.user.mention} has requested a subdomain.\n<@409152798609899530>"
        )


class CommissionTechButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Start Bot Commission",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:tech_pjt",
        emoji="📝",
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.guild.id == TechID.g_tech:
            return await interaction.response.send_message(
                f"{interaction.user.mention} commissions have moved to the Staff Resources & Information Server!\nYou "
                f"can start one here: <#956619270899499028>.",
                ephemeral=True,
            )

        modal = BotRequestModal(self.bot)
        return await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="Request Custom Subdomain",
        style=discord.ButtonStyle.grey,
        custom_id="persistent_view:custom_subdomain",
        emoji="🖇",
    )
    async def custom_subdomain(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.guild.id == TechID.g_tech:
            return await interaction.response.send_message(
                f"{interaction.user.mention} commissions have moved to the Staff Resources & Information Server!\nYou "
                f"can start one here: <#956619270899499028>.",
                ephemeral=True,
            )

        modal = SubdomainForm(self.bot)
        return await interaction.response.send_modal(modal)


class TechProjectCMD(commands.Cog):
    """
    Commands for bot commissions
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.emoji_to_tag = {
            "⚪": LeaderID.t_pending_claim,
            "🎯": LeaderID.t_claimed,
            "🟡": LeaderID.t_in_progress,
            "🟢": LeaderID.t_completed,
            "🔴": LeaderID.t_not_possible,
        }
        self.__cog_name__ = "Bot Commissions"

    @property
    def display_emoji(self) -> str:
        return Emoji.pythonLogo

    BDC = app_commands.Group(
        name="bot_commissions",
        description="Manage bot commissions!",
        guild_ids=[StaffID.g_staff_resources],
    )

    @BDC.command(
        description="Change the status of a bot commission. | Only to be used by Bot Developer Staff."
    )
    @slash_is_bot_admin()
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.channel.id))
    @app_commands.describe(status="Read options for the list of statuses.")
    async def status_update(
        self,
        interaction: discord.Interaction,
        status: Literal[
            "⚪️ - Pending developer review; unclaimed.",
            "🎯 - Claimed; used for internal tracking. ",
            "🔴 - Extra information needed or not possible.",
            "🟡 - In progress; working on the project.",
            "🟢 - Complete; pending requestor to accept final product.",
        ],
    ):
        channel: discord.ForumChannel = self.bot.get_channel(LeaderID.ch_bot_commissions)
        thread: discord.Thread = interaction.channel

        if not isinstance(thread, discord.Thread) or thread.parent_id != channel.id:
            return await interaction.response.send_message(
                "This is not a bot commission.", ephemeral=True
            )
        channel_name = thread.name.split("-")[1]
        status = str(status)

        l = status.split(" - ")
        status = l[0]
        definition = l[1]
        tag_id = self.emoji_to_tag[status]

        await thread.edit(name=f"{status}-{channel_name}")
        for tag in thread.applied_tags:
            await thread.remove_tags(discord.Object(tag.id))

        await thread.add_tags(discord.Object(LeaderID.t_bot_commission), discord.Object(tag_id), reason="Bot Commission Status Update")
        await interaction.response.send_message(
            f"**{interaction.user.mention}** updated the status of this bot commission to {status} | `{definition}`"
        )

    @BDC.command(description="Close a bot commission. | Only to be used by Bot Developer Staff.")
    @slash_is_bot_admin()
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.guild_id, i.channel.id))
    async def close(
        self, interaction: discord.Interaction
    ):
        channel: discord.TextChannel = self.bot.get_channel(LeaderID.ch_bot_commissions)
        thread = interaction.channel

        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message(
                "This is not a bot commission.", ephemeral=True
            )
            return

        query = database.TechCommissionArchiveLog.select().where(
            database.TechCommissionArchiveLog.ThreadID == thread.id
        )
        if thread not in channel.threads or query.exists():
            await interaction.response.send_message(
                "This commission is already closed.", ephemeral=True
            )
            return
        else:
            query = database.TechCommissionArchiveLog.create(ThreadID=thread.id)
            query.save()

            await interaction.response.send_message(
                "Commission closed! You can find the commission in the archived threads of that channel."
            )
            await thread.edit(archived=True)

    @commands.Cog.listener("on_message")
    async def auto_open_commission(self, message: discord.Message):
        channel: discord.TextChannel = self.bot.get_channel(TechID.ch_bot_requests)

        if (
            isinstance(message.channel, discord.Thread)
            and message.type == discord.MessageType.default
            and message.channel in channel.threads
        ):

            query = database.TechCommissionArchiveLog.select().where(
                database.TechCommissionArchiveLog.ThreadID == message.channel.id
            )
            if query.exists():
                result = query.get()
                result.delete_instance()

                await message.reply(content="Commission re-opened!")


async def setup(bot: commands.Bot):
    await bot.add_cog(TechProjectCMD(bot))
