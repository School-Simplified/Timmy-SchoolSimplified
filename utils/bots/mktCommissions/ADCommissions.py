import discord
from core.checks import is_botAdmin3
from discord.ext import commands, tasks
from core.common import SelectMenuHandler, TempConfirm, LockButton, TECH_ID, Emoji
from core.checks import is_botAdmin
from core import database

"Everyone needs to make advertisements at some point and every SBU/department has access to using corporate marketing’s resources!\n\n",
":white_check_mark: Note:",
":barrow~3: Marketing has final say regarding where and how something is promoted.",
":barrow~3: The release of an advertisement will be decided by Marketing and will be dependent on the urgency of the request.",
":barrow~3: The Marketing Team has the right to cancel and ignore any commissions if deemed appropriate.\n\n",
":camera_with_flash:  How To Get Started:",
":barrow~3: Click the button below!",
":barrow~3: Please make sure you are authorized to make commissions! ",


class AD_MDL_1(discord.ui.Modal):
    def __init__(self, bot) -> None:
        super().__init__("Advertisement Request")
        self.bot = bot

        self.add_item(
            discord.ui.InputText(
                label="What is a descriptive title for your request?",
                style=discord.InputTextStyle.short,
                max_length=1024,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="How critical is your request?",
                style=discord.InputTextStyle.short,
                placeholder="How urgent and how imperative is it",
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Which team is this request for?",
                style=discord.InputTextStyle.short,
                max_length=1024,
                placeholder="Include BOTH the Team and Department/Program",
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Write a brief description about your request",
                style=discord.InputTextStyle.long,
                max_length=1024,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="What are you hoping to gain from this ad?",
                style=discord.InputTextStyle.long,
                required=True,
                max_length=1024,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="{} Request", color=discord.Color.blurple()
        )
        embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.avatar.url
        )

        embed.add_field(
            name="Project Title", value=self.children[0].value, inline=False
        )
        embed.add_field(
            name="Critcal Status", value=self.children[1].value, inline=False
        )
        embed.add_field(
            name="Team Requester", value=self.children[2].value, inline=False
        )
        embed.add_field(
            name="Project Description", value=self.children[3].value, inline=False
        )
        embed.add_field(name="End Goal", value=self.children[4].value, inline=False)

        embed.set_footer(text="Advertisement Commission")

        c_ch: discord.TextChannel = await self.bot.fetch_channel(945757098686414858)
        msg: discord.Message = await c_ch.send(interaction.user.mention, embed=embed)
        thread = await msg.create_thread(name=self.children[0].value)
        await thread.send(interaction.user.mention)
        await thread.send(f"requested a Advertisement project <@589275602343952414>!")
        await interaction.response.send_message(
            content=f"Got it! Please proceed to <#{thread.id}> to continue on this request.",
            ephemeral=True,
        )


class CommissionADButton(discord.ui.View):
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
        modal = AD_MDL_1(self.bot)
        return await interaction.response.send_modal(modal)


class MKTProject2(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @is_botAdmin
    async def mktembedc2(self, ctx):
        view = CommissionADButton(self.bot)
        await ctx.send(
            "https://cdn.discordapp.com/attachments/892290621249847406/945506790253158440/Copy_of_Multiuse_Banner_1.png"
        )
        await ctx.send(
            "Everyone needs to make advertisements at some point and every SBU/department has access to using corporate marketing’s resources!\n\n**✅ Note:**\n<:barrow:896096260396814377> Marketing has final say regarding where and how something is promoted.\n<:barrow:896096260396814377> The release of an advertisement will be decided by Marketing and will be dependent on the urgency of the request.\n<:barrow:896096260396814377> The Marketing Team has the right to cancel and ignore any commissions if deemed appropriate. \n\n\n\n**📸  How To Get Started:**\n<:barrow:896096260396814377> Click the button below!\n<:barrow:896096260396814377> Please make sure you are authorized to make commissions!",
            view=view,
        )

    @commands.command()
    # @commands.has_role(945533984740343859)
    async def closemkt(self, ctx: commands.Context):
        thread: discord.Thread = ctx.channel
        if thread.parent_id == 945757098686414858:
            messages = await thread.history(limit=2, oldest_first=True).flatten()
            msg = messages[1]
            var = msg.content
            var = (
                var.replace("<", "").replace("@", "").replace(">", "").replace("!", "")
            )
            member = await self.bot.fetch_user(int(var))
            await member.send(
                "Your request has been closed, please contact Marketing for any questions."
            )
            await ctx.send("Closed!")
            await thread.archive(locked=True)


def setup(bot):
    bot.add_cog(MKTProject2(bot))
