import discord
from core.checks import is_botAdmin3
from discord.ext import commands, tasks
from core.common import SelectMenuHandler, TempConfirm, LockButton, TECH_ID, Emoji
from core.checks import is_botAdmin
from core import database

class BotRequestModal(discord.ui.Modal):
    def __init__(self, bot) -> None:
        super().__init__("Bot Development Request")
        self.bot = bot

        self.add_item(
            discord.ui.InputText(
                label="What is a descriptive title for your project?",
                style=discord.InputTextStyle.long,
                max_length=1024,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Which team is this project for?",
                style=discord.InputTextStyle.short,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Write a brief description of the project.",
                style=discord.InputTextStyle.long,
                max_length=1024,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Do you have approval for this commission?",
                style=discord.InputTextStyle.long,
                max_length=1024,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Anything else?",
                style=discord.InputTextStyle.long,
                required=False,
                max_length=1024,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="Got it! Please wait while I create your ticket.", ephemeral=True
        )

        embed = discord.Embed(
            title="Bot Developer Commission", color=discord.Color.blurple()
        )
        embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.avatar.url
        )
        embed.add_field(
            name="Project Title", value=self.children[0].value, inline=False
        )
        embed.add_field(
            name="Team Requester", value=self.children[1].value, inline=False
        )
        embed.add_field(
            name="Project Description", value=self.children[2].value, inline=False
        )
        embed.add_field(name="Approval", value=self.children[3].value, inline=False)
        embed.add_field(
            name="Anything else?", value=self.children[4].value, inline=False
        )
        embed.set_footer(text="Bot Developer Commission")

        c_ch: discord.TextChannel = await self.bot.fetch_channel(933181562885914724)
        msg: discord.Message = await c_ch.send(interaction.user.mention, embed=embed)
        thread = await msg.create_thread(name=self.children[0].value)

        await thread.send(
            f"{interaction.user.mention} has requested a bot development project.\n<@&{TECH_ID.r_botDeveloper}>"
        )


class CommissionTechButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Start Commission",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:mkt_ad_commission_start",
        emoji="📝",
    )
    async def verify(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = BotRequestModal(self.bot)
        return await interaction.response.send_modal(modal)


class MKTProject(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @is_botAdmin
    async def mktembedc(self, ctx):
        embed = discord.Embed(
            title="Bot Developer Commissions", color=discord.Color.green()
        )
        embed.add_field(
            name="Get Started",
            value="To get started, click the button below!\n*Please make sure you are authorized to make commissions!*",
        )
        embed.set_footer(
            text="The Bot Development Team has the right to cancel and ignore any commissions if deemed appropriate. "
            "We also have the right to cancel and ignore any commissions if an improper deadline is given, "
            "please make sure you create a commission ahead of time and not right before a due date",
        )
        view = CommissionTechButton(self.bot)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    async def closethreadmkt(self, ctx: commands.Context):
        channel: discord.TextChannel = await self.bot.fetch_channel(TECH_ID.ch_botreq)
        thread: discord.Thread = ctx.channel
        if thread in channel.threads:
            await ctx.send("Closed thread!")
            query = database.TechCommissionArchiveLog.create(ThreadID = thread.id)
            query.save()
            thread.archive()
        else:
            await ctx.send("Not a valid thread.")



def setup(bot):
    bot.add_cog(MKTProject(bot))
