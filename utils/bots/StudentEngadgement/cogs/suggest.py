from discord.app_commands import Group, command
import discord
from typing import List, Literal, Dict, Union
from core.common import MAIN_ID, SET_ID
from discord.ext import commands
from set import spammer_check


class Suggest(commands.Cog, Group):
    def __init__(
            self,
            bot: commands.Bot
    ):
        super().__init__(
            name="suggest",
            description="Suggest something for community engagement!",
            guild_ids=[MAIN_ID.g_main]
        )
        self.bot = bot

    @command(name="book")
    @spammer_check()
    async def __book(self, interaction: discord.Interaction):
        """Make a book suggestion!"""
        await interaction.response.send_modal(SuggestModal(self.bot, "Book"))

    @command(name="movie")
    @spammer_check()
    async def __movie(self, interaction: discord.Interaction):
        """Make a movie suggestion!"""
        await interaction.response.send_modal(SuggestModal(self.bot, "Movie"))

    @command(name="tv_show")
    @spammer_check()
    async def __tv_show(self, interaction: discord.Interaction):
        """Make a TV show suggestion!"""
        await interaction.response.send_modal(SuggestModal(self.bot, "TV Show"))

    @command(name="meme")
    @spammer_check()
    async def __meme(self, interaction: discord.Interaction):
        """Make a meme suggestion!"""
        await interaction.response.send_modal(SuggestModal(self.bot, "Meme"))

    @command(name="pickup_line")
    @spammer_check()
    async def __pickup_line(self, interaction: discord.Interaction):
        """Make a pickup line suggestion!"""
        await interaction.response.send_modal(SuggestModal(self.bot, "Pickup Line"))

    @command(name="puzzle")
    @spammer_check()
    async def __puzzle(self, interaction: discord.Interaction):
        """Make a suggestion for the weekly puzzle!"""
        await interaction.response.send_modal(SuggestModal(self.bot, "Puzzle"))

    @command(name="daily_question")
    @spammer_check()
    async def __daily_question(self, interaction: discord.Interaction):
        """Make a suggestion for the daily question!"""
        await interaction.response.send_modal(SuggestModal(self.bot, "Daily Question"))

    @command(name="motivation")
    @spammer_check()
    async def __motivation(self, interaction: discord.Interaction):
        """Make a motivation suggestion!"""
        await interaction.response.send_modal(SuggestModal(self.bot, "Motivation"))

    @command(name="music")
    @spammer_check()
    async def __motivation(self, interaction: discord.Interaction):
        """Make a music suggestion!"""
        await interaction.response.send_modal(SuggestModal(self.bot, "Music"))

    @command(name="art")
    @spammer_check()
    async def __art(self, interaction: discord.Interaction, art: discord.Attachment):
        """Make an art appreciation suggestion!"""
        await interaction.response.send_message("Submitted!")
        embed = discord.Embed(
            title="Art Appreciation Suggestion",
            timestamp=discord.utils.utcnow(),
            color=discord.Color.blurple()
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.set_image(url=art.url)
        channel = self.bot.get_channel(SET_ID.ch_suggestions)
        await channel.send(embed=embed)


class SuggestModal(discord.ui.Modal):
    def __init__(
            self,
            bot: commands.Bot,
            suggest_type: Literal[
                "Book",
                "Movie",
                "TV Show",
                "Meme",
                "Pickup Line",
                "Puzzle",
                "Daily Question",
                "Motivation",
                "Music"
            ]
    ):
        super().__init__(
            timeout=None,
            title=suggest_type + " Suggestion"
        )
        self.type = suggest_type
        self.bot = bot
        self.book_question_list: List[Dict[str, Union[str, bool, None]]] = [
            {
                "question": "Which book are you recommending?",
                "placeholder": None,
                "required": True
            },
            {
                "question": "What rating does this book have?",
                "placeholder": None,
                "required": True
            },
            {
                "question": "Give a short description of the book with no spoilers.",
                "placeholder": None,
                "required": True
            },
            {
                "question": "Why do you want to recommend this book?",
                "placeholder": None,
                "required": False
            },
        ]
        self.movie_question_list: List[Dict[str, Union[str, bool, None]]] = [
            {
                "question": "Which movie are you recommending?",
                "placeholder": None,
                "required": True
            },
            {
                "question": "What genre is it?",
                "placeholder": None,
                "required": True
            },
            {
                "question": "What rating does this movie have? If you aren't sure, give your best guess.",
                "placeholder": "Examples: TV-G or TV-PG",
                "required": True
            },
            {
                "question": "Give a short description of the movie with no spoilers",
                "placeholder": None,
                "required": True
            },
            {
                "question": "Why do you want to recommend this movie?",
                "placeholder": "This is an optional question, so if you would like to tell people why you liked this "
                               "movie (with no spoilers!) then feel free to write why you would recommend it!",
                "required": False
            },
        ]
        self.tv_question_list: List[Dict[str, Union[str, bool, None]]] = [
            {
                "question": "Which TV show are you recommending?",
                "placeholder": None,
                "required": True
            },
            {
                "question": "What genre is it?",
                "placeholder": None,
                "required": True
            },
            {
                "question": "What rating does this show have? If you aren't sure, give your best guess.",
                "placeholder": "Examples: TV-G or TV-PG",
                "required": True
            },
            {
                "question": "Give a short description of the show with no spoilers",
                "placeholder": None,
                "required": True
            },
            {
                "question": "Why do you want to recommend this show?",
                "placeholder": "This is an optional question, so if you would like to tell people why you liked this "
                               "show (with no spoilers!) then feel free to write why you would recommend it!",
                "required": False
            },
        ]
        self.meme_question_list: List[Dict[str, Union[str, bool, None]]] = [
            {
                "question": "Upload your meme here. Make sure it is appropriate and follows both School Simplified "
                            "rules and Discord TOS.",
                "placeholder": "You can link the file, link a Google Doc with the image, or use any other method that "
                               "works for you.",
                "required": True
            },
        ]
        self.pickup_question_list: List[Dict[str, Union[str, bool, None]]] = [
            {
                "question": "Type your pickup line here. Make sure it is appropriate and follows both School "
                            "Simplified rules and Discord TOS.",
                "placeholder": None,
                "required": True
            },
        ]
        self.puzzle_question_list: List[Dict[str, Union[str, bool, None]]] = [
            {
                "question": "What puzzle are you suggesting?",
                "placeholder": None,
                "required": True
            },
            {
                "question": "Include the solution steps needed to solve",
                "placeholder": None,
                "required": True
            },
        ]
        self.daily_q_question_list: List[Dict[str, Union[str, bool, None]]] = [
            {
                "question": "What question are you suggesting?",
                "placeholder": "Questions should be thoughtful and not shallow.",
                "required": True
            },
        ]
        self.motivation_question_list: List[Dict[str, Union[str, bool, None]]] = [
            {
                "question": "What quote are you suggesting? Make sure to include who said it.",
                "placeholder": None,
                "required": True
            },
            {
                "question": "If you have an interpretation/explanation of the quote, type it below!",
                "placeholder": None,
                "required": False
            },
        ]
        self.music_question_list: List[Dict[str, Union[str, bool, None]]] = [
            {
                "question": "What song are you recommending? Give the artist(s) as well.",
                "placeholder": None,
                "required": True
            },
            {
                "question": "What genre of music are you recommending?",
                "placeholder": None,
                "required": True
            },
            {
                "question": "Do you have any playlist name ideas?",
                "placeholder": "Do you have any playlist name ideas?",
                "required": False
            },
        ]
        self.type_to_questions_list: Dict[str, List[Dict[str, Union[bool, str, None]]]] = {
            "Book": self.book_question_list,
            "Movie": self.movie_question_list,
            "TV Show": self.tv_question_list,
            "Meme": self.meme_question_list,
            "Pickup Line": self.pickup_question_list,
            "Puzzle": self.puzzle_question_list,
            "Daily Question": self.daily_q_question_list,
            "Motivation": self.motivation_question_list,
            "Music": self.music_question_list
        }
        for question in self.type_to_questions_list[self.type]:
            self.add_item(
                discord.ui.TextInput(
                    label=question["question"],
                    required=question["required"],
                    placeholder=question["placeholder"] if question["placeholder"] else None,
                    max_length=1024,
                    style=discord.TextStyle.paragraph,
                    custom_id="suggestion_modal"
                )
            )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Submitted!")
        embed = discord.Embed(
            title=self.type + " Suggestion",
            timestamp=discord.utils.utcnow(),
            color=discord.Color.blurple()
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)

        for item, question in zip(
                [item for item in self.children if isinstance(item, discord.TextInput)],
                self.type_to_questions_list[self.type]
        ):
            embed.add_field(
                name=question["question"],
                value=item.value if item.value else "None"
            )

        channel = self.bot.get_channel(SET_ID.ch_suggestions)
        await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Suggest(bot))
