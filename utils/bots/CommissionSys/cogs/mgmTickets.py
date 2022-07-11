from datetime import datetime

import discord
from discord import ui, app_commands
from discord.ext import commands

from core import database
from core.checks import is_botAdmin
from core.common import Emoji, MGMCommissionButton, EmailDropdown, create_ui_modal_class, \
    create_ticket_button, TechID, StaffID


class QuestionInput(ui.Modal, title="Submit Questions here!"):
    def __init__(self, bot: commands.Bot, title: str, channel_name: str, button_label: str, category_id: int, channel_id: int, transcript_channel: int, role_id: str, limit: int = None) -> None:
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
        placeholder="Leave blank if you don't want to use this question or leave everything blank for no questions!"
    )
    second_question = ui.TextInput(
        label="Question Two:",
        style=discord.TextStyle.short,
        max_length=45,
        min_length=5,
        required=False,
        placeholder="Leave blank if you don't want to use this question or leave everything blank for no questions!"
    )
    third_question = ui.TextInput(
        label="Question Three:",
        style=discord.TextStyle.short,
        max_length=45,
        min_length=5,
        required=False,
        placeholder="Leave blank if you don't want to use this question or leave everything blank for no questions!"
    )
    fourth_question = ui.TextInput(
        label="Question Four:",
        style=discord.TextStyle.short,
        max_length=45,
        min_length=5,
        required=False,
        placeholder="Leave blank if you don't want to use this question or leave everything blank for no questions!"
    )
    fifth_question = ui.TextInput(
        label="Question Five:",
        style=discord.TextStyle.short,
        max_length=45,
        min_length=5,
        required=False,
        placeholder="Leave blank if you don't want to use this question or leave everything blank for no questions!"
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.limit is None:
            limit = 0
        if self.first_question.value == "" and self.second_question.value == "" and self.third_question.value == "" and self.fourth_question.value == "" and self.fifth_question.value == "":
            questions = []
        else:
            questions = [self.first_question.value, self.second_question.value, self.third_question.value, self.fourth_question.value, self.fifth_question.value]
            questions = list(filter(None, questions))

        query = database.TicketConfiguration.select().where(database.TicketConfiguration.category_id == self.category_id)
        if query.exists():
            return await interaction.response.send_message("Tickets already setup in this category, delete the category and create a new one "
                                  "if you wish to re-configure this config!!.")
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
                button_label=self.button_label
            )
            query.save()

            UIModal = create_ui_modal_class(query.id)
            modal = UIModal(self.bot, self.title, query.questions, query.id)

            GlobalSubmitButton = create_ticket_button(query.id)
            submit_button = GlobalSubmitButton(modal)

            ticket_start_channel: discord.TextChannel = self.bot.get_channel(query.channel_id)
            await ticket_start_channel.send(
             "** **", view=submit_button
            )

            # Send a final output of everything in an embed
            embed = discord.Embed(
                title="Successfully Created Ticket Configuration",
                description=f"{interaction.user.mention} has created a ticket configuration for {ticket_start_channel.mention}",
                color=discord.Colour.brand_green(),
            )
            embed.add_field(name="Instructions", value=f"This configuration has been setup and your requested button "
                                                       f"has been sent the start channel you provided in the command. "
                                                       f"If you wish to re-send the button for any reason, "
                                                       f"please use the following ID: {query.id} with /send_button.",
                            inline=False)
            embed.add_field(name="Title", value=query.title, inline=False)
            embed.add_field(name="Channel Identifier", value=query.channel_identifier, inline=False)
            embed.add_field(name="Category", value=query.category_id, inline=False)
            embed.add_field(name="Guild", value=query.guild_id, inline=False)
            embed.add_field(name="Limit", value=query.limit, inline=False)
            embed.add_field(name="Roles", value=query.role_id, inline=False)
            embed.add_field(name="Questions", value=query.questions, inline=False)

            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.avatar.url,
            )
            embed.set_footer(
                text=f"ID: {query.id}"
            )
            await interaction.response.send_message(embed=embed)




class MGMTickets(commands.Cog):
    """
    Commands for bot commissions
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.__cog_name__ = "MGM Commissions"
        #self.autoUnarchiveThread.start()

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

    @app_commands.command(
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
    @app_commands.guilds(
        discord.Object(TechID.g_tech), discord.Object(StaffID.g_staff_resources)
    )
    @is_botAdmin
    async def setup_tickets(
            self,
            interaction: discord.Interaction,
            title: str,
            channel_identifier: str,
            button_label: str,
            category_id: str,
            start_channel: discord.TextChannel,
            transcript_channel: discord.TextChannel,
            role_id: str,
            limit: int = 0
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

        await interaction.response.send_modal(QuestionInput(
            self.bot,
            title,
            channel_identifier,
            button_label,
            int(category_id),
            start_channel.id,
            transcript_channel.id,
            role_id,
            limit
        ))

    @app_commands.command(
        name="send_button",
        description="Send a pre-configured ticket button",
    )
    @app_commands.guilds(
        discord.Object(TechID.g_tech), discord.Object(StaffID.g_staff_resources)
    )
    @app_commands.describe(
        configuration_id="The configuration ID that corresponds to the button.",
        channel="Where the button will be sent; leave blank to send it to the channel it was configured with.",
    )
    @is_botAdmin
    async def send_button(self, interaction: discord.Interaction, configuration_id: int, channel: discord.TextChannel = None):
        """
        Send a pre-configured ticket button

        configuration_id: The configuration ID that corresponds to the button
        channel: Where the button will be sent
        """
        query = database.TicketConfiguration.select().where(database.TicketConfiguration.id == configuration_id)
        if not query.exists():
            return await interaction.response.send_message("Invalid configuration ID")
        query = query.get()

        UIModal = create_ui_modal_class(query.id)
        modal = UIModal(self.bot, query.title, query.questions, query.id)

        UIButton = create_ticket_button(query.id)
        submit_button = UIButton(modal)

        if channel is None:
            ticket_start_channel = self.bot.get_channel(query.channel_id)
        else:
            ticket_start_channel = channel

        await interaction.response.send_message("Sent!", ephemeral=True)

        await ticket_start_channel.send(
            "** **", view=submit_button
        )




async def setup(bot: commands.Bot):
    await bot.add_cog(MGMTickets(bot))
