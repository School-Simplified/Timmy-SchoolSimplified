from __future__ import print_function

import random
import string
from datetime import datetime
from typing import Literal

import discord
from discord import app_commands

# from discord.app_commands import locale_str as _
from discord.ext import commands
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import core.common
from core import database
from core.checks import slash_is_bot_admin_4
from core.common import HRID, access_secret, Emoji, ButtonHandler, StaffID
from core.logging_module import get_log

_log = get_log(__name__)


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

    GS = app_commands.Group(
        name="gsuite",
        description="G-Suite Commands",
        guild_ids=[HRID.g_hr],
    )

    HRCS = app_commands.Group(
        name="hr-request",
        description="Request something from HR!",
        guild_ids=[
            954104500388511784,
            932066545117585428,
            950799439625355294,
            953433561178968104,
            950813235588780122,
            952294235028201572,
            952287046750310440,
            950799370855518268,
            950799485901107270,
            951595352090374185,
            950795656853876806,
            955911166520082452,
            824421093015945216,
            815753072742891532,
            891521033700540457,
            1006787368839286866,
            1007766456584372325,
        ],
    )

    @GS.command(
        name="create",
        description="Create a GSuite Account",
    )
    @app_commands.describe(
        organizationunit="Select the organization unit this user will be in."
    )
    @app_commands.checks.has_role(HRID.r_hr_staff)
    async def create_gsuite(
        self,
        interaction: discord.Interaction,
        firstname: str,
        lastname: str,
        organizationunit: Literal["Personal Account", "Team Account"],
    ):
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

    @GS.command(
        name="delete",
        description="Suspend/Delete a GSuite Account",
    )
    @app_commands.checks.has_role(HRID.r_hr_staff)
    async def delete_gsuite(self, interaction: discord.Interaction, email: str):
        try:
            service.users().delete(userKey=email).execute()
        except:
            return await interaction.response.send_message(
                f"{interaction.user.mention} The account **{email}** does not exist."
            )
        else:
            await interaction.response.send_message("Successfully deleted the account.")

    @GS.command(
        name="suspend",
        description="Suspend a GSuite Account",
    )
    @app_commands.describe(
        suspend="Select whether to suspend or restore the account. This field is required."
    )
    @app_commands.checks.has_role(HRID.r_hr_staff)
    async def suspend_gsuite(
        self, interaction: discord.Interaction, email: str, suspend: bool
    ):
        if suspend is None:
            return await interaction.response.send_message(
                f"{interaction.user.mention} Please specify whether you want to suspend or restore the account."
            )

        try:
            user = service.users().get(userKey=email).execute()
            user["suspended"] = suspend
            service.users().update(userKey=email, body=user).execute()
        except:
            await interaction.response.send_message(
                f"{interaction.user.mention} The account **{email}** does not exist."
            )
        else:
            if suspend:
                await interaction.response.send_message(
                    "Successfully suspended the account."
                )
            else:
                await interaction.response.send_message(
                    "Successfully restored the account."
                )

    @HRCS.command(
        name="promote",
        description="Create a promotion request to HR.",
    )
    @app_commands.describe(
        user="Select the user you want to promote.",
        reason="Enter the reason for the promotion.",
        team="Select the team the user is in.",
        additional_info="Enter any additional information you want to include.",
    )
    async def promote(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        reason: str,
        team: str,
        additional_info: str,
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
        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_promote_tickets
        )
        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} You must be in the server to create a resignation request.\nIf you "
                    f"are not a manager+, please DM someone from HR! "
                )

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
                custom_id="mgm_ch_lock_menu",
            )
        )
        LCM = await ticket_channel.send(
            interaction.user.mention, embed=control_embed, view=LCB
        )
        await LCM.pin()
        embed_information = discord.Embed(
            title="Promotion Request",
            description=f"User: {user.mention}\n"
            f"**Reason:** {reason}"
            f"**Team:** {team}"
            f"\n**Additional "
            f"Information:** {additional_info}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)

        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a promotion request for **{user.name}**.\n
                    **Reason:** {reason}\n,
                    You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )

    @HRCS.command(
        name="fire",
        description="Create a firing request to HR.",
    )
    @app_commands.describe(
        user="Select the user you want to fire.",
        reason="Enter the reason for the firing.",
        additional_info="Enter any additional information you want to include.",
        evidence_text="Enter any *textual* evidence* for the firing.",
        evidence_url="Upload any attachment relating to the firing.",
    )
    async def fire(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        reason: str,
        team: str,
        additional_info: str,
        evidence_text: str = None,
        evidence_url: discord.Attachment = None,
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
        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_fire_tickets
        )
        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} You must be in the server to create a resignation request.\nIf you "
                    f"are not a manager+, please DM someone from HR! "
                )

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
                custom_id="mgm_ch_lock_menu",
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
            f"**Team:** {team}\n"
            f"**Additional Information:** {additional_info}\n"
            f"**Evidence:** {evidence_text}\n"
            f"**Evidence URL:** {evidence_url}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)
        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a firing request for **{user.name}**.\n
            **Reason:** {reason}\n,
            You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )

    @HRCS.command(
        name="censure",
        description="Create a censure request to HR.",
    )
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
        evidence_url: discord.Attachment = None,
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
        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_censure_tickets
        )
        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} You must be in the server to create a resignation request.\nIf you "
                    f"are not a manager+, please DM someone from HR! "
                )

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
                custom_id="mgm_ch_lock_menu",
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
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)
        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a censure request for **{user.name}**.\n
            **Reason:** {reason}\n
            You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )

    @HRCS.command(
        name="strike",
        description="Create a strike request to HR.",
    )
    @app_commands.describe(
        user="Select the user you want to strike.",
        reason="Enter the reason for the strike.",
        department="Select the department this user is in.",
        evidence_text="Enter any *textual* evidence* for the strike.",
        evidence_url="Upload any attachment relating to the strike.",
    )
    async def censure(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        reason: str,
        department: str,
        evidence_text: str = None,
        evidence_url: discord.Attachment = None,
    ):
        mgm_server = self.bot.get_guild(core.common.StaffID.g_staff_mgm)
        manager_role = discord.utils.get(mgm_server.roles, name="Manager")

        try:
            user_in_mgm = await mgm_server.fetch_member(interaction.user.id)
        except discord.errors.NotFound:
            return await interaction.response.send_message(
                f"{interaction.user.mention} I can't seem to verify you are a manager, please contact HR for assistance."
            )

        if user.bot:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You cannot strike a bot."
            )

        if user == interaction.user:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You cannot strike yourself."
            )

        if not reason:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a reason for the strike."
            )

        if user_in_mgm.top_role.position < manager_role.position:
            return await interaction.response.send_message(
                f"{interaction.user.mention} This command is only for managers+, contact HR for more information."
            )

        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_censure_tickets
        )
        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} You must be in the server to create a resignation request.\nIf you "
                    f"are not a manager+, please DM someone from HR! "
                )

        ticket_channel = await ticket_category.create_text_channel(
            f"{user.name}-strike",
            topic=f"{user.name} | {user.id} strike",
            reason=f"Requested by {interaction.user.name} strike",
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
                custom_id="mgm_ch_lock_menu",
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
            title="Strike Request",
            description=f"User: {user.mention}\n"
            f"**Reason:** {reason}\n"
            f"**Department:** {department}\n"
            f"**Evidence:** {evidence_text}\n"
            f"**Evidence URL:** {evidence_url}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)
        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a strike request for **{user.name}**.\n
                **Reason:** {reason}\n
                You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )

    @HRCS.command(
        name="break",
        description="Create a break request to HR.",
    )
    @app_commands.describe(
        team="Identify the teams you are in/want to take a break from.",
        start_date="Enter the start date of the break.",
        end_date="Enter the end date of the break.",
        reason="Enter the reason for the break.",
    )
    async def break_request(
        self,
        interaction: discord.Interaction,
        team: str,
        start_date: str,
        end_date: str,
        reason: str = "No reason provided.",
    ):
        if not team:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a team."
            )
        if not start_date:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a start date."
            )
        if not end_date:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter an end date."
            )
        mgm_server = self.bot.get_guild(core.common.StaffID.g_staff_resources)
        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_break_tickets
        )
        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} You must be in the server to create a resignation request.\nIf you "
                    f"are not a manager+, please DM someone from HR! "
                )

        ticket_channel = await ticket_category.create_text_channel(
            f"{interaction.user.name}-break",
            topic=f"{interaction.user.name} | {interaction.user.id} break",
            reason=f"Requested by {interaction.user.name} break",
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
            title="Break Request",
            description=f"User: {member.mention}\n"
            f"**Reason:** {reason}\n"
            f"**Team:** {team}\n"
            f"**Start Date:** {start_date}\n"
            f"**End Date:** {end_date}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)

        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a break request for you.\n
            **Reason:** {reason}\n
            You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )

    @HRCS.command(
        name="resignations",
        description="Create a resignation request to HR.",
    )
    @app_commands.describe(
        team="Identify the team(s) want to resign from.",
        expected_date="Enter the expected date of your resignation.",
        reason="Enter the reason for your resignation.",
    )
    async def resignation_request(
        self,
        interaction: discord.Interaction,
        team: str,
        expected_date: str,
        reason: str = "No reason provided.",
    ):
        if not team:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a team."
            )
        if not expected_date:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a expected date."
            )
        mgm_server = self.bot.get_guild(core.common.StaffID.g_staff_resources)
        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_resignation_tickets
        )
        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} You must be in the server to create a resignation request.\nIf you "
                    f"are not a manager+, please DM someone from HR! "
                )

        ticket_channel = await ticket_category.create_text_channel(
            f"{interaction.user.name}-resignation",
            topic=f"{interaction.user.name} | {interaction.user.id} resignation",
            reason=f"Requested by {interaction.user.name} resignation",
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
            title="Resignation Request",
            description=f"User: {member.mention}\n"
            f"**Team:** {team}\n"
            f"**Expected Date:** {expected_date}\n"
            f"**Reason:** {reason}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)

        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a resignation request for you.\n
            **Team:** {team}\n
            **Expected Date:** {expected_date}\n
            **Reason:** {reason}\n,
            You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )

    @HRCS.command(
        name="suggestions",
        description="Create a suggestion request to HR.",
    )
    @app_commands.describe(
        suggestion="Enter the suggestion you want to make.",
        related_team="Enter the team(s) this suggestion is related to.",
    )
    async def suggestion_request(
        self,
        interaction: discord.Interaction,
        suggestion: str,
        related_team: str = "No team provided.",
    ):
        if not suggestion:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a suggestion."
            )
        mgm_server = self.bot.get_guild(core.common.StaffID.g_staff_resources)
        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_suggestions_tickets
        )
        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} You must be in the server to create a resignation request.\nIf you "
                    f"are not a manager+, please DM someone from HR! "
                )

        ticket_channel = await ticket_category.create_text_channel(
            f"{interaction.user.name}-suggestion",
            topic=f"{interaction.user.name} | {interaction.user.id} suggestion",
            reason=f"Requested by {interaction.user.name} suggestion",
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
            title="Suggestion Request",
            description=f"User: {member.mention}\n"
            f"**Related Team:** {related_team}\n"
            f"**Suggestion:** {suggestion}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)

        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a suggestion request for you.\n
            **Related Team:** {related_team}\n
            **Suggestion:** {suggestion}\n,
            You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )

    @HRCS.command(
        name="complaint",
        description="Create a complaint request to HR.",
    )
    @app_commands.describe(
        user="Who is the user you wish to submit a complaint about?",
        complaint="Enter the complaint you want to make.",
        evidence="Enter the evidence you have for the complaint.",
        evidence_url="Upload attachments here.",
    )
    async def complaint_request(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        complaint: str,
        evidence: str = "None provided",
        evidence_url: discord.Attachment = None,
    ):
        if not complaint:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a complaint."
            )
        mgm_server = self.bot.get_guild(core.common.StaffID.g_staff_resources)
        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_complaint_tickets
        )
        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} You must be in the server to create a resignation request.\nIf you "
                    f"are not a manager+, please DM someone from HR! "
                )

        ticket_channel = await ticket_category.create_text_channel(
            f"{interaction.user.name}-complaint",
            topic=f"{interaction.user.name} | {interaction.user.id} complaint",
            reason=f"Requested by {interaction.user.name} complaint",
        )
        query = database.MGMTickets.create(
            ChannelID=ticket_channel.id,
            authorID=interaction.user.id,
            createdAt=datetime.now(),
        )
        query.save()

        if evidence_url is None:
            evidence_url = "No evidence provided."
        else:
            evidence_url = evidence_url.url

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
            title="Complaint Request",
            description=f"User: {user.mention}\n"
            f"**Complaint:** {complaint}\n"
            f"**Evidence:** {evidence}\n"
            f"**Evidence URL:** {evidence_url}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)

        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a complaint request for you.\n
            **Complaint:** {complaint}\n
            **User:** {user.mention}\n
            **Evidence:** {evidence}\n
            **Evidence URL:** {evidence_url}\n,
            You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )

    @HRCS.command(
        name="cs-hours",
        description="Request CS hours.",
    )
    @app_commands.describe(
        team="Enter the team(s) you want to request CS hours for.",
        hours="Enter the number of hours you want to request.",
        form_link="Paste your form link here.",
    )
    async def cs_hours(
        self, interaction: discord.Interaction, team: str, hours: int, form_link: str
    ):
        if not team:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a team."
            )
        if not hours:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter the number of hours you want to request."
            )
        if not form_link:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You must enter a form link."
            )

        mgm_server = self.bot.get_guild(core.common.StaffID.g_staff_resources)
        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_cs_hours_tickets
        )
        member = interaction.guild.get_member(interaction.user.id)

        if member is None:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} You must be in the server to create a resignation request.\nIf you "
                    f"are not a manager+, please DM someone from HR! "
                )

        ticket_channel = await ticket_category.create_text_channel(
            f"{interaction.user.name}-cs-hours",
            topic=f"{interaction.user.name} | {interaction.user.id} cs-hours",
            reason=f"Requested by {interaction.user.name} cs-hours",
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
            title="CS Hours Request",
            description=f"User: {member.mention}\n"
            f"**Team:** {team}\n"
            f"**Hours:** {hours}\n"
            f"**Form Link:** {form_link}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)

        await interaction.response.send_message(
            content=f"""{interaction.user.mention} Successfully created a CS hours request for you.\n
            **Team:** {team}\n
            **Hours:** {hours}\n
            **Form Link:** {form_link}\n,
            You can view the ticket here: {ticket_channel.mention}""",
            ephemeral=True,
        )

    @app_commands.command(
        name="furry-raid",
        description="Request a furry raid. | Anti-furry officers will be dispatched to raid every kitten nickname.",
    )
    @slash_is_bot_admin_4()
    @app_commands.guilds(discord.Object(HRID.g_hr))
    @app_commands.describe(
        user="Target a specific user to raid, if left blank it raids everyone.",
        force="Force a nickname change regardless, maybe they disguised furry??? | Only works on targeted users.",
    )
    async def furry_raid(
        self,
        interaction: discord.Interaction,
        user: discord.User = None,
        force: bool = False,
    ):
        # TODO: Make sure to check if the username translates to furry in a different language

        stupid = ["furry", "kitten", "meow", "daddy", "fruity", "gato"]
        user_count = 0
        await interaction.response.defer()

        if not user:
            for member in interaction.guild.members:
                for element in stupid:
                    if (
                        element in member.display_name
                        and not member.bot
                        and member.id != 409152798609899530
                    ):
                        user_count += 1
                        try:
                            await member.edit(nick="name seized by anti-furry police")
                        except Exception as e:
                            _log.error("FurryRaid: Unable to edit user: {}".format(e))

            await interaction.followup.send(
                f"{interaction.user.mention} Successfully raided {user_count} users."
            )
        else:
            if user.id == 409152798609899530 or user.bot:
                return await interaction.followup.send(
                    f"{interaction.user.mention} You can't raid the police/already raided users!"
                )

            seized = False
            user = interaction.guild.get_member(user.id)

            if not force:
                for element in stupid:
                    if element in user.display_name and not user.bot:
                        try:
                            await user.edit(nick="name seized by anti-furry police")
                        except Exception as e:
                            await interaction.followup.send(
                                f"{interaction.user.mention}: <@409152798609899530> I need some backup! This furry is too dangerous for me to handle!"
                            )
                        else:
                            seized = True
                if not seized:
                    await interaction.followup.send(
                        f"{interaction.user.mention} {user.mention} cleared inspection."
                    )
                else:
                    await interaction.followup.send(
                        f"{interaction.user.mention}: {user.mention} has been raided by the anti-furry police."
                    )
            else:
                try:
                    await user.edit(nick="name seized by anti-furry police")
                except Exception as e:
                    await interaction.followup.send(
                        f"{interaction.user.mention}: <@409152798609899530> I need some backup! This furry is too dangerous for me to handle!"
                    )
                else:
                    await interaction.followup.send(
                        f"{interaction.user.mention}: {user.mention} has been raided by the anti-furry police."
                    )


async def setup(bot):
    await bot.add_cog(AdminAPI(bot))
