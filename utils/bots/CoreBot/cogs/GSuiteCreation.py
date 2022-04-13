from __future__ import print_function

import random
import string
from typing import Literal

import discord
from discord.ext import commands
from discord import app_commands

from googleapiclient.discovery import build

from core.common import HR_ID, access_secret, Emoji


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
        return Emoji.humanresources

    @app_commands.command(
        name="gsuite-create",
        description="Create a GSuite Account",
    )
    @app_commands.guilds(HR_ID.g_hr)
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
        HR_Role = discord.utils.get(interaction.user.guild.roles, id=HR_ID.r_hrStaff)
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
        service.users().insert(body=user).execute()
        await interaction.response.send_message(
            f"{interaction.user.mention} Successfully created **{firstname} {lastname}'s** account.\n"
            f"**Username:** {firstname}.{lastname}@schoolsimplified.org\n"
            f"**Organization Unit:** {orgUnit[organizationunit]}",
            ephemeral=False,
        )
        await interaction.response.send_message(
            f"**Temporary Password:**\n||{temppass}||\n\n**Instructions:**\nGive the Username and the Temporary "
            f"Password to the user and let them know they have **1 week** to setup 2FA before they get locked out. ",
            ephemeral=True,
        )

    @app_commands.command(
        name="gsuite-delete",
        description="Suspend/Delete a GSuite Account",
    )
    @app_commands.guilds(HR_ID.g_hr)
    async def delete_gsuite(self, interaction: discord.Interaction, email: str):
        HR_Role = discord.utils.get(interaction.guild.roles, id=HR_ID.r_hrStaff)
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
    @app_commands.guilds(HR_ID.g_hr)
    @app_commands.describe(
        suspend="Select whether to suspend or restore the account. This field is required."
    )
    async def suspend_gsuite(self, interaction: discord.Interaction, email: str, suspend: bool):
        HR_Role = discord.utils.get(interaction.guild.roles, id=HR_ID.r_hrStaff)
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
            await interaction.response.send_message("Successfully suspended the account.")


async def setup(bot):
    await bot.add_cog(AdminAPI(bot))
