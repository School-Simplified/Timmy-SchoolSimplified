from __future__ import print_function

import random
import string
from typing import Literal

import discord
from discord import app_commands, ui
from discord.ext import commands
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import core.common
from core import database
from core.common import HRID, access_secret, Emoji, ButtonHandler


def get_random_string(length=13):
    # choose from all lowercase letter
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"

    rnd = random.SystemRandom()
    return "".join(rnd.choice(chars) for i in range(length))


# ADMIN API NOW
SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.orgunit",
    "https://www.googleapis.com/auth/admin.directory.userschema",
]
orgUnit = {
    "Personal Account": "/School Simplified Personal Acc.",
    "Team Account": "/School Simplified Team Acc.",
}


creds = access_secret("adm_t", True, 0, SCOPES)
service = build("admin", "directory_v1", credentials=creds)


class GSuiteForm(ui.Modal, title="GSuite Account/Email Request"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    firstName = ui.TextInput(
        label="What is your first name?",
        style=discord.TextStyle.short,
        max_length=100,
    )

    lastName = ui.TextInput(
        label="What is your last name?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    descriptionTI = ui.TextInput(
        label="Personal Email Address",
        style=discord.TextStyle.short,
        placeholder="This is not required but if given, you will get a copy of sign in details in your email.",
        max_length=1024,
        required=False,
    )

    dept = ui.TextInput(
        label="Primary Department",
        style=discord.TextStyle.short,
        placeholder="What is the current department you are in?",
        max_length=1024,
    )

    anythingElseTI = ui.TextInput(
        label="Anything else?",
        style=discord.TextStyle.long,
        required=False,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        respChannel = self.bot.get_channel(968345000100384788)
        await respChannel.send("")


class GSuiteButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Get GSuite Account",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:gsuite_form",
        emoji="📝",
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.followup.send_modal(GSuiteForm(self.bot))


class AdminAPI(commands.Cog):
    """
    HR Commands
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.__cog_name__ = "Human Resources"

    @property
    def display_emoji(self) -> str:
        return Emoji.human_resources

    @app_commands.command(
        name="gsuite-create",
        description="Create a GSuite Account",
    )
    @app_commands.guilds(HRID.g_hr)
    @app_commands.describe(
        organizationunit="Select the organization unit this user will be in."
    )
    async def create_gsuite(
        self,
        interaction: discord.Interaction,
        firstname: str,
        lastname: str,
        organizationunit: Literal["Personal Account", "Team Account"],
    ):
        HR_Role = discord.utils.get(interaction.user.guild.roles, id=HRID.r_hr_staff)
        if HR_Role not in interaction.user.roles:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You do not have the required permissions to use this command."
            )

        temppass = get_random_string()
        user = {
            "name": {
                "givenName": firstname,
                "fullName": firstname + " " + lastname,
                "familyName": lastname,
            },
            "password": temppass,
            "primaryEmail": f"{firstname}.{lastname}@schoolsimplified.org",
            "changePasswordAtNextLogin": True,
            "orgUnitPath": orgUnit[organizationunit],
        }
        try:
            service.users().insert(body=user).execute()
        except HttpError as e:
            """If the error code is 409, send a message to the user saying that the email is already taken."""
            if e.status_code == 409:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} The email {user['primaryEmail']} is already taken."
                )
            else:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} An error occurred. Please try again later.\nError: {e}"
                )

        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} Successfully created **{firstname} {lastname}'s** account.\n"
                f"**Username:** {firstname}.{lastname}@schoolsimplified.org\n"
                f"**Organization Unit:** {orgUnit[organizationunit]}",
                ephemeral=False,
            )
            await interaction.followup.send(
                f"**Temporary Password:**\n||{temppass}||\n\n**Instructions:**\nGive the Username and the Temporary "
                f"Password to the user and let them know they have **1 week** to setup 2FA before they get locked out. ",
                ephemeral=True,
            )

    @app_commands.command(
        name="gsuite-delete",
        description="Suspend/Delete a GSuite Account",
    )
    @app_commands.guilds(HRID.g_hr)
    async def delete_gsuite(self, interaction: discord.Interaction, email: str):
        HR_Role = discord.utils.get(interaction.guild.roles, id=HRID.r_hr_staff)
        if HR_Role not in interaction.user.roles:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You do not have the required permissions to use this command."
            )

        try:
            service.users().delete(userKey=email).execute()
        except:
            return await interaction.response.send_message(
                f"{interaction.user.mention} The account **{email}** does not exist."
            )
        else:
            await interaction.response.send_message("Successfully deleted the account.")

    @app_commands.command(
        name="gsuite-suspend",
        description="Suspend a GSuite Account",
    )
    @app_commands.guilds(HRID.g_hr)
    @app_commands.describe(
        suspend="Select whether to suspend or restore the account. This field is required."
    )
    async def suspend_gsuite(self, interaction: discord.Interaction, email: str, suspend: bool):
        HR_Role = discord.utils.get(interaction.guild.roles, id=HRID.r_hr_staff)
        if HR_Role not in interaction.user.roles:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You do not have the required permissions to use this command."
            )

        if suspend is None:
            return await interaction.response.send_message(
                f"{interaction.user.mention} Please specify whether you want to suspend or restore the account."
            )

        try:
            user = service.users().get(userKey=email).execute()
            user['suspended'] = suspend
            service.users().update(userKey=email, body=user).execute()
        except:
            await interaction.response.send_message(
                f"{interaction.user.mention} The account **{email}** does not exist."
            )
        else:
            if suspend:
                await interaction.response.send_message("Successfully suspended the account.")
            else:
                await interaction.response.send_message("Successfully restored the account.")



    @app_commands.command(
        name="promote",
        description="Create a promotion request to HR.",
    )
    @app_commands.guilds(discord.Object(815753072742891532))
    @app_commands.describe(
        user="Select the user you want to promote.",
        reason="Enter the reason for the promotion.",
    )
    async def promote(
            self,
            interaction: discord.Interaction,
            user: discord.User,
            reason: str
    ):
        if user.bot:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You cannot promote a bot."
            )

        if user == interaction.user:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You cannot promote yourself."
            )

        if not reason:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a reason for the promotion."
            )

        mgm_server = self.bot.get_guild(core.common.StaffID.g_staff_mgm)
        ticket_category = discord.utils.get(mgm_server.categories, id=956297567346495568)
        member = interaction.guild.get_member(interaction.user.id)

        ticket_channel = await ticket_category.create_text_channel(
            f"{user.name}-promotion",
            topic=f"{user.name} | {user.id} promotion",
            reason=f"Requested by {interaction.user.name} promotion",
        )
        query = database.MGMTickets.create(
            ChannelID=ticket_channel.id,
            authorID=interaction.user.id,
            createdAt=datetime.now(),
        )
        query.save()

        await ticket_channel.set_permissions(
            discord.utils.get(mgm_server.roles, name="Human Resources"),
            read_messages=True,
            send_messages=True,
            manage_messages=True,
        )
        await ticket_channel.set_permissions(
            member,
            read_messages=True,
            send_messages=True,
            manage_messages=True,
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
                custom_id="mgm_ch_lock",
            )
        )
        LCM = await ticket_channel.send(
            interaction.user.mention, embed=control_embed, view=LCB
        )
        await LCM.pin()
        embed_information = discord.Embed(
            title="Promotion Request",
            description=f"User: {user.mention}\n"
            f"**Reason:** {reason}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(
            text=f"ID: {interaction.user.id}"
        )
        await ticket_channel.send(embed=embed_information)

        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a promotion request for **{user.name}**.\n
                    **Reason:** {reason}\n,
                    You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )


    @app_commands.command(
        name="fire",
        description="Create a firing request to HR.",
    )
    @app_commands.guilds(discord.Object(815753072742891532))
    @app_commands.describe(
        user="Select the user you want to fire.",
        reason="Enter the reason for the firing.",
        evidence_text="Enter any *textual* evidence* for the firing.",
        evidence_url="Upload any attachment relating to the firing.",
    )
    async def fire(
            self,
            interaction: discord.Interaction,
            user: discord.User,
            reason: str,
            evidence_text: str = None,
            evidence_url: discord.Attachment = None
    ):
        if user.bot:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You cannot fire a bot."
            )

        if user == interaction.user:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You cannot fire yourself."
            )

        if not reason:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a reason for the firing."
            )

        mgm_server = self.bot.get_guild(core.common.StaffID.g_staff_mgm)
        ticket_category = discord.utils.get(mgm_server.categories, id=956297567346495568)
        member = interaction.guild.get_member(interaction.user.id)

        ticket_channel = await ticket_category.create_text_channel(
            f"{user.name}-firing",
            topic=f"{user.name} | {user.id} firing",
            reason=f"Requested by {interaction.user.name} firing",
        )
        query = database.MGMTickets.create(
            ChannelID=ticket_channel.id,
            authorID=interaction.user.id,
            createdAt=datetime.now(),
        )
        query.save()

        await ticket_channel.set_permissions(
            discord.utils.get(mgm_server.roles, name="Human Resources"),
            read_messages=True,
            send_messages=True,
            manage_messages=True,
        )
        await ticket_channel.set_permissions(
            member,
            read_messages=True,
            send_messages=True,
            manage_messages=True,
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
                custom_id="mgm_ch_lock",
            )
        )
        LCM = await ticket_channel.send(
            interaction.user.mention, embed=control_embed, view=LCB
        )
        await LCM.pin()
        if evidence_text is None:
            evidence_text = "No evidence provided."

        if evidence_url is None:
            evidence_url = "No evidence provided."
        else:
            evidence_url = evidence_url.url

        embed_information = discord.Embed(
            title="Firing Request",
            description=f"User: {user.mention}\n"
            f"**Reason:** {reason}\n"
            f"**Evidence:** {evidence_text}\n"
            f"**Evidence URL:** {evidence_url}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(
            text=f"ID: {interaction.user.id}"
        )
        await ticket_channel.send(embed=embed_information)
        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a firing request for **{user.name}**.\n
            **Reason:** {reason}\n,
            You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )


    @app_commands.command(
        name="censure",
        description="Create a censure request to HR.",
    )
    @app_commands.guilds(discord.Object(815753072742891532))
    @app_commands.describe(
        user="Select the user you want to censure.",
        reason="Enter the reason for the censure.",
        evidence_text="Enter any *textual* evidence* for the censure.",
        evidence_url="Upload any attachment relating to the censure.",
    )
    async def censure(
            self,
            interaction: discord.Interaction,
            user: discord.User,
            reason: str,
            evidence_text: str = None,
            evidence_url: discord.Attachment = None
    ):
        if user.bot:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You cannot censure a bot."
            )

        if user == interaction.user:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You cannot censure yourself."
            )

        if not reason:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a reason for the censure."
            )

        mgm_server = self.bot.get_guild(core.common.StaffID.g_staff_mgm)
        ticket_category = discord.utils.get(mgm_server.categories, id=956297567346495568)
        member = interaction.guild.get_member(interaction.user.id)

        ticket_channel = await ticket_category.create_text_channel(
            f"{user.name}-censure",
            topic=f"{user.name} | {user.id} censure",
            reason=f"Requested by {interaction.user.name} censure",
        )
        query = database.MGMTickets.create(
            ChannelID=ticket_channel.id,
            authorID=interaction.user.id,
            createdAt=datetime.now(),
        )
        query.save()

        await ticket_channel.set_permissions(
            discord.utils.get(mgm_server.roles, name="Human Resources"),
            read_messages=True,
            send_messages=True,
            manage_messages=True,
        )
        await ticket_channel.set_permissions(
            member,
            read_messages=True,
            send_messages=True,
            manage_messages=True,
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
                custom_id="mgm_ch_lock",
            )
        )
        LCM = await ticket_channel.send(
            interaction.user.mention, embed=control_embed, view=LCB
        )
        await LCM.pin()
        if evidence_text is None:
            evidence_text = "No evidence provided."

        if evidence_url is None:
            evidence_url = "No evidence provided."
        else:
            evidence_url = evidence_url.url
        embed_information = discord.Embed(
            title="Censure Request",
            description=f"User: {user.mention}\n"
            f"**Reason:** {reason}\n"
            f"**Evidence:** {evidence_text}\n"
            f"**Evidence URL:** {evidence_url}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(
            text=f"ID: {interaction.user.id}"
        )
        await ticket_channel.send(embed=embed_information)
        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a censure request for **{user.name}**.\n
            **Reason:** {reason}\n
            You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(AdminAPI(bot))
