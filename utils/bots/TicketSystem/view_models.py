from __future__ import annotations, print_function

from datetime import datetime
from typing import List

import discord
import pytz
from discord import ui
from discord.ext import commands
from googleapiclient.errors import HttpError

import core.common
from core import database
from core.common import (
    ButtonHandler,
    get_random_string,
    service,
    HRID,
    StaffID,
    TechID,
    raw_export,
    Emoji,
)

EmailSelectOptions = [
    discord.SelectOption(
        label="Individual Email",
        description="Request an individual email address.",
        emoji="👤",
    ),
    discord.SelectOption(
        label="Team Email",
        description="Request a team email address.",
        emoji="👥",
    ),
]


def create_ui_modal_class(conf_id):
    query = database.TicketConfiguration.select().where(
        database.TicketConfiguration.id == conf_id
    )
    if query.exists():
        query: database.TicketConfiguration = query.get()
    else:
        return None

    class UIModal(ui.Modal, title=query.title):
        def __init__(
            self, bot: commands.Bot, title: str, questions_l: str, conf_id: int
        ):
            super().__init__(timeout=None)
            self.bot = bot
            self.title = title
            self.questions = str(questions_l).strip("][").split(", ")
            self.conf_id = conf_id

            self.question_obj: List[ui.TextInput] = []
            self.answers = []
            self.index_to_config_dict = {
                1: query.q1_config,
                2: query.q2_config,
                3: query.q3_config,
                4: query.q4_config,
                5: query.q5_config,
            }
            self.config_to_TextStyle_dict = {
                "S": discord.TextStyle.short,
                "L": discord.TextStyle.long,
            }
            self.create_ui_elements()

        def create_ui_elements(self):
            cache_list = []
            for elem in self.questions:
                cache_list.append(elem.strip("'"))
            self.questions = cache_list
            index = 1

            for question_e in self.questions:
                # get q1.config and update config to match ui.TextInput arguments
                config = self.index_to_config_dict[index]
                if config is None or config == "":
                    style = discord.TextStyle.long
                    min_length = None
                    max_length = None
                else:
                    style, min_length, max_length = config.split(",")
                    style = self.config_to_TextStyle_dict[style]

                text_input = ui.TextInput(
                    label=question_e,
                    required=True,
                    style=style,
                    min_length=min_length,
                    max_length=max_length,
                )
                self.add_item(text_input)
                self.question_obj.append(text_input)
                index += 1

        async def on_submit(self, interaction: discord.Interaction):
            for question in self.question_obj:
                self.answers.append(question.value)

            query = database.TicketConfiguration.select().where(
                database.TicketConfiguration.id == self.conf_id
            )

            if not query.exists():
                return await interaction.response.send_message(
                    "Ticket configuration no longer exists!"
                )
            else:
                query: database.TicketConfiguration = query.get()

            if query.limit != 0:
                lim_query = database.MGMTickets.select().where(
                    (database.MGMTickets.configuration_id == self.conf_id)
                    & (database.MGMTickets.authorID == interaction.user.id)
                )

                if lim_query.count() >= query.limit:
                    return await interaction.response.send_message(
                        "You have hit the ticket limit for this "
                        "category, please close already open "
                        "tickets before opening a new one!"
                    )

            ticket_server = self.bot.get_guild(query.guild_id)
            ticket_category = discord.utils.get(
                ticket_server.categories, id=query.category_id
            )
            member = interaction.guild.get_member(interaction.user.id)

            ticket_channel = await ticket_category.create_text_channel(
                f"{interaction.user.name}-{query.channel_identifier}",
                topic=f"{interaction.user.name} | {interaction.user.id}\n{query.title}",
                reason=f"Requested by {interaction.user.name} break",
            )
            cache_query = database.MGMTickets.create(
                ChannelID=ticket_channel.id,
                authorID=interaction.user.id,
                createdAt=datetime.now(),
                configuration_id=self.conf_id,
            )
            cache_query.save()

            await ticket_channel.set_permissions(
                ticket_server.default_role, read_messages=False
            )

            # make query.role_id into a list (comma seperated string) and add each role to the ticket channel
            if query.role_id is not None:
                role_list = [
                    int(e) if e.strip().isdigit() else e
                    for e in query.role_id.split(",")
                ]
                for role in role_list:
                    role = discord.utils.get(ticket_server.roles, id=int(role))
                    try:
                        await ticket_channel.set_permissions(
                            role, read_messages=True, send_messages=True
                        )
                    except discord.NotFound:
                        pass

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
                    custom_id=f"mgm_ch_lock_menu:{query.id}",
                )
            )
            LCM = await ticket_channel.send(
                interaction.user.mention, embed=control_embed, view=LCB
            )
            await LCM.pin()
            # make an embed that has the questions and answers
            embed = discord.Embed(
                title="Ticket Created",
                description=f"{interaction.user.mention} has created a ticket in {ticket_channel.mention}",
                color=discord.Colour.gold(),
            )
            for question_final_embed, answer in zip(self.questions, self.answers):
                embed.add_field(name=question_final_embed, value=answer, inline=False)
            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.avatar.url,
            )
            embed.set_footer(text=f"ID: {interaction.user.id}")
            await ticket_channel.send(embed=embed)

            await interaction.response.send_message(
                content=f"{interaction.user.mention}, I've created a ticket for you!\n> {ticket_channel.mention}",
                ephemeral=True,
            )

    return UIModal


def create_ticket_button(conf_id):
    query = database.TicketConfiguration.select().where(
        database.TicketConfiguration.id == conf_id
    )
    if query.exists():
        query: database.TicketConfiguration = query.get()
    else:
        return None

    class GlobalSubmitButton(discord.ui.View):
        def __init__(self, modal_view) -> None:
            super().__init__(timeout=None)
            self.modal_view = modal_view
            self.value = None

        @discord.ui.button(
            label=query.button_label,
            style=discord.ButtonStyle.blurple,
            disabled=False,
            custom_id=f"cts_pers:{query.id}",
        )
        async def starts_commission(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if self.modal_view is not None:
                await interaction.response.send_modal(self.modal_view)
            else:
                await interaction.response.send_message("No modal found!")

    return GlobalSubmitButton


def create_no_form_button(conf_id):
    query = database.TicketConfiguration.select().where(
        database.TicketConfiguration.id == conf_id
    )
    if query.exists():
        query: database.TicketConfiguration = query.get()
    else:
        return None

    class GlobalSubmitButton(discord.ui.View):
        def __init__(self, conf_id, bot) -> None:
            super().__init__(timeout=None)
            self.conf_id = conf_id
            self.bot = bot
            self.value = None

        @discord.ui.button(
            label=query.button_label,
            style=discord.ButtonStyle.blurple,
            disabled=False,
            custom_id=f"cts_pers:{query.id}",
        )
        async def starts_commission(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            query = database.TicketConfiguration.select().where(
                database.TicketConfiguration.id == self.conf_id
            )

            if not query.exists():
                return await interaction.response.send_message(
                    "Ticket configuration no longer exists!"
                )
            else:
                query: database.TicketConfiguration = query.get()

            if query.limit != 0:
                lim_query = database.MGMTickets.select().where(
                    (database.MGMTickets.configuration_id == self.conf_id)
                    & (database.MGMTickets.authorID == interaction.user.id)
                )

                if lim_query.count() >= query.limit:
                    return await interaction.response.send_message(
                        "You have hit the ticket limit for this "
                        "category, please close already open "
                        "tickets before opening a new one!"
                    )

            ticket_server = self.bot.get_guild(query.guild_id)
            ticket_category = discord.utils.get(
                ticket_server.categories, id=query.category_id
            )
            member = interaction.guild.get_member(interaction.user.id)

            ticket_channel = await ticket_category.create_text_channel(
                f"{interaction.user.name}-{query.channel_identifier}",
                topic=f"{interaction.user.name} | {interaction.user.id}\n{query.title}",
                reason=f"Requested by {interaction.user.name} break",
            )
            cache_query = database.MGMTickets.create(
                ChannelID=ticket_channel.id,
                authorID=interaction.user.id,
                createdAt=datetime.now(),
                configuration_id=self.conf_id,
            )
            cache_query.save()

            await ticket_channel.set_permissions(
                ticket_server.default_role, read_messages=False
            )

            # make query.role_id into a list (comma seperated string) and add each role to the ticket channel
            if query.role_id is not None:
                role_list = [
                    int(e) if e.strip().isdigit() else e
                    for e in query.role_id.split(",")
                ]
                for role in role_list:
                    role = discord.utils.get(ticket_server.roles, id=int(role))
                    try:
                        await ticket_channel.set_permissions(
                            role, read_messages=True, send_messages=True
                        )
                    except discord.NotFound:
                        pass

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
                    custom_id=f"mgm_ch_lock_menu:{query.id}",
                )
            )
            LCM = await ticket_channel.send(
                interaction.user.mention, embed=control_embed, view=LCB
            )
            await LCM.pin()
            # make an embed that has the questions and answers
            embed = discord.Embed(
                title="Ticket Created",
                description=f"{interaction.user.mention} has created a ticket in {ticket_channel.mention}",
                color=discord.Colour.gold(),
            )
            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.avatar.url,
            )
            embed.set_footer(
                text=f"ID: {interaction.user.id} | This ticket config has no form setup!"
            )
            await ticket_channel.send(embed=embed)

            await interaction.response.send_message(
                content=f"{interaction.user.mention}, I've created a ticket for you!\n> {ticket_channel.mention}",
                ephemeral=True,
            )

    return GlobalSubmitButton


class HREmailDisabled(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, disabled=True)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        pass

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, disabled=True)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass


class HREmailConfirm(discord.ui.View):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Confirm",
        emoji="✅",
        style=discord.ButtonStyle.green,
        custom_id="temp_mgm_confirm",
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = interaction.message.embeds[0]
        embed.title = f"[CREATED] {embed.title}"
        embed.colour = discord.Colour.green()
        temppass = get_random_string()
        if embed.fields[0].value == "G":
            return await interaction.response.send_message(
                "Error, not supported yet.\nYou'll need to contact a Super/User "
                "Administrator to create this manually.",
                ephemeral=True,
            )
        elif embed.fields[0].value == "T":
            firstname = embed.fields[4].value
            lastname = "Team"
            user = {
                "name": {
                    "givenName": firstname,
                    "fullName": firstname + " Team",
                    "familyName": "Team",
                },
                "password": temppass,
                "primaryEmail": embed.fields[2].value,
                "changePasswordAtNextLogin": True,
                "orgUnitPath": "/School Simplified Team Acc.",
                "organizations": [
                    {
                        "title": "Team Email",
                        "primary": True,
                        "department": embed.fields[4].value,
                        "description": "Team",
                    }
                ],
            }
        elif embed.fields[0].value == "Personal":
            firstname = embed.fields[1].value
            lastname = embed.fields[2].value
            user = {
                "name": {
                    "givenName": embed.fields[1].value,
                    "fullName": embed.fields[1].value + " " + embed.fields[2].value,
                    "familyName": embed.fields[2].value,
                },
                "password": temppass,
                "primaryEmail": f"{embed.fields[1].value}.{embed.fields[2].value}@schoolsimplified.org",
                "changePasswordAtNextLogin": True,
                "orgUnitPath": "/School Simplified Personal Acc.",
                "relations": [{"value": embed.fields[3].value, "type": "manager"}],
                "organizations": [
                    {
                        "title": embed.fields[5].value,
                        "primary": True,
                        "type": "work",
                        "department": embed.fields[4].value,
                    }
                ],
            }
        else:
            return
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
                    f"{interaction.user.mention} An error occurred. Please try again later; forward this to a Bot "
                    f"Developer if you continue to have problems!.\nError: {e} "
                )
        else:
            if embed.fields[0].value == "Personal":
                await interaction.response.send_message(
                    f"{interaction.user.mention} Successfully created **{firstname} {lastname}'s** account.\n"
                    f"**Username:** {firstname}.{lastname}@schoolsimplified.org\n"
                    f"**Organization Unit:** {user['orgUnitPath']}",
                    ephemeral=False,
                )
            else:
                await interaction.response.send_message(
                    f"{interaction.user.mention} Successfully created **{user['name']['givenName']}'s** account.\n"
                    f"**Username:** {user['primaryEmail']}\n"
                    f"**Organization Unit:** {user['orgUnitPath']}\n",
                    "**Note:** This email has been flagged as a `TEAM` email.",
                    ephemeral=False,
                )
            await interaction.followup.send(
                f"**Temporary Password:**\n||{temppass}||\n\n**Instructions:**\nGive the Username and the Temporary "
                f"Password to the user and let them know they have **1 week** to setup 2FA before they get locked out. ",
                ephemeral=True,
            )
        self.value = True
        await interaction.message.edit(embed=embed, view=HREmailDisabled())
        self.stop()

    @discord.ui.button(
        label="Cancel",
        emoji="❌",
        style=discord.ButtonStyle.red,
        custom_id="temp_mgm_cancel",
    )
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        embed = interaction.message.embeds[0]
        embed.title = f"[RESOLVED] {embed.title}"
        embed.colour = discord.Color.brand_red()

        await interaction.message.edit(embed=embed, view=HREmailDisabled())
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
        await interaction.response.send_message(
            "Thank you for your submission, forwarding your request to HR!",
            ephemeral=True,
        )
        hr_email: discord.TextChannel = self.bot.get_channel(HRID.ch_email_requests)
        embed = discord.Embed(
            title=f"Email Request from {interaction.user.name}#{interaction.user.discriminator}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="Account Type", value="Personal", inline=False)
        embed.add_field(name="First Name", value=self.first_name.value)
        embed.add_field(name="Last Name", value=self.last_name.value)
        embed.add_field(
            name="Managers Email", value=self.managers_email.value, inline=False
        )
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        embed.add_field(name="Team Role", value=self.team_role.value)
        await hr_email.send(embed=embed, view=HREmailConfirm(self.bot))


class TEmailForm(ui.Modal, title="Email Address Requests"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    email_type = ui.TextInput(
        label="Purpose of Email",
        style=discord.TextStyle.short,
        placeholder="G for Group Email and T for Team Email",
        max_length=1,
    )

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

    team_name = ui.TextInput(
        label="Team Name",
        style=discord.TextStyle.short,
        placeholder="What Team is this email for?",
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        email_type = self.email_type.value
        await interaction.response.send_message(
            "Thank you for your submission, forwarding your request to HR!",
            ephemeral=True,
        )
        hr_email: discord.TextChannel = self.bot.get_channel(HRID.ch_email_requests)
        embed = discord.Embed(
            title=f"Email Request from {interaction.user.name}#{interaction.user.discriminator}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        account_type = {"G": "Group", "T": "Team"}
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(
            name="Account Type", value=account_type[email_type], inline=False
        )
        embed.add_field(name="Email Purpose", value=self.email_purpose.value)
        embed.add_field(name="Desired Email", value=self.requested_address.value)
        embed.add_field(name="Email Type", value=email_type)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        await hr_email.send(embed=embed, view=HREmailConfirm(self.bot))


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
        await interaction.response.send_message(
            "Thank you for your submission, creating your ticket now!", ephemeral=True
        )
        counter_num = (
            database.BaseTickerInfo.select()
            .where(database.BaseTickerInfo.guildID == interaction.guild.id)
            .get()
        )
        num = counter_num.counter
        counter_num.counter = counter_num.counter + 1
        counter_num.save()

        category = discord.utils.get(
            interaction.guild.categories, id=StaffID.cat_staffapps_tickets
        )
        channel = await interaction.guild.create_text_channel(
            f"staff-apps-{num}", category=category
        )

        await channel.set_permissions(
            HRID.r_hr_staff,
            read_messages=True,
            send_messages=True,
            reason="Ticket Perms (HR Staff)",
        )

        await channel.set_permissions(
            interaction.user,
            read_messages=True,
            send_messages=True,
            reason="Ticket Perms (User)",
        )
        await channel.set_permissions(
            interaction.guild.default_role,
            read_messages=False,
            send_messages=False,
            reason="Ticket Perms (Default Role)",
        )

        controlTicket = discord.Embed(
            title="Control Panel",
            description="To end this ticket, click the lock button!",
            color=discord.Colour.gold(),
        )
        LockControlButton = discord.ui.View()
        LockControlButton.add_item(
            ButtonHandler(
                style=discord.ButtonStyle.green,
                url=None,
                disabled=False,
                label="Lock",
                emoji="🔒",
                custom_id="mgm_ch_lock_menu",
            )
        )

        LCM = await channel.send(
            interaction.user.mention, embed=controlTicket, view=LockControlButton
        )
        await LCM.pin()

        tz = pytz.timezone("EST")
        opened_at = datetime.now(tz)
        query = database.MGMTickets.create(
            ChannelID=channel.id,
            authorID=interaction.message.author.id,
            createdAt=opened_at,
        )
        query.save()

        embed = discord.Embed(
            title=f"Staff Application from {interaction.user.name}#{interaction.user.discriminator}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        embed.add_field(name="Application", value=self.target_app.value, inline=False)
        embed.add_field(name="Approved By", value=self.approval.value, inline=False)
        await channel.send(embed=embed)


class StaffAnnouncements(ui.Modal, title="Staff Announcements"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    publish_location = ui.TextInput(
        label="Where will this be published?:",
        style=discord.TextStyle.short,
        max_length=1024,
        placeholder="For Staff or Public?",
    )

    app_title = ui.TextInput(
        label="Subject:",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    team_name = ui.TextInput(
        label="What team/dept. is this for?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    """target_publication = ui.TextInput(
        label="Where will this be published?",
        style=discord.TextStyle.long,
        max_length=1024,
    )"""

    approval = ui.TextInput(
        label="Who approved this?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Thank you for your submission, creating your ticket now!", ephemeral=True
        )
        counter_num = (
            database.BaseTickerInfo.select()
            .where(database.BaseTickerInfo.guildID == interaction.guild.id)
            .get()
        )
        num = counter_num.counter
        counter_num.counter = counter_num.counter + 1
        counter_num.save()

        category = discord.utils.get(
            interaction.guild.categories, id=StaffID.cat_announcements_tickets
        )
        channel = await interaction.guild.create_text_channel(
            f"staff-announce-{num}", category=category
        )

        await channel.set_permissions(
            interaction.user,
            read_messages=True,
            send_messages=True,
            reason="Ticket Perms (User)",
        )
        await channel.set_permissions(
            interaction.guild.default_role,
            read_messages=False,
            send_messages=False,
            reason="Ticket Perms (Default Role)",
        )

        controlTicket = discord.Embed(
            title="Control Panel",
            description="To end this ticket, click the lock button!",
            color=discord.Colour.gold(),
        )
        LockControlButton = discord.ui.View()
        LockControlButton.add_item(
            ButtonHandler(
                style=discord.ButtonStyle.green,
                url=None,
                disabled=False,
                label="Lock",
                emoji="🔒",
                custom_id="mgm_ch_lock_menu",
            )
        )

        LCM = await channel.send(
            interaction.user.mention, embed=controlTicket, view=LockControlButton
        )
        await channel.send(
            "Thank you for creating an announcement ticket! Please use the link below to schedule a "
            "time for the announcement to be sent out. When scheduling, keep the following in "
            "mind:\n\n> <:barrow:967579494833618954> You may only schedule a date that is at least "
            "**two weeks** AFTER the creation of this ticket.\n> <:barrow:967579494833618954> The "
            "scheduled date is NOT final; Corporate Officers reserve the right to change the date if "
            "the announcement is not "
            "ready.\n\n<:barrow2:967579638207500398>https://ssimpl.org/AnnouncementScheduling"
        )
        await LCM.pin()

        tz = pytz.timezone("EST")
        opened_at = datetime.now(tz)
        query = database.MGMTickets.create(
            ChannelID=channel.id,
            authorID=interaction.message.author.id,
            createdAt=opened_at,
        )
        query.save()

        embed = discord.Embed(
            title=f"Staff Announcements from {interaction.user.name}#{interaction.user.discriminator}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="Subject", value=self.app_title.value, inline=False)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        embed.add_field(
            name="Target Publication", value=self.publish_location.value, inline=False
        )
        embed.add_field(name="Approved By", value=self.approval.value, inline=False)
        await channel.send(embed=embed)


class MGMCommissionButton(discord.ui.View):
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
            956619079853179031: StaffApps(self.bot),
            956619132525244516: StaffAnnouncements(self.bot),
        }
        modal = channel_to_modal_map[interaction.channel.id]
        await interaction.response.send_modal(modal)


class EmailDropdown(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Individual Email",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:i_email_mgm",
        emoji="👤",
    )
    async def i_email(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        modal = IEmailForm(self.bot)
        return await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="Team Email",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:t_email_mgm",
        emoji="👥",
    )
    async def t_email(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        modal = TEmailForm(self.bot)
        return await interaction.response.send_modal(modal)


class TechnicalCommissionConfirm(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="persistent_view:tempconfirm",
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        transcript_log = self.bot.get_channel(TechID.ch_ticket_log)
        ch = self.bot.get_channel(interaction.channel_id)

        await raw_export(ch, transcript_log, interaction.user)
        await ch.delete()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(
            "ok, not removing this channel.", ephemeral=True
        )
        self.value = False
        self.stop()


class LockButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Lock",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:lock",
        emoji="🔒",
    )
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        ch = self.bot.get_channel(interaction.channel_id)
        temp_confirm_instance = TechnicalCommissionConfirm(self.bot)

        await ch.send(
            "Are you sure you want to close this ticket?", view=temp_confirm_instance
        )


class GSuiteVerify(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(
        label="Verify with GSuite",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:gsuiteverify",
        emoji=Emoji.gsuite_logo,
    )
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True


class TempConfirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="persistent_view:tempconfirm",
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()


class NitroConfirmFake(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(
        label="Claim",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:nitrofake",
    )
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message(
                "https://images-ext-2.discordapp.net/external/YTk-6Mfxbbr8KwIc-3Pyy5Z_06tfpcO65MflxYgbjA8/"
                "%3Fcid%3D73b8f7b119cc9225923f70c7e25a1f8e8932c7ae8ef48fe7%26rid%3Dgiphy.mp4%26ct%3Dg/"
                "https/media2.giphy.com/media/Ju7l5y9osyymQ/giphy.mp4",
                ephemeral=True,
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                "https://images-ext-2.discordapp.net/external/YTk-6Mfxbbr8KwIc-3Pyy5Z_06tfpcO65MflxYgbjA8/%3Fcid%3D73"
                "b8f7b119cc9225923f70c7e25a1f8e8932c7ae8ef48fe7%26rid%3Dgiphy.mp4%26ct%3Dg"
                "/https/media2.giphy.com/media/Ju7l5y9osyymQ/giphy.mp4",
                ephemeral=True,
            )
        self.value = True


class TicketLockButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Lock",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:lock",
        emoji="🔒",
    )
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        ch = self.bot.get_channel(interaction.channel_id)
        TempConfirmInstance = TicketTempConfirm()

        await ch.send(
            "Are you sure you want to close this ticket?", view=TempConfirmInstance
        )


class TicketTempConfirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="persistent_view:tempconfirm",
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()


class CommissionConfirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()


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
        await interaction.response.send_modal(GSuiteForm(self.bot))


class RecruitmentForm(ui.Modal, title="Recruitment Request"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    urgency = ui.TextInput(
        label="How urgent is your request?",
        style=discord.TextStyle.short,
        max_length=100,
        placeholder="LOW, MED, HIGH, or CRIT",
    )

    rank = ui.TextInput(
        label="What rank is this position?",
        style=discord.TextStyle.short,
        max_length=100,
        placeholder="Leadership, Associate",
    )

    position_title = ui.TextInput(
        label="What is the position title?",
        style=discord.TextStyle.short,
        max_length=100,
    )

    position_title = ui.TextInput(
        label="What is the position title?",
        style=discord.TextStyle.short,
        max_length=100,
    )

    num_people = ui.TextInput(
        label="How many people are needed?",
        style=discord.TextStyle.short,
        max_length=5,
    )

    async def on_submit(self, interaction: discord.Interaction):
        mgm_server = self.bot.get_guild(core.common.StaffID.g_staff_resources)
        ticket_category = discord.utils.get(
            mgm_server.categories, id=StaffID.cat_recruiting_tickets
        )
        member = interaction.guild.get_member(interaction.user.id)

        ticket_channel = await ticket_category.create_text_channel(
            f"{interaction.user.name}-recruitment-request",
            topic=f"{interaction.user.name} | {interaction.user.id} recruitment-request",
            reason=f"Requested by {interaction.user.name} recruitment-request",
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
            title="Recruitment Request",
            description=f"User: {member.mention}\n"
            f"**Position Title:** {self.position_title.value}\n"
            f"**Ranking:** {self.children[0].value}\n"
            f"**People Needed:** {self.num_people.value}\n"
            f"**Urgency:** {self.children[1].value}",
            color=discord.Colour.gold(),
        )
        embed_information.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
        )
        embed_information.set_footer(text=f"ID: {interaction.user.id}")
        await ticket_channel.send(embed=embed_information)
        await interaction.response.send_message(
            f"Your ticket has been created!\nYou can view it here: <#{ticket_channel.id}>",
            ephemeral=True,
        )


class RecruitmentButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Start Recruitment Request",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:recruit_form",
        emoji="📝",
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.send_modal(RecruitmentForm(self.bot))
