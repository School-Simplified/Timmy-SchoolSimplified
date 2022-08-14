from datetime import datetime
from typing import Literal, List

import discord
from discord import ui, app_commands
from discord.ext import commands

from core import database
from core.checks import is_botAdmin, slash_is_bot_admin
from core.common import (
    Emoji,
    TechID,
    StaffID,
)
from utils.bots.TicketSystem.view_models import create_ui_modal_class, create_ticket_button, MGMCommissionButton, \
    EmailDropdown, create_no_form_button


def text_to_list(hashtags):
    return hashtags.strip("[]").replace("'", "").split(",")


class QuestionInput(ui.Modal, title="Submit Questions here!"):
    def __init__(
        self,
        bot: commands.Bot,
        title: str,
        channel_name: str,
        button_label: str,
        category_id: int,
        channel_id: int,
        transcript_channel: int,
        role_id: str,
        limit: int = None,
    ) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.title = title
        self.channel_name = channel_name
        self.button_label = button_label
        self.category_id = category_id
        self.channel_id = channel_id
        self.transcript_channel = transcript_channel
        self.role_id = role_id
        self.limit = limit

    first_question = ui.TextInput(
        label="Question One:",
        style=discord.TextStyle.short,
        max_length=45,
        min_length=5,
        required=False,
        placeholder="Leave blank if you don't want to use this question or leave everything blank for no questions!",
    )
    second_question = ui.TextInput(
        label="Question Two:",
        style=discord.TextStyle.short,
        max_length=45,
        min_length=5,
        required=False,
        placeholder="Leave blank if you don't want to use this question or leave everything blank for no questions!",
    )
    third_question = ui.TextInput(
        label="Question Three:",
        style=discord.TextStyle.short,
        max_length=45,
        min_length=5,
        required=False,
        placeholder="Leave blank if you don't want to use this question or leave everything blank for no questions!",
    )
    fourth_question = ui.TextInput(
        label="Question Four:",
        style=discord.TextStyle.short,
        max_length=45,
        min_length=5,
        required=False,
        placeholder="Leave blank if you don't want to use this question or leave everything blank for no questions!",
    )
    fifth_question = ui.TextInput(
        label="Question Five:",
        style=discord.TextStyle.short,
        max_length=45,
        min_length=5,
        required=False,
        placeholder="Leave blank if you don't want to use this question or leave everything blank for no questions!",
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.limit is None:
            limit = 0
        if (
            self.first_question.value == ""
            and self.second_question.value == ""
            and self.third_question.value == ""
            and self.fourth_question.value == ""
            and self.fifth_question.value == ""
        ):
            questions = []
        else:
            questions = [
                self.first_question.value,
                self.second_question.value,
                self.third_question.value,
                self.fourth_question.value,
                self.fifth_question.value,
            ]
            questions = list(filter(None, questions))

        query = database.TicketConfiguration.select().where(
            database.TicketConfiguration.category_id == self.category_id
        )
        if query.exists():
            return await interaction.response.send_message(
                "Tickets already setup in this category, delete the category and create a new one "
                "if you wish to re-configure this config!!."
            )
        else:
            query = database.TicketConfiguration.create(
                category_id=self.category_id,
                channel_id=self.channel_id,
                role_id=self.role_id,
                limit=self.limit,
                author_id=interaction.user.id,
                created_at=datetime.now(),
                questions=questions,
                transcript_channel_id=self.transcript_channel,
                guild_id=interaction.guild.id,
                title=self.title,
                channel_identifier=self.channel_name,
                button_label=self.button_label,
            )
            query.save()

            if questions.count != 0:
                UIModal = create_ui_modal_class(query.id)
                modal = UIModal(self.bot, self.title, query.questions, query.id)

                GlobalSubmitButton = create_ticket_button(query.id)
                submit_button = GlobalSubmitButton(modal)
            else:
                no_form_button = create_no_form_button(query.id)
                submit_button = no_form_button(query.id, self.bot)


            ticket_start_channel: discord.TextChannel = self.bot.get_channel(
                query.channel_id
            )
            await ticket_start_channel.send("** **", view=submit_button)

            # Send a final output of everything in an embed
            embed = discord.Embed(
                title="Successfully Created Ticket Configuration",
                description=f"{interaction.user.mention} has created a ticket configuration for {ticket_start_channel.mention}",
                color=discord.Colour.brand_green(),
            )
            embed.add_field(
                name="Instructions",
                value=f"This configuration has been setup and your requested button "
                f"has been sent the start channel you provided in the command. "
                f"If you wish to re-send the button for any reason, "
                f"please use the following ID: {query.id} with /send_button.",
                inline=False,
            )
            embed.add_field(name="Title", value=query.title, inline=False)
            embed.add_field(
                name="Channel Identifier", value=query.channel_identifier, inline=False
            )
            embed.add_field(name="Category", value=query.category_id, inline=False)
            embed.add_field(name="Guild", value=query.guild_id, inline=False)
            embed.add_field(name="Limit", value=query.limit, inline=False)
            embed.add_field(name="Roles", value=query.role_id, inline=False)
            embed.add_field(name="Questions", value=query.questions, inline=False)

            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.avatar.url,
            )
            embed.set_footer(text=f"ID: {query.id}")
            await interaction.response.send_message(embed=embed)


class MGMTickets(commands.Cog):
    """
    Commands for bot commissions
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.__cog_name__ = "MGM Commissions"
        self.whitelisted_cat = [
            StaffID.cat_design_tickets,
            StaffID.cat_recruiting_tickets,
            StaffID.cat_cs_hours_tickets,
            StaffID.cat_complaint_tickets,
            StaffID.cat_suggestions_tickets,
            StaffID.cat_resignation_tickets,
            StaffID.cat_break_tickets,
            StaffID.cat_announcements_tickets,
            StaffID.cat_staffapps_tickets,
            StaffID.cat_QnA_tickets,
            StaffID.cat_hr_tickets,
        ]
        # self.autoUnarchiveThread.start()

    @property
    def display_emoji(self) -> str:
        return Emoji.pythonLogo

    """async def cog_unload(self):
        self.autoUnarchiveThread.cancel()"""

    @commands.command()
    @is_botAdmin
    async def send_mgm_embed(self, ctx, param: int):
        if param == 1:
            await ctx.send("Testing Mode", view=MGMCommissionButton(self.bot))
        elif param == 2:
            view = EmailDropdown(self.bot)
            await ctx.send("Testing Mode", view=view)

    CTS = app_commands.Group(
        name="cts",
        description="Custom Ticket System Commands",
        guild_ids=[TechID.g_tech, StaffID.g_staff_resources, StaffID.g_staff_mgm],
    )

    @CTS.command(
        name="setup_tickets",
        description="Setup tickets for a category",
    )
    @app_commands.describe(
        title="A title for this configuration.",
        channel_identifier="Identifier for what the channel name will be.",
        button_label="Button Label",
        category_id="The category ID to setup tickets for",
        start_channel="The channel ID where tickets will be created",
        transcript_channel="The channel ID where transcripts will be posted",
        role_id="Role IDs (seperated by commas) that will be able to view tickets",
        limit="The limit of tickets that can be created per person, leave blank for no limit",
    )
    @slash_is_bot_admin()
    async def setup(
        self,
        interaction: discord.Interaction,
        title: str,
        channel_identifier: str,
        button_label: str,
        category_id: str,
        start_channel: discord.TextChannel,
        transcript_channel: discord.TextChannel,
        role_id: str = None,
        limit: int = 0,
    ):
        """
        Setup tickets for a category

        title: A title for this configuration.
        channel_name: Identifier for what the channel name will be.
        button_label: Button Label
        category_id: The category ID to setup tickets for
        channel_id: The channel ID where tickets will be created
        transcript_channel: The channel ID where transcripts will be posted
        role_id: Role IDs (seperated by commas) that will be able to view tickets
        limit: The limit of tickets that can be created per person, leave blank for no limit
        """

        await interaction.response.send_modal(
            QuestionInput(
                self.bot,
                title,
                channel_identifier,
                button_label,
                int(category_id),
                start_channel.id,
                transcript_channel.id,
                role_id,
                limit,
            )
        )

    @CTS.command(
        name="send_button",
        description="Send a pre-configured ticket button",
    )
    @app_commands.describe(
        configuration_id="The configuration ID that corresponds to the button.",
        channel="Where the button will be sent; leave blank to send it to the channel it was configured with.",
        message_id="Edits the message to include button in same message. Channel must be filled out for this.",
    )
    @slash_is_bot_admin()
    async def send_button(
        self,
        interaction: discord.Interaction,
        configuration_id: int,
        channel: discord.TextChannel = None,
        message_id: str = None,
    ):
        """
        Send a pre-configured ticket button

        configuration_id: The configuration ID that corresponds to the button
        channel: Where the button will be sent
        """
        query = database.TicketConfiguration.select().where(
            database.TicketConfiguration.id == configuration_id
        )
        if not query.exists():
            return await interaction.response.send_message("Invalid configuration ID")
        query = query.get()

        UIModal = create_ui_modal_class(query.id)
        modal = UIModal(self.bot, query.title, query.questions, query.id)

        UIButton = create_ticket_button(query.id)
        submit_button = UIButton(modal)

        if channel is None and message_id is None:
            ticket_start_channel = self.bot.get_channel(query.channel_id)
            await ticket_start_channel.send("** **", view=submit_button)
        elif message_id is not None and channel is None:
            return await interaction.response.send_message(
                "You must provide a channel (the channel where the message "
                "is in) if you are providing a message ID"
            )
        elif channel is not None and message_id is None:
            ticket_start_channel = channel
            await ticket_start_channel.send("** **", view=submit_button)
        elif channel is not None and message_id is not None:
            ticket_start_channel = channel
            try:
                message = await ticket_start_channel.fetch_message(message_id)
            except:
                return await interaction.response.send_message("Invalid message ID")
            await message.edit(view=submit_button)

        await interaction.response.send_message("Sent!", ephemeral=True)

    @CTS.command(
        name="edit_modal",
        description="Edit a pre-configured ticket's questions.",
    )
    @app_commands.describe(
        configuration_id="The configuration ID that corresponds to the button.",
        edit_mode="Edit Questions: Edit the questions itself, Edit Attributes: Edit the attributes (e.g. min length)"
    )
    @slash_is_bot_admin()
    async def edit_modal(
        self,
        interaction: discord.Interaction,
        configuration_id: int,
        edit_mode: Literal["Edit Questions", "Edit Attributes"],
    ):
        """
        Edit a pre-configured ticket button

        configuration_id: The configuration ID that corresponds to the button
        """
        query = database.TicketConfiguration.select().where(
            database.TicketConfiguration.id == configuration_id
        )
        if not query.exists():
            return await interaction.response.send_message("Invalid configuration ID")
        query = query.get()

        questions = text_to_list(query.questions)
        if edit_mode == "Edit Questions":

            class QuestionEdit(ui.Modal, title=query.title):
                def __init__(self, bot: commands.Bot):
                    super().__init__(timeout=None)
                    self.bot = bot
                    self.title = query.title
                    self.questions = questions
                    self.conf_id = query.id

                    self.question_obj: List[ui.TextInput] = []
                    self.answers = []
                    self.create_ui_elements()

                def create_ui_elements(self):
                    """cache_list = []
                    for elem in self.questions:
                        cache_list.append(elem.strip("'"))
                    self.questions = cache_list"""
                    index = 1

                    for question_e in self.questions:
                        text_input = ui.TextInput(
                            label=f"Question {index}",
                            required=True,
                            style=discord.TextStyle.long,
                            max_length=45,
                            placeholder=question_e,
                        )
                        self.add_item(text_input)
                        self.question_obj.append(text_input)
                        index += 1

                async def on_submit(self, interaction_i: discord.Interaction):
                    for question in self.question_obj:
                        self.answers.append(question.value)

                    # Update the database with new questions
                    query.questions = self.answers
                    query.save()

                    await interaction_i.response.send_message("Updated Questions!")

            modal = QuestionEdit(self.bot)
            await interaction.response.send_modal(modal)

        elif edit_mode == "Edit Question Attributes":

            class QuestionAttributesEdit(ui.Modal, title=query.title):
                def __init__(self, bot: commands.Bot):
                    super().__init__(timeout=None)
                    self.bot = bot
                    self.title = query.title
                    self.questions = questions
                    self.conf_id = query.id

                    self.question_obj: List[ui.TextInput] = []
                    self.answers = []
                    self.create_ui_elements()

                def create_ui_elements(self):
                    """cache_list = []
                    for elem in self.questions:
                        cache_list.append(elem.strip("'"))
                    self.questions = cache_list"""

                    for question_e in self.questions:
                        text_input = ui.TextInput(
                            label=question_e,
                            required=True,
                            style=discord.TextStyle.short,
                            max_length=75,
                            placeholder="S/L, Char. Limit Min, Char. Limit Max",
                        )
                        self.add_item(text_input)
                        self.question_obj.append(text_input)

                async def on_submit(self, interaction_i: discord.Interaction):
                    index = 1
                    for question in self.question_obj:
                        self.answers.append(question.value)
                        if index == 1:
                            query.q1_config = question.value
                        elif index == 2:
                            query.q2_config = question.value
                        elif index == 3:
                            query.q3_config = question.value
                        elif index == 4:
                            query.q4_config = question.value
                        elif index == 5:
                            query.q5_config = question.value
                        query.save()
                        index += 1

                    await interaction_i.response.send_message(
                        "Updated Question Configs!"
                    )

            modal = QuestionAttributesEdit(self.bot)
            await interaction.response.send_modal(modal)

    @CTS.command(
        name="edit_config",
        description="Edit a pre-configured ticket's config.",
    )
    @app_commands.describe(
        configuration_id="The configuration ID that corresponds to the button.",
        element="Edit the element. See here for more: https://ssimpl.org/cts-docs",
        value="The new value for the element.",
    )
    @slash_is_bot_admin()
    async def edit_modal(
        self,
        interaction: discord.Interaction,
        configuration_id: int,
        element: Literal[
            "title",
            "channel_identifier",
            "button_label",
            "category_id",
            "start_channel",
            "transcript_channel",
            "role_id",
            "limit",
        ],
        value: str,
    ):
        """
        Edit a pre-configured ticket button

        configuration_id: The configuration ID that corresponds to the button
        """
        query = database.TicketConfiguration.select().where(
            database.TicketConfiguration.id == configuration_id
        )
        if not query.exists():
            return await interaction.response.send_message("Invalid configuration ID")
        query = query.get()

        if element == "title":
            query.title = value
        elif element == "channel_identifier":
            query.channel_identifier = value
        elif element == "button_label":
            query.button_label = value
        elif element == "category_id":
            try:
                value = int(value)
            except:
                return await interaction.response.send_message("Invalid category ID")
            query.category_id = value
        elif element == "start_channel":
            try:
                value = int(value)
            except:
                return await interaction.response.send_message("Invalid channel ID")
            query.start_channel = value
        elif element == "transcript_channel":
            try:
                value = int(value)
            except:
                return await interaction.response.send_message("Invalid channel ID")
            query.transcript_channel = value
        elif element == "role_id":
            query.role_id = value
        elif element == "limit":
            try:
                value = int(value)
            except:
                return await interaction.response.send_message("Invalid limit")
            query.limit = value
        else:
            return await interaction.response.send_message("Invalid element")
        query.save()

        await interaction.response.send_message(f"Updated field {element} to {value}")

    @CTS.command(
        name="useradd",
        description="Adds a user to your ticket.",
    )
    @app_commands.describe(
        user="The person to add."
    )
    async def add_user(self, interaction: discord.Interaction, user: discord.Member):
        channel: discord.TextChannel = interaction.channel
        category = channel.category

        query = database.TicketConfiguration.select().where(
            database.TicketConfiguration.category_id == category.id
        )
        if not query.exists() and channel.category.id not in self.whitelisted_cat:
            return await interaction.response.send_message("This channel does not seem to be a ticket.")

        await channel.set_permissions(
            user,
            read_messages=True,
            send_messages=True,
        )
        await interaction.response.send_message(
            f"{interaction.user.mention}\n> **{user.mention}** has been added to the ticket!"
        )

    @CTS.command(
        name="userremove",
        description="Removes a user to your ticket.",
    )
    @app_commands.describe(
        user="The person to remove."
    )
    async def remove_user(self, interaction: discord.Interaction, user: discord.Member):
        channel: discord.TextChannel = interaction.channel
        category = channel.category

        query = database.TicketConfiguration.select().where(
            database.TicketConfiguration.category_id == category.id
        )
        if not query.exists() and channel.category.id not in self.whitelisted_cat:
            return await interaction.response.send_message("This channel does not seem to be a ticket.")

        await channel.set_permissions(
            user,
            read_messages=False,
            send_messages=False,
        )
        await interaction.response.send_message(
            f"{interaction.user.mention}\n> **{user.mention}** has been removed from the ticket!"
        )

    @CTS.command(
        name="rename",
        description="Rename a ticket channel.",
    )
    @app_commands.describe(
        name="The new name for the ticket channel."
    )
    async def rename_channel(self, interaction: discord.Interaction, name: str):
        channel: discord.TextChannel = interaction.channel
        old_name = channel.name
        category = channel.category

        query = database.TicketConfiguration.select().where(
            database.TicketConfiguration.category_id == category.id
        )
        if not query.exists():
            return await interaction.response.send_message("This channel does not seem to be a ticket.")
        await channel.edit(name=name, reason="Renamed by {}".format(interaction.user.name))
        await interaction.response.send_message(f"{interaction.user.mention} **Renamed channel!**\n> `{old_name}` -> `{name}`")


async def setup(bot: commands.Bot):
    await bot.add_cog(MGMTickets(bot))
