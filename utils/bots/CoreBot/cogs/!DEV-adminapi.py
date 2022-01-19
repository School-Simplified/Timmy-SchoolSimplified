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
from core.common import bcolors

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

def get_random_string(length=8):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length)) 

gc = service_account.Credentials.from_service_account_file(filename='gsheetsadmin/credentialsA.json')
scopedCreds = gc.with_scopes(scope)
client = gspread.Client(auth=scopedCreds)
client.session = AuthorizedSession(scopedCreds)
sheet = client.open("School Simplified Staff Profile Form (Responses)").sheet1


# ADMIN API NOW
ASCOPES = ['https://www.googleapis.com/auth/admin.directory.user']
orgUnit = {
    "NONE": "/School Simplified",
    "School Simplified Digital": "/School Simplified, Core Organization/School Simplified Digital",
    "Projects": "/School Simplified, Core Organization/Projects",
    "Human Resources": "/School Simplified, Core Organization/Human Resources",
    "Marketing": "/School Simplified, Core Organization/Global Marketing",
    "Programming Simplified": "/School Simplified, Core Organization/Programming Simplified",
    "Student Activities": "/School Simplified, Core Organization/Student Activities Division",
}

if os.path.exists('gsheetsadmin/tokenA.json'):
    creds = Credentials.from_authorized_user_file('gsheetsadmin/tokenA.json', ASCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'gsheetsadmin/admincred.json', ASCOPES)
        creds = flow.run_local_server(port=8102)
    # Save the credentials for the next run
    with open('gsheetsadmin/tokenA.json', 'w') as token:
        token.write(creds.to_json())

service = build('admin', 'directory_v1', credentials=creds)



class AdminAPI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="integrate")
    @is_botAdmin
    async def integratesheets(self, ctx):
        await ctx.send("Starting GSuite Administration.")
        list_of_lists = sheet.get_values()
        for list in list_of_lists:
            DiscordTag = list[0]
            Name = list[1]
            Title = list[2]
            ContractSigned = list[3]
            DiscordID = list[4]

            if DiscordID == "NONE":
                print(f"{bcolors.WARNING}DiscordID is NONE for {DiscordTag} {bcolors.ENDC}")
            elif Name == "NONE":
                print(f"\n{bcolors.WARNING}{DiscordTag} didn't fill out their name {bcolors.ENDC}")
            elif ContractSigned == "y":
                try:
                    temppass = get_random_string()
                    user = {
                        "name": {
                            "givenName": Name.split()[0],
                            "fullName": Name,
                            "familyName": Name.split()[1]
                        },
                        "password": temppass,
                        "primaryEmail": f"{Name.split()[0].lower()}.{Name.split()[1].lower()}@schoolsimplified.org",
                        "changePasswordAtNextLogin": True,
                        "orgUnitPath": orgUnit[Title]
                    }
                    service.users().insert(body=user).execute()
                except Exception as e:
                    await ctx.send("Failed with (EXC 1) " + DiscordTag)
                    print(e)
                else:
                    try:
                        msg = f"""
                        Hello **{Name}**,\n\nAs a manager (or above), you are authorized to receive a **Google Workspace Account**.\nYour Google Workspace Account is as follows:\n\n> Username: `{Name.split()[0].lower()}.{Name.split()[1].lower()}@schoolsimplified.org`\n> Password: ||{temppass}||\n\nPlease use this information to access your Google Workspace Account, you will be required to change your password once you login.\nIf you require any IT Support please contact **timmy@schoolsimplified.org or DM Space#2587**.\n\nThank you for your time,\nSchool Simplified.\n\n\n\n\n
                        """
                        userOBJ: discord.User = await self.bot.fetch_user(int(DiscordID))
                        await userOBJ.send(msg)
                        await ctx.send("Sent to " + DiscordTag)
                    except Exception as e:
                        await ctx.send("Failed with (EXC 2) " + DiscordTag)
                        print(f"EXC 2 {e} | {list[0]}\n{msg}")

            else:
                print(f"\n{bcolors.FAIL}{DiscordTag} didn't sign shit{bcolors.ENDC}")
        await ctx.send("Ending GSuite Administration.")

def setup(bot):
    bot.add_cog(AdminAPI(bot))
