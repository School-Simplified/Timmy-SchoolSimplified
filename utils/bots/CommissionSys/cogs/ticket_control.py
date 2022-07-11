import asyncio

import discord
from discord.ext import commands

from core import database
from core.common import ButtonHandler, Emoji, LeaderID, StaffID
from utils.events.TicketDropdown import TicketExport


class MGMDropdownTickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.main_server = [StaffID.g_staff_resources, StaffID.g_staff_mgm]
        self.response_channel_dict = {
            StaffID.g_staff_resources: LeaderID.ch_com_log,
            StaffID.g_staff_mgm: 990311940989534229,
        }


    @commands.Cog.listener("on_interaction")
    async def mgm_ticket_control(self, interaction: discord.Interaction):
        inter_response = interaction.data

        if interaction.message is None:
            return

        try:
            val = inter_response["custom_id"]
        except KeyError:
            return
        query = database.TicketConfiguration.select().where(database.TicketConfiguration.guild_id == interaction.guild_id)
        print(val)

        if (
            not query.exists()
            # and interaction.message.id == int(self.CHID_DEFAULT)
            and inter_response["custom_id"] == "persistent_view:mgm_ticketdrop"
        ):
            pass
        elif "mgm_ch_lock_menu" in val:
            channel = interaction.message.channel
            guild = interaction.message.guild
            author = interaction.user

            embed = discord.Embed(
                title="Confirm?",
                description="Click an appropriate button.",
                color=discord.Colour.red(),
            )
            ButtonViews = discord.ui.View()
            ButtonViews.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.green,
                    label="Confirm",
                    custom_id="mgm_ch_lock_CONFIRM",
                    emoji="✅",
                    button_user=author,
                )
            )
            ButtonViews.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.red,
                    label="Cancel",
                    custom_id="mgm_ch_lock_CANCEL",
                    emoji="❌",
                    button_user=author,
                )
            )
            try:
                await interaction.response.send_message(
                    f"{author.mention}\n", embed=embed, view=ButtonViews
                )
            except Exception:
                await interaction.followup.send(f"{author.mention}\n", embed=embed, view=ButtonViews)

        elif "mgm_ch_lock_CONFIRM" in val:
            if val == "mgm_ch_lock_CONFIRM" or val == "mgm_ch_lock_CONFIRM:NONE":
                conf_id = "NONE"
            else:
                conf_id = val.split(":")[1]
            channel = interaction.message.channel
            guild = interaction.message.guild
            author = interaction.user
            query = (
                database.MGMTickets.select()
                .where(database.MGMTickets.ChannelID == interaction.channel_id)
                .get()
            )

            try:
                TicketOwner = await guild.fetch_member(query.authorID)
            except discord.NotFound:
                try:
                    await interaction.response.send_message(
                        f"{author.mention} The ticket owner has left the server."
                    )
                except Exception:
                    await interaction.followup.send(f"{author.mention} The ticket owner has left the server.")
            else:
                await channel.set_permissions(
                    TicketOwner, read_messages=False, reason="Ticket Perms Close(User)"
                )
            await interaction.message.delete()
            embed = discord.Embed(
                title="Support Staff Commands",
                description="Click an appropriate button.",
                color=discord.Colour.red(),
            )
            embed.set_footer(text="This ticket has been closed!")
            ButtonViews2 = discord.ui.View()

            ButtonViews2.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.green,
                    label="Close & Delete Ticket",
                    custom_id=f"mgm_ch_lock_C&D:{conf_id}",
                    emoji="🔒",
                )
            )
            ButtonViews2.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.grey,
                    label="Re-Open Ticket",
                    custom_id=f"mgm_ch_lock_R:{conf_id}",
                    emoji="🔓",
                )
            )
            ButtonViews2.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.blurple,
                    label="Create Transcript",
                    custom_id=f"mgm_ch_lock_T{conf_id}",
                    emoji="📝",
                )
            )
            ButtonViews2.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.red,
                    label="Cancel",
                    custom_id=f"mgm_ch_lock_STOP{conf_id}",
                    emoji="❌",
                )
            )
            try:
                await interaction.response.send_message(
                    author.mention, embed=embed, view=ButtonViews2
                )
            except Exception:
                await interaction.followup.send(author.mention, embed=embed, view=ButtonViews2)

        elif "mgm_ch_lock_STOP" in val:
            channel = interaction.message.channel
            author = interaction.user
            try:
                await interaction.response.send_message(
                    f"{author.mention} Alright, canceling request.", ephemeral=True
                )
            except Exception:
                await interaction.followup.send(f"{author.mention} Alright, canceling request.", ephemeral=True)
            await interaction.message.delete()

        elif "mgm_ch_lock_S" in val:
            channel = self.bot.get_channel(interaction.channel_id)
            author = interaction.user

            try:
                await interaction.response.send_message(
                    f"{author.mention} Alright, canceling request.", delete_after=5.0
                )
            except Exception:
                await interaction.followup.send(
                    f"{author.mention} Alright, canceling request.", delete_after=5.0
                )
            await interaction.message.delete()

        elif "mgm_ch_lock_R" in val:
            """
            Re-open Ticket
            """
            channel = self.bot.get_channel(interaction.channel_id)
            author = interaction.user
            guild = interaction.message.guild
            query = (
                database.MGMTickets.select()
                .where(database.MGMTickets.ChannelID == interaction.channel_id)
                .get()
            )
            try:
                TicketOwner = await guild.fetch_member(query.authorID)
            except discord.NotFound:
                try:
                    await interaction.response.send_message(
                        f"{author.mention} Sorry, but the ticket owner has left the server."
                    )
                except Exception:
                    await interaction.followup.send(
                        f"{author.mention} Sorry, but the ticket owner has left the server."
                    )
                return
            else:
                await channel.set_permissions(
                    TicketOwner,
                    read_messages=True,
                    send_messages=True,
                    reason="Ticket Perms Re-Open (User)",
                )
                try:
                    await interaction.response.send_message(
                        f"{author.mention} Alright, the ticket has been re-opened."
                    )
                except Exception:
                    await interaction.followup.send(
                        f"{author.mention} Alright, the ticket has been re-opened."
                    )
                await interaction.message.delete()

        elif "mgm_ch_lock_T" in val:
            if val == "mgm_ch_lock_T" or val == "mgm_ch_lock_T:NONE":
                conf_id = "NONE"
                response_log_channel: discord.TextChannel = self.bot.get_channel(
                    self.response_channel_dict[interaction.guild_id]
                )
            else:
                conf_id = val.split(":")[1]
                query = database.TicketConfiguration.select().where(database.TicketConfiguration.ID == conf_id).get()
                response_log_channel: discord.TextChannel = self.bot.get_channel(query.transcript_channel_id)
            channel: discord.TextChannel = interaction.channel


            author = interaction.user
            msg = await interaction.channel.send(
                f"Please wait, creating your transcript {Emoji.loadingGIF2}\n**THIS MAY TAKE SOME TIME**"
            )
            async with channel.typing():
                msg, file, S3_URL = await TicketExport(
                    self, channel, response_log_channel, author, None, True
                )
                await msg.delete()
            await interaction.channel.send(
                f"{author.mention}\nTranscript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {S3_URL}"
            )

        elif "mgm_ch_lock_C&D" in val:
            channel = self.bot.get_channel(interaction.channel_id)
            author = interaction.user
            response_log_channel: discord.TextChannel = self.bot.get_channel(
                self.response_channel_dict[interaction.guild_id]
            )
            query = (
                database.MGMTickets.select()
                .where(database.MGMTickets.ChannelID == interaction.channel_id)
                .get()
            )
            msgO = await interaction.channel.send(
                f"{author.mention}\nPlease wait, generating a transcript {Emoji.loadingGIF2}\n**THIS MAY TAKE SOME TIME**"
            )
            async with channel.typing():
                TicketOwner = self.bot.get_user(query.authorID)
                if TicketOwner is None:
                    TicketOwner = await self.bot.fetch_user(query.authorID)

                messages = [message async for message in channel.history(limit=None)]
                author_list = []

                for msg in messages:
                    if msg.author not in author_list:
                        author_list.append(msg.author)
                msg, transcript_file, url = await TicketExport(
                    self, channel, response_log_channel, TicketOwner, author_list
                )
                # S3_upload_file(transcript_file.filename, "ch-transcriptlogs")
                # print(transcript_file.filename)

            try:
                await msgO.edit(
                    content=f"{author.mention}\nTranscript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {url}"
                )
            except Exception:
                try:
                    await msgO.edit(
                        content=f"{author.mention}\nTranscript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {url}"
                    )
                except Exception:
                    await msgO.edit(
                        content=f"{author.mention}\nTranscript Created!\n>>> `Jump Link:` {msg.jump_url}\n`Transcript Link:` {url}"
                    )
            await asyncio.sleep(5)
            await channel.send(f"{author.mention} Alright, closing ticket.")
            await channel.delete()
            query.delete_instance()


async def setup(bot):
    await bot.add_cog(MGMDropdownTickets(bot))
