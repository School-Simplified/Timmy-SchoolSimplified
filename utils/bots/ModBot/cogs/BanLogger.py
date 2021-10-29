import asyncio
import json
import os
import re
from datetime import datetime
from random import randint

import discord
import gspread
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials
from core.common import MAIN_ID

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

try:
    sa_creds = json.loads(os.getenv("GSPREADSJSON"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(sa_creds, scope)
    client = gspread.authorize(creds)
    sheet = client.open("SchoolSimplifiedBans").sheet1
except Exception as e:
    print(f"ERROR: Could not authorize GSpreads: {e}")


def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list) + 1)


class BanUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ModLogID = MAIN_ID.ch_actionLogs

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """
        Pycord doesn't give us the information we need so we need to dig deeper and query the audit logs
        """

        now = datetime.now()

        if guild.id != MAIN_ID.g_main:
            return

        await asyncio.sleep(15)

        async for logs in guild.audit_logs(
            limit=1, oldest_first=False, action=discord.AuditLogAction.ban
        ):
            # Query the audit log for a type ban and get the latest one.

            moderator = logs.user
            target = logs.target

            # We need to check who banned the person.
            if moderator.id == 548410451818708993:  # Wick's ID
                banReasonAUDIT = logs.reason

                if "No reason specified by" in banReasonAUDIT:
                    random, fullUsernameMOD = banReasonAUDIT.split(
                        "No reason specified by "
                    )
                    banReason = "None Specified"

                else:
                    banReason = re.match(r"[^[]*\[([^]]*)\]", banReasonAUDIT).groups()[
                        0
                    ]

                    try:
                        random, fullUsernameMOD = banReasonAUDIT.split("- ")
                    except ValueError:
                        fullUsernameMOD = "Wick"

            else:
                banReason = logs.reason
                # Get full username with tag
                fullUsernameMOD = f"{moderator.display_name}#{moderator.discriminator}"

            # Okay now we got our reason, we need to get a few more things
            timestamp = now.strftime("%m/%d/%Y %H-%M-%S")  # Get our timestamp

            # Get full username with tag
            fullUsernameTARGET = f"{target.display_name}#{target.discriminator}"

            # Get everything into a list so we can bulk insert.
            row = [
                timestamp,
                fullUsernameTARGET,
                "",
                str(target.id),
                "",
                fullUsernameMOD,
                "",
                banReason,
            ]

            sheet.insert_row(row, 2)  # Insert data, and boom. We done!

            ModChannel = await self.bot.fetch_channel(self.ModLogID)

            embed = discord.Embed(
                title="Successful Ban Entry",
                description=f"Google Sheets has been updated with the recent ban!",
                color=discord.Colour.green(),
            )
            embed.add_field(
                name="Entry Details:",
                value=f"**Timestamp:** {timestamp}"
                f"\n**Banned User:** {fullUsernameTARGET}"
                f"\n**Target ID:** {str(target.id)}"
                f"\n**Moderator:** {fullUsernameMOD}"
                f"\n**Ban Reason:** {banReason}",
            )
            await ModChannel.send(embed=embed)
            break


def setup(bot):
    bot.add_cog(BanUpdate(bot))
