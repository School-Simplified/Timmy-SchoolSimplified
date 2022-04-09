from __future__ import annotations
from typing import Dict, List, Literal, TYPE_CHECKING, Union

import discord
from github import Github
from discord.ext import commands
from discord.app_commands import command

if TYPE_CHECKING:
    from main import Timmy

QuestionListType = List[Dict[str, Union[bool, str, None]]]
GithubActionLiteral = Literal["ISSUE", ]


class GithubControlModal(discord.ui.Modal):
    def __init__(self, bot: 'Timmy'):
        super().__init__(timeout=None)
        self.bot = bot
        self.issue_list: QuestionListType = [
            {
                "title": "Issue Title",
                "required": True,
                "placeholder": None
            },
            {
                "title": "Issue Summary",
                "required": True,
                "placeholder": "A simple summary of your bug report"
            },
            {
                "title": "Reproducible Steps",
                "required": True,
                "placeholder": "What you did to make it happen."
            },
            {
                "title": "Expected Results",
                "required": True,
                "placeholder": "What did you expect to happen?"
            },
            {
                "title": "Actual Results",
                "required": True,
                "placeholder": "What actually happened?"
            },
            {
                "title": "Location",
                "required": True,
                "placeholder": "Server + Channel name"
            },
            {
                "title": "Additional Context",
                "required": False,
                "placeholder": "If there is anything else to say, please do so here."
            },
        ]

    def transform(self, _type: GithubActionLiteral) -> QuestionListType:
        transformer_dict: Dict[GithubActionLiteral, QuestionListType] = {
            "ISSUE": self.issue_list
        }
        return transformer_dict[_type]


class GithubCommands(commands.Cog):
    def __init__(self, bot: 'Timmy'):
        self.bot = bot
        self._github_client = Github()

    @command(name="open-issue")
    async def __issue(
            self,
            interaction: discord.Interaction,
            feature: Literal["Command", "Slash Command", "Dropdown or Button", "Other"],
            screenshot: discord.Attachment
    ):
        ...
