from datetime import datetime

import discord
from discord import ui, app_commands
from discord.ext import commands

from core import database
from core.common import TechID, Emoji, StaffID, ButtonHandler


class WebRequestModal(ui.Modal, title="Web Development Request"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    priority = ui.TextInput(
        label="Priority of the request.",
        style=discord.TextStyle.short,
        max_length=1024,
        placeholder="MISC, LOW, MED, HIGH, or CRIT",
    )

    request_type = ui.TextInput(
        label="Request Type",
        style=discord.TextStyle.short,
        max_length=1024,
        placeholder="Content Changes, Typo Fixes, Page Redesign, or Build New Page",
    )

    deadline = ui.TextInput(
        label="Provide a reasonable deadline if available.",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    title_commission = ui.TextInput(
        label="Provide a title for your request.",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    information = ui.TextInput(
        label="Provide all details regarding your request.",
        style=discord.TextStyle.long,
        required=False,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        mgm_server = self.bot.get_guild(StaffID.g_staff_resources)
        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_web_requests
        )
        member = interaction.guild.get_member(interaction.user.id)

        ticket_channel = await ticket_category.create_text_channel(
            f"{interaction.user.name}-web-request",
            topic=f"{interaction.user.name} | {interaction.user.id} web-request",
            reason=f"Requested by {interaction.user.name} web-request",
        )
        query = database.MGMTickets.create(
            ChannelID=ticket_channel.id,
            authorID=interaction.user.id,
            createdAt=datetime.now(),
        )
        query.save()

        await ticket_channel.set_permissions(
            discord.utils.get(mgm_server.roles, name="Website Team"),
            read_messages=True,
            send_messages=True,
            manage_messages=True,
        )
        await ticket_channel.set_permissions(
            member,
            read_messages=True,
            send_messages=True,
        )
        control_embed = discord.Embed(
            title="Control Panel",
            description="To end this ticket, click the lock button!",
            color=discord.Colour.gold(),
        )
        LCB = discord.ui.View()
        LCB.add_item(
            ButtonHandler(
                style=discord.ButtonStyle.green,
                url=None,
                disabled=False,
                label="Lock",
                emoji="🔒",
                custom_id="mgm_ch_lock_menu",
            )
        )
        LCM = await ticket_channel.send(
            interaction.user.mention, embed=control_embed, view=LCB
        )
        await LCM.pin()
        embed_information = discord.Embed(
            title="Web Development Request",
            description=f"User: {member.mention}\n"
            f"Priority: {self.priority.value}\n"
            f"Request Type: {self.request_type.value}\n"
            f"Deadline: {self.deadline.value}\n"
            f"Title: {self.title_commission.value}\n"
            f"Information: {self.information.value}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)

        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created aWeb Development request for you.\n
                    You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )


class CommissionWebButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Start Web Commission",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:web_pjt",
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

        modal = WebRequestModal(self.bot)
        return await interaction.response.send_modal(modal)


class WebCommissionCode(commands.Cog):
    """
    Commands for bot commissions
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.__cog_name__ = "Web Commissions"

    @property
    def display_emoji(self) -> str:
        return Emoji.pythonLogo

    @app_commands.command(name="webcommission", description="Start a web commission")
    @app_commands.guilds(TechID.g_tech, StaffID.g_staff_resources)
    async def webcommission(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            button = CommissionWebButton(self.bot)
            await interaction.response.send_message(view=button)
        else:
            await interaction.response.send_message(
                "You're not allowed to do that.", ephemeral=True
            )

    @app_commands.command(
        name="webcommission-list", description="List all web commissions"
    )
    @app_commands.guilds(TechID.g_tech, StaffID.g_staff_resources)
    async def webcommission_list(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            query = database.MGMTickets.select()
            tickets = []
            for ticket in query:
                tickets.append(ticket)
            embed = discord.Embed(
                title="Bot Commission List",
                description="All bot commissions",
                color=discord.Colour.gold(),
            )
            for ticket in tickets:
                embed.add_field(
                    name=f"{ticket.authorID}",
                    value=f"{ticket.ChannelID}",
                    inline=False,
                )
            await interaction.response.send_message(embed=embed)

        else:
            await interaction.response.send_message(
                "You're not allowed to do that.", ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(WebCommissionCode(bot))
