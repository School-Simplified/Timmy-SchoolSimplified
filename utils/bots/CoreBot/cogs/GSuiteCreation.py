from __future__ import print_function

import random
import string
from typing import Literal

import discord
from discord import app_commands, ui
from discord.ext import commands
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from core.common import HRID, access_secret, Emoji


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


async def setup(bot):
    await bot.add_cog(AdminAPI(bot))
