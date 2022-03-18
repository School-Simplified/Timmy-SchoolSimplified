from __future__ import print_function

import json
import os
import os.path
import random
import string

import discord
import gspread
from core.checks import is_botAdmin
from discord.ext import commands
from google.auth.transport.requests import AuthorizedSession, Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from core.common import HR_ID, access_secret, bcolors


def get_random_string(length=13):
    # choose from all lowercase letter
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'

    rnd = random.SystemRandom()
    return (''.join(rnd.choice(chars) for i in range(length)))




# ADMIN API NOW
SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user', 
    'https://www.googleapis.com/auth/admin.directory.group', 
    'https://www.googleapis.com/auth/admin.directory.orgunit',
    'https://www.googleapis.com/auth/admin.directory.userschema',
    
]
orgUnit = {
    "Personal Account": "/School Simplified Personal Acc.",
    "Team Account": "/School Simplified Team Acc.",
}


creds = access_secret("adm_t", True, 0, SCOPES)
service = build('admin', 'directory_v1', credentials=creds)



class AdminAPI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(
        name="gsuite-create",
        description="Create a GSuite Account",
        guild_ids=[HR_ID.g_hr],
    )
    async def create_gsuite(self, ctx: commands.Context, firstname, lastname, organizationunit: discord.Option(str, "Choose an account type.", choices=["Personal Account", "Team Account"]),):
        HR_Role = discord.utils.get(ctx.guild.roles, id=HR_ID.r_hrStaff)
        if HR_Role not in ctx.author.roles:
            return await ctx.respond(
                f"{ctx.author.mention} You do not have the required permissions to use this command."
            )

        temppass = get_random_string()
        user = {
            "name": {
                "givenName": firstname,
                "fullName": firstname + " " + lastname,
                "familyName": lastname
            },
            "password": temppass,
            "primaryEmail": f"{firstname}.{lastname}@schoolsimplified.org",
            "changePasswordAtNextLogin": True,
            "orgUnitPath": orgUnit[organizationunit]
        }
        service.users().insert(body=user).execute()
        await ctx.respond(
            f"{ctx.author.mention} Successfully created **{firstname} {lastname}'s** account.\n"
            f"**Username:** {firstname}.{lastname}@schoolsimplified.orf\n"
            f"**Organization Unit:** {orgUnit[organizationunit]}",
            ephemeral=False
        )
        await ctx.respond(f"**Temporary Password:**\n||{temppass}||\n\n**Instructions:**\nGive the Username and the Temporary Password to the user and let them know they have **1 week** to setup 2FA before they get locked out. ", ephemeral=True)

    @discord.slash_command(
        name="gsuite-delete",
        description="Suspend/Delete a GSuite Account",
        guild_ids=[HR_ID.g_hr],
    )
    async def delete_gsuite(self, ctx: commands.Context, email):
        HR_Role = discord.utils.get(ctx.guild.roles, id=HR_ID.r_hrStaff)
        if HR_Role not in ctx.author.roles:
            return await ctx.respond(
                f"{ctx.author.mention} You do not have the required permissions to use this command."
            )
        
        try:
            service.users().delete(userKey=email).execute()
        except:
            return await ctx.respond(
                f"{ctx.author.mention} The account **{email}** does not exist."
            )
        else:
            await ctx.respond("Successfully deleted the account.")

def setup(bot):
    bot.add_cog(AdminAPI(bot))