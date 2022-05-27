from discord.ext import commands, tasks

from core.checks import is_botAdmin
from core.common import TechID, Emoji, StaffID, SelectMenuHandler, HRID, access_secret, ButtonHandler, \
    MGMCommissionButton, EmailDropdown


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

    """@app_commands.command()
    @app_commands.guilds(TechID.g_tech)
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.guild_id, i.channel.id))
    async def commission(
            self, interaction: discord.Interaction, action: Literal["close"]
    ):
        channel: discord.TextChannel = self.bot.get_channel(TechID.ch_bot_requests)
        thread = interaction.channel

        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message(
                "This is not a bot commission.", ephemeral=True
            )
            return

        if action == "close":
            query = database.TechCommissionArchiveLog.select().where(
                database.TechCommissionArchiveLog.ThreadID == thread.id
            )
            if thread not in channel.threads or query.exists():
                await interaction.response.send_message(
                    "This commission is already closed.", ephemeral=True
                )
                return
            else:
                query = database.TechCommissionArchiveLog.create(ThreadID=thread.id)
                query.save()

                await interaction.response.send_message(
                    "Commission closed! You can find the commission in the archived threads of that channel."
                )
                await thread.edit(archived=True)

    @commands.Cog.listener("on_message")
    async def auto_open_commission(self, message: discord.Message):
        channel: discord.TextChannel = self.bot.get_channel(TechID.ch_bot_requests)

        if (
                isinstance(message.channel, discord.Thread)
                and message.type == discord.MessageType.default
                and message.channel in channel.threads
        ):

            query = database.TechCommissionArchiveLog.select().where(
                database.TechCommissionArchiveLog.ThreadID == message.channel.id
            )
            if query.exists():
                result = query.get()
                result.delete_instance()

                await message.reply(content="Commission re-opened!")

    @tasks.loop(seconds=60.0)
    async def autoUnarchiveThread(self):

        channel: discord.TextChannel = self.bot.get_channel(TechID.ch_bot_requests)
        query = database.TechCommissionArchiveLog.select()
        closed_threads = [entry.ThreadID for entry in query]

        async for archived_thread in channel.archived_threads():
            if archived_thread.id not in closed_threads:
                await archived_thread.edit(archived=False)

    @autoUnarchiveThread.before_loop
    async def before_loop_(self):
        await self.bot.wait_until_ready()"""


async def setup(bot: commands.Bot):
    await bot.add_cog(MGMTickets(bot))
