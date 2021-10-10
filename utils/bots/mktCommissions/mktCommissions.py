import asyncio
import random
import string
import discord
from discord.ext import commands
from discord import ButtonStyle

from core.common import Emoji, hexColors, ButtonHandler, SelectMenuHandler, MKT_ID, Others
from core.checks import is_mktCommissionAuthorized


# end imports


async def lockButton(interaction: discord.Interaction, view: discord.ui.View):
    """
    Continuing code after lock button.
    """
    viewCheck = discord.ui.View()
    viewCheck.add_item(ButtonHandler(style=ButtonStyle.green, label="Confirm", custom_id="Confirm",
                                     emoji=Emoji.confirm, button_user=interaction.user))
    viewCheck.add_item(ButtonHandler(style=ButtonStyle.red, label="Cancel", custom_id="Cancel",
                                     emoji=Emoji.confirm, button_user=interaction.user,
                                     interaction_message="Canceled", ephemeral=True))
    embedCheck = discord.Embed(
        title="Check",
        description="Are you sure you want to close this commission?"
    )
    await interaction.response.send_message(embed=embedCheck, view=viewCheck, ephemeral=True)

    timeout = await viewCheck.wait()

    if not timeout:
        if viewCheck.value == "Confirm":
            await interaction.channel.delete()

        elif viewCheck.value == "Cancel":
            viewCheckDisabled = discord.ui.View()
            viewCheckDisabled.add_item(ButtonHandler(style=ButtonStyle.green, label="Confirm", emoji=Emoji.confirm,
                                                     disabled=True))
            viewCheckDisabled.add_item(ButtonHandler(style=ButtonStyle.red, label="Cancel", emoji=Emoji.confirm,
                                                     disabled=True))

            await interaction.edit_original_message(embed=embedCheck, view=viewCheckDisabled)


async def createCommissionChannel(
        ctx: commands.Context,
        bot: commands.Bot,
        category_str: str):
    """
    Creates a commission channel

    Parameters:
        ctx: The context of the command
        bot: The bot object
        category_str: The commission category
    """
    random_ID = "".join(random.choices(string.ascii_letters + string.digits, k=4))

    if category_str == "Design Commission":
        category = bot.get_channel(MKT_ID.mkt_designCategory)
        channelName = f"mktDesign-{random_ID}"
        teamMember = "Design Team Member"

    elif category_str == "Media Commission":
        category = bot.get_channel(MKT_ID.mkt_mediaCateogory)
        channelName = f"mktMedia-{random_ID}"
        teamMember = "Media Team Member"

    elif category_str == "Discord Commission":
        category = bot.get_channel(MKT_ID.mkt_discordCategory)
        channelName = f"mktDiscord-{random_ID}"
        teamMember = "Discord Editor"

    mkt_secretService = ctx.guild.get_role(MKT_ID.mkt_secretService)
    mkt_executiveAssistant = ctx.guild.get_role(MKT_ID.mkt_executiveAssistant)
    mkt_Director = ctx.guild.get_role(MKT_ID.mkt_Director)
    mkt_Manager = ctx.guild.get_role(MKT_ID.mkt_Manager)
    mkt_AssistantManager = ctx.guild.get_role(MKT_ID.mkt_executiveAssistant)

    perms = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
        mkt_secretService: discord.PermissionOverwrite(read_messages=True),
        mkt_executiveAssistant: discord.PermissionOverwrite(read_messages=True),
        mkt_Director: discord.PermissionOverwrite(read_messages=True),
        mkt_Manager: discord.PermissionOverwrite(read_messages=True),
        mkt_AssistantManager: discord.PermissionOverwrite(read_messages=True)
    }

    commissionChannel = await category.create_text_channel(name=channelName, overwrites=perms)
    return commissionChannel, teamMember


class mktCommissions(commands.Cog):
    """
    Marketing commissions system
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["mkt-setup"])
    async def mktsetup(self, ctx, channel: discord.TextChannel):
        """
        Sends the Marketing Commissions message into a specific channel.

        Parameters:
            channel: The specific channel in which the message should be sent in.
        """

        embedCheck = discord.Embed(
            color=hexColors.yellow,
            title="Check",
            description=f"Are you sure you want to send the commission setup into {channel.mention}?",
        )
        viewMain = discord.ui.View()
        viewMain.add_item(ButtonHandler(style=discord.ButtonStyle.green, label="Confirm", custom_id="Confirm",
                                        button_user=ctx.author, emoji=Emoji.confirm))
        viewMain.add_item(ButtonHandler(style=discord.ButtonStyle.red, label="Cancel", custom_id="Cancel",
                                        button_user=ctx.author, emoji=Emoji.deny))

        viewDisabled = discord.ui.View()
        viewDisabled.add_item(ButtonHandler(style=discord.ButtonStyle.green, label="Confirm", custom_id="Confirm",
                                            button_user=ctx.author, disabled=True, emoji=Emoji.confirm))
        viewDisabled.add_item(ButtonHandler(style=discord.ButtonStyle.red, label="Cancel", custom_id="Cancel",
                                            button_user=ctx.author, disabled=True, emoji=Emoji.deny))

        msg = await ctx.send(content="_ _", embed=embedCheck, view=viewMain)

        timeout = await viewMain.wait()
        if not timeout:

            if viewMain.value == "Confirm":
                embedConfirm = discord.Embed(
                    color=hexColors.green_confirm,
                    title="Check",
                    description=f"Setup have been send into {channel.mention} successfully."
                )
                await msg.edit(embed=embedConfirm, view=viewDisabled)

                embedSetup = discord.Embed(
                    color=hexColors.green_general,
                    title="Marketing Team Commissions",
                    description="**Creating a Commission Ticket**"
                                "\nIf you'd like to start a Marketing Commission, please fill out the form by running "
                                f"`+request` in <#{MKT_ID.mkt_commands}> and then follow the bot's instructions!"
                )
                embedSetup.set_author(name="Need to make a Marketing Commission? Read on!",
                                      icon_url="https://images-ext-2.discordapp.net/external/1P5y2JKHlIhS6fQuMiYOu7zB1Y8El-T9Bh7JJIMqSks/%3Fsize%3D1024/https/cdn.discordapp.com/icons/778406166735880202/ab248ec34ef53e5f5f209f191204a9a2.png")
                embedSetup.set_footer(text="If you have any questions, feel free to DM a Marketing Manager!")
                await channel.send(embed=embedSetup)

            elif viewMain.value == "Cancel":
                embedCancel = discord.Embed(
                    color=hexColors.red_cancel,
                    title="Check",
                    description="Setup canceled."
                )
                await msg.edit(embed=embedCancel, view=viewDisabled)
        else:
            embedTimeout = discord.Embed(
                color=hexColors.red_cancel,
                title="Check",
                description="Setup canceled due to timeout."
            )
            await msg.edit(embed=embedTimeout, view=viewDisabled)

    @commands.command(aliases=["mkt-request"])
    async def mktrequest(self, ctx: commands.Context):
        """
        To submit a Marketing Commission.
        """
        if ctx.channel.id == MKT_ID.mkt_commands:

            # Local variables
            category = None
            goal = None
            information = None
            dates = None
            approver = None
            finalDesicion = None
            anything_else = None

            question_1 = "Q1: Which of these categories does your project suggestion fit under?"
            question_2 = "Q2: What is the goal and purpose of this ticket?"
            question_3 = "Q3: Please provide some information regarding your commission."
            question_4 = "Q4: What is the expected deadline and any other important dates?"
            question_5 = "Q5: Who approved of it (if not a manager)?"
            question_6 = "Q6: Do you understand that the Marketing department will have the final decision " \
                         "in regards to commissions and that requests made under 2 weeks in advance from " \
                         "the needed deadline may not be completed on time?"
            question_7 = "Q7: Anything else?"

            embedDisclaimer = discord.Embed(
                color=hexColors.red_cancel,
                title="Reminders",
                description="1) You may suggest, but non marketing leadership will have **no power** making the final decision on where it is promoted."
                            "\n2) Your request may be declined at the discretion of marketing."
                            "\n3) Requests made **under 2 weeks** in advance may not be completed."
                            "\n4) **If you have any questions, DM a Marketing VP!**"
            )
            try:
                await ctx.author.send(embed=embedDisclaimer)
            except discord.Forbidden:
                await ctx.send(f"{ctx.author.mention} You have to enable your DMs in order to request a commission.")
                return

            await ctx.send(f"{ctx.author.mention} Check DMs!")

            designCommission = discord.SelectOption(
                label="Design Commission",
                description="If you need a new logo, design, illustration, etc. click here!",
                emoji="🎨"
            )
            mediaCommission = discord.SelectOption(
                label="Media Commission",
                description="If you need an advertisement, event, etc. click here!",
                emoji="📸"
            )
            discordCommission = discord.SelectOption(
                label="Discord Commission",
                description="If you need help with discord editing, click here!",
                emoji="💻"
            )

            options = [designCommission, mediaCommission, discordCommission]

            viewQuestion_1 = discord.ui.View(timeout=60)
            viewQuestion_1.add_item(SelectMenuHandler(options=options,
                                                      place_holder="Select a category that relates to your commission!",
                                                      select_user=ctx.author
                                                      ))
            viewDisabled = discord.ui.View()
            viewDisabled.add_item(SelectMenuHandler(options=options,
                                                    place_holder="Select a category that relates to your commission!",
                                                    select_user=ctx.author, disabled=True
                                                    ))

            embedQuestion_1 = discord.Embed(
                color=hexColors.yellow,
                title=question_1
            )
            try:
                msgQuestion_1 = await ctx.author.send(content="_ _", embed=embedQuestion_1, view=viewQuestion_1)
            except discord.Forbidden:
                return

            timeout = await viewQuestion_1.wait()
            if not timeout:
                category = viewQuestion_1.value

                embedQuestion_2 = discord.Embed(
                    color=hexColors.yellow,
                    title=question_2
                )
                try:
                    await ctx.author.send(embed=embedQuestion_2)
                except discord.Forbidden:
                    return

                def checkRequest(check_message: discord.Message):
                    return type(check_message.channel) == discord.DMChannel and check_message.author == ctx.author

                count = 0
                while True:
                    try:
                        message = await self.bot.wait_for('message', check=checkRequest, timeout=60)
                    except asyncio.TimeoutError:
                        embedTimeout = discord.Embed(
                            color=hexColors.red_cancel,
                            title="Timeout",
                            description="Request canceld due to timeout."
                        )
                        try:
                            await ctx.author.send(embed=embedTimeout)
                        except discord.Forbidden:
                            return

                        await msgQuestion_1.edit(embed=embedQuestion_1, view=viewDisabled)
                        return

                    else:
                        if count == 0:
                            goal = message.content

                            embedNextQuestion = discord.Embed(
                                color=hexColors.yellow,
                                title=question_3
                            )

                        elif count == 1:
                            information = message.content

                            embedNextQuestion = discord.Embed(
                                color=hexColors.yellow,
                                title=question_4
                            )

                        elif count == 2:
                            dates = message.content

                            embedNextQuestion = discord.Embed(
                                color=hexColors.yellow,
                                title=question_5
                            )

                        elif count == 3:
                            approver = message.content

                            embedNextQuestion = discord.Embed(
                                color=hexColors.yellow,
                                title=question_6
                            )

                        elif count == 4:
                            finalDesicion = message.content

                            embedNextQuestion = discord.Embed(
                                color=hexColors.yellow,
                                title=question_7
                            )

                        elif count == 5:
                            anything_else = message.content
                            break

                        count += 1
                        try:
                            await ctx.author.send(embed=embedNextQuestion)
                        except discord.Forbidden:
                            return

                embedCheck = discord.Embed(
                    color=hexColors.yellow,
                    title="Confirm Responses...",
                    description="Are you ready to submit these responses?"
                )
                viewCheck = discord.ui.View()
                viewCheck.add_item(ButtonHandler(style=ButtonStyle.green, label="Confirm", emoji=Emoji.confirm,
                                                 button_user=ctx.author, custom_id="Confirm"))

                viewCheck.add_item(ButtonHandler(style=ButtonStyle.red, label="Cancel",
                                                 emoji=Emoji.confirm, button_user=ctx.author,
                                                 interaction_message="Canceled", ephemeral=True, custom_id="Cancel"))
                try:
                    await ctx.author.send(content="_ _", embed=embedCheck, view=viewCheck)
                except discord.Forbidden:
                    return

                timeout = await viewCheck.wait()
                continueBool = False
                if not timeout:
                    if viewCheck.value == "Confirm":
                        continueBool = True

                if continueBool:
                    commissionChannel, teamMember = await createCommissionChannel(ctx=ctx, bot=self.bot,
                                                                                  category_str=category)
                    transcriptChannel = self.bot.get_channel(MKT_ID.mkt_commissionTranscripts)

                    try:
                        await ctx.author.send(
                            content="**Ticket Created!**"
                                    f"\n> Please use {commissionChannel.mention} if you wish to follow up on your commission!"
                        )
                    except discord.Forbidden:
                        pass

                    mkt_secretService = ctx.guild.get_role(MKT_ID.mkt_secretService)
                    mkt_executiveAssistant = ctx.guild.get_role(MKT_ID.mkt_executiveAssistant)
                    mkt_Director = ctx.guild.get_role(MKT_ID.mkt_Director)
                    mkt_Manager = ctx.guild.get_role(MKT_ID.mkt_Manager)
                    mkt_AssistantManager = ctx.guild.get_role(MKT_ID.mkt_executiveAssistant)

                    lockRoles = [mkt_secretService, mkt_executiveAssistant, mkt_Director, mkt_Manager,
                                 mkt_AssistantManager]

                    viewControlPanel = discord.ui.View(timeout=None)
                    viewControlPanel.add_item(
                        ButtonHandler(style=discord.ButtonStyle.green, label="Lock", custom_id="Lock",
                                      emoji="🔒", button_user=ctx.author, roles=lockRoles,
                                      coroutine=lockButton))
                    embedControlPanel = discord.Embed(
                        color=hexColors.yellow,
                        title="Control Panel",
                        description="To end this ticket, click the lock button!"
                    )
                    await commissionChannel.send(content="_ _", embed=embedControlPanel, view=viewControlPanel)

                    embedTicket = discord.Embed(
                        color=hexColors.green_general,
                        title="Marketing Ticket",
                        description=f"Welcome {ctx.author.mention}! A {teamMember} will be with you shortly."
                    )

                    embedRequest = discord.Embed(
                        color=hexColors.green_general,
                        title="New Project Request",
                        description=f"Project requested by {ctx.author.mention}"
                    )
                    embedRequest.add_field(name=question_1, value=category)
                    embedRequest.add_field(name=question_2, value=goal)
                    embedRequest.add_field(name=question_3, value=information)
                    embedRequest.add_field(name=question_4, value=dates)
                    embedRequest.add_field(name=question_5, value=approver)
                    embedRequest.add_field(name=question_6, value=finalDesicion)
                    embedRequest.add_field(name=question_7, value=anything_else)

                    await commissionChannel.send(embed=embedTicket)
                    await commissionChannel.send("Submitted Report:", embed=embedRequest)
                    await transcriptChannel.send(embed=embedRequest)


            else:
                embedTimeout = discord.Embed(
                    color=hexColors.red_cancel,
                    title="Timeout",
                    description="Request canceld due to timeout."
                )
                try:
                    await ctx.author.send(embed=embedTimeout)
                except discord.Forbidden:
                    return

                await msgQuestion_1.edit(embed=embedQuestion_1, view=viewDisabled)


    @commands.command(aliases=["mkt-add"])
    @is_mktCommissionAuthorized
    async def mktadd(self, ctx: commands.Context, member: discord.Member):
        """
        To add a user to a commission channel, who hasn't access to it.
        """
        if not ctx.channel.category or ctx.channel.category.id not in [MKT_ID.mkt_designCategory, MKT_ID.mkt_mediaCateogory, MKT_ID.mkt_discordCategory]:

            embedError = discord.Embed(
                title="Not allowed!",
                color=hexColors.red_error,
                description="You can't use this command in this channel!"
                            "\n\nPlease make sure you use this command in a commission channel."
            )
            embedError.set_thumbnail(url=Others.error_png)
            embedError.set_footer(text="Consult the Help Command if you are having trouble or call over a Bot Manager!")
            await ctx.send(embed=embedError)

        else:
            perms = ctx.channel.overwrites
            perms.update({member: discord.PermissionOverwrite(read_messages=True)})

            await ctx.channel.edit(overwrites=perms)

            embedSuccess = discord.Embed(
                title="Member added",
                color=hexColors.green_confirm,
                description=f"Successfully added {member.mention} to this commission."
            )
            await ctx.send(embed=embedSuccess)


def setup(bot):
    bot.add_cog(mktCommissions(bot))
