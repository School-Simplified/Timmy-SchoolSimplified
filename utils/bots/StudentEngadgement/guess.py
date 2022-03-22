from typing import Dict, List, Literal, Union

import discord
from discord.ext import commands
from discord.app_commands import command, Group
from core.common import MAIN_ID


class Engagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="puzzle_guess",
        description="Submit a guess for the weekly puzzle!"
    )
    async def _guess(self, interaction: discord.Interaction, guess: str):
        embed = discord.Embed(
            color=0xc387ff,
            title="Puzzle Guess",
            description=f"```{guess}```",
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        ssd: discord.Guild = self.bot.get_guild(778406166735880202)
        guess_channel: discord.TextChannel = ssd.get_channel(950083341967843398)
        await guess_channel.send(embed=embed)
        await interaction.response.send_message("Your guess has been submitted!", ephemeral=True)


class Suggest(Group):
    def __init__(self):
        super().__init__(
            name="suggest",
            description="Suggest something for community engagement!",
            guild_ids=[MAIN_ID.g_main]
        )

    @command(name="book")
    async def __book(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SuggestModal("Book"))


class SuggestModal(discord.ui.Modal):
    def __init__(
            self,
            suggest_type: Literal["Media", "Book",]
    ):
        super().__init__(
            timeout=None,
            title=suggest_type + "Suggestion"
        )
        self.type = suggest_type
        self.book_question_list: List[Dict[str, Union[str, bool]]] = [
            {
                "question": "Which book are you recommending?",
                "required": True
            },
            {
                "question": "What rating does this book have?",
                "required": True
            },
            {
                "question": "Give a short description of the book with no spoilers.",
                "required": True
            },
            {
                "question": "Why do you want to recommend this book?",
                "required": False
            },
        ]

        self.type_to_questions_list = {
            "Book": self.book_question_list
        }
        for question in self.type_to_questions_list[self.type]:
            self.add_item(
                discord.ui.TextInput(
                    label=question["question"],
                    required=question["required"],
                    max_length=1024
                )
            )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Submitted!")
        embed = discord.Embed(

        )
        ...
        # idk what to do here, i want the embed field to be the question and the answer to be the field value


async def setup(bot: commands.Bot):
    await bot.add_cog(Engagement(bot))
    bot.tree.add_command(Suggest())
