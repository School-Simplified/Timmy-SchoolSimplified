from typing import Literal

import discord
from discord import ui, app_commands
from discord.ext import commands, tasks

from utils.bots.CoreBot.cogs.GSuiteCreation import get_random_string
from core import database
from core.checks import is_botAdmin
from core.common import TechID, Emoji, StaffID, SelectMenuHandler, HRID

"""
embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="Email Purpose", value=self.email_purpose.value)
        embed.add_field(name="Desired Email", value=self.requested_address.value)
        embed.add_field(name="Email Type", value=self.email_type.value)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        embed.add_field(name="Account Type", value=account_type[self.email_type.value], inline=False)
"""

class HREmailConfirm(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.value = None
        self.bot = bot

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        temppass = get_random_string()
        if embed.fields[4].value == "G":
            return await interaction.response.send("Error, not supported yet.", ephemeral=True)
        elif embed.fields[4].value == "T":
            """
            embed.add_field(name="Email Purpose", value=self.email_purpose.value)
            embed.add_field(name="Desired Email", value=self.requested_address.value)
            embed.add_field(name="Email Type", value=self.email_type.value)
            embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
            embed.add_field(name="Account Type", value=account_type[self.email_type.value], inline=False)
            """
            user = {
                "name": {
                    "givenName": embed.fields[3].value,
                    "fullName": embed.fields[3].value + " Team",
                    "familyName": "Team",
                },
                "password": temppass,
                "primaryEmail": f"{embed.fields[0].value}.{embed.fields[1].value}@schoolsimplified.org",
                "changePasswordAtNextLogin": True,
                "orgUnitPath": "/School Simplified Team Acc.",
                "organizations": [
                    {
                        "title": "Team Email",
                        "primary": True,
                        "department": embed.fields[3].value,
                        "description": "Team",
                    }
                ]
            }
        elif embed.fields[5].value == "Personal":
            """
            embed.add_field(name="First Name", value=self.first_name.value)
            embed.add_field(name="Last Name", value=self.last_name.value)
            embed.add_field(name="Managers Email", value=self.managers_email.value, inline=False)
            embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
            embed.add_field(name="Team Role", value=self.team_role.value)
            embed.add_field(name="Account Type", value="Personal", inline=False)
            """
            user = {
                "name": {
                    "givenName": embed.fields[0].value,
                    "fullName": embed.fields[0].value + " " + embed.fields[1].value,
                    "familyName": embed.fields[1].value,
                },
                "password": temppass,
                "primaryEmail": f"{embed.fields[0].value}.{embed.fields[1].value}@schoolsimplified.org",
                "changePasswordAtNextLogin": True,
                "orgUnitPath": "/School Simplified Personal Acc.",
                "relations": [
                    {
                        "value": embed.fields[2].value,
                        "type": "manager"
                    }
                ],
                "organizations": [
                    {
                        "title": embed.fields[4].value,
                        "primary": True,
                        "type": "work",
                        "department": embed.fields[3].value,
                    }
                ]

            }
        else:
            return
        service.users().insert(body=user).execute()
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        embed = interaction.message.embeds[0]
        embed.title = f'[RESOLVED] {embed.title}'
        embed.colour = discord.Color.brand_red()
        """Mark the buttons as disabled"""
        for button in interaction.message.components:
            button.disabled = False

        await interaction.message.edit(embed=embed)
        self.value = False
        self.stop()


class IEmailForm(ui.Modal, title="Auto Email Form"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    first_name = ui.TextInput(
        label="First Name",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    last_name = ui.TextInput(
        label="Last Name",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    team_name = ui.TextInput(
        label="Team/Dept. Name",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    team_role = ui.TextInput(
        label="What is your position in that team?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    managers_email = ui.TextInput(
        label="Managers Email",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        hr_email: discord.TextChannel = self.bot.get_channel(HRID.ch_email_requests)
        embed = discord.Embed(
            title=f"Email Request from {interaction.user.name}#{interaction.user.discriminator}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="First Name", value=self.first_name.value)
        embed.add_field(name="Last Name", value=self.last_name.value)
        embed.add_field(name="Managers Email", value=self.managers_email.value, inline=False)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        embed.add_field(name="Team Role", value=self.team_role.value)
        embed.add_field(name="Account Type", value="Personal", inline=False)
        await hr_email.send(embed=embed, view=None)


class TEmailForm(ui.Modal, title="Email Address Requests"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    email_purpose = ui.TextInput(
        label="Purpose of Email",
        style=discord.TextStyle.short,
        placeholder="What is this email going to be used for?",
        max_length=1024,
    )

    requested_address = ui.TextInput(
        label="Desired Email",
        style=discord.TextStyle.short,
        placeholder="Include @schoolsimplified.org",
        max_length=1024,
    )

    email_type = ui.TextInput(
        label="Email Type",
        style=discord.TextStyle.short,
        placeholder="G for Group Email, T for Team Email",
        max_length=1,
    )

    team_name = ui.TextInput(
        label="Team Name",
        style=discord.TextStyle.short,
        placeholder="What Team is this email for?",
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        hr_email: discord.TextChannel = self.bot.get_channel(HRID.ch_email_requests)
        embed = discord.Embed(
            title=f"Email Request from {interaction.user.name}#{interaction.user.discriminator}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        account_type = {"G": "Group", "T": "Team"}
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="Email Purpose", value=self.email_purpose.value)
        embed.add_field(name="Desired Email", value=self.requested_address.value)
        embed.add_field(name="Email Type", value=self.email_type.value)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        embed.add_field(name="Account Type", value=account_type[self.email_type.value], inline=False)

        await hr_email.send(embed=embed, view=None)


class StaffApps(ui.Modal, title="Staff Applications"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    team_name = ui.TextInput(
        label="Team Name",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    target_app = ui.TextInput(
        label="Application that needs updating",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    approval = ui.TextInput(
        label="Who approved this?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        pass


class StaffAnnouncements(ui.Modal, title="Staff Announcements"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    app_title = ui.TextInput(
        label="Announcement Title",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    team_name = ui.TextInput(
        label="Team Name",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    approval = ui.TextInput(
        label="Who approved this?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        pass


class CommissionButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Start Commission",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:start_commission_mgm",
        emoji="📝",
    )
    async def start_commission(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button,
    ):
        # TODO: Comply with Code Guidelines and use ConfigCat for IDs
        channel_to_modal_map = {
            956619405511524382: EmailAddReq,
            956619079853179031: StaffApps,
            956619132525244516: StaffAnnouncements,
            0: AutoEmailForm,
        }
        modal = channel_to_modal_map[interaction.channel.id](self.bot)
        return await interaction.response.send_modal(modal)


class MGMTickets(commands.Cog):
    """
    Commands for bot commissions
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.__cog_name__ = "MGM Commissions"
        #self.autoUnarchiveThread.start()

    @property
    def display_emoji(self) -> str:
        return Emoji.pythonLogo

    """async def cog_unload(self):
        self.autoUnarchiveThread.cancel()"""

    @app_commands.command()
    @is_botAdmin
    async def send_mgm_embed(self, ctx, param: Literal["1", "2", "3"]):
        pass

    """@app_commands.command()
    @app_commands.guilds(TechID.g_tech)
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.guild_id, i.channel.id))
    async def commission(
            self, interaction: discord.Interaction, action: Literal["close"]
    ):
        channel: discord.TextChannel = self.bot.get_channel(TechID.ch_bot_requests)
        thread = interaction.channel

        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message(
                "This is not a bot commission.", ephemeral=True
            )
            return

        if action == "close":
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

    @tasks.loop(seconds=60.0)
    async def autoUnarchiveThread(self):

        channel: discord.TextChannel = self.bot.get_channel(TechID.ch_bot_requests)
        query = database.TechCommissionArchiveLog.select()
        closed_threads = [entry.ThreadID for entry in query]

        async for archived_thread in channel.archived_threads():
            if archived_thread.id not in closed_threads:
                await archived_thread.edit(archived=False)

    @autoUnarchiveThread.before_loop
    async def before_loop_(self):
        await self.bot.wait_until_ready()"""


async def setup(bot: commands.Bot):
    await bot.add_cog(MGMTickets(bot))
