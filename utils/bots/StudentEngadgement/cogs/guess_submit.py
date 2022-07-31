from datetime import datetime

import discord
import pytz
from discord import app_commands, ui
from discord.ext import commands, tasks

from core import database
from core.common import MainID, Emoji, SETID


class GuessModal(ui.Modal, title="May Day Event Submission"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    guess = ui.TextInput(
        label="Submit your guess here!",
        style=discord.TextStyle.long,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"{interaction.user.mention}, I have submitted your guess!", ephemeral=True
        )
        ch: discord.TextChannel = self.bot.get_channel(SETID.ch_may_day_guess)
        embed = discord.Embed(
            color=0xC387FF,
            title="May Day Event Guess",
            description=self.guess.value,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        await ch.send(embed=embed)


class GuessSubmit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = [
            "Q: Hastings, England, has its own special festival on May Day known as what?",
            "Q: What piece of wood is vital to the May Day celebration?",
            "Q: Which of the following flowers are associated with May Day in France?",
            "Q: In traditional English May Day celebrations, what is the lady who personifies the ideals of the event?",
            "Q: Lei Day is what US State’s iteration of May Day?",
            "Q: Antarrashtriya Shramik Diwas is May Day in what country?",
            "Q: When was four year period when May Day celebrations were banned in the British Kingdom?",
            "Q: May Day was believed to bring what supernatural creature?",
            "Q: What would one wash their faces with on May Day to beautify their skin?",
            "Q: In which of the following countries is May Day considered the happiest day of the year?",
            "Q: May Day has nothing to do with the international call of distress, “mayday,” from what two French words does it come from?",
            "Q: What roman goddess was May Day celebrated for?",
            "Q: While originally a pagan festival, what does May Day now represent worldwide?",
            "Q: What is a festival often associated with May Day, but is not May Day?",
            "Q: Although the maypole dance was invented in Europe, similar dances could be found in pre-columbian __?",
        ]
        self.est = pytz.timezone("US/Eastern")
        self.__cog_name__ = "May Day Event"

    @property
    def display_emoji(self) -> str:
        return Emoji.date

    @app_commands.command(description="Submit your event guess here!")
    @app_commands.guilds(MainID.g_main)
    async def event_guess(self, interaction: discord.Interaction):
        await interaction.response.send_modal(GuessModal(self.bot))

    @tasks.loop(minutes=60.0)
    async def mayEventPost(self):
        now = datetime.now(self.est)
        TutorSession = pytz.timezone("America/New_York").localize(now)
        channel = self.bot.get_channel(MainID.ch_event_announcements)
        q = database.BaseQueue.select().where(database.BaseQueue.queueID == 2).get()
        if TutorSession.hour >= 7 and not q.queueID > 15:
            await channel.send(self.questions[q.queueID])
            q.queueID += 1
            q.save()


async def setup(bot: commands.Bot):
    await bot.add_cog(GuessSubmit(bot))
