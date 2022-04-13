from __future__ import annotations

import itertools
import os
from typing import Any, Dict, List, Literal, TYPE_CHECKING, Union, Optional

from discord import app_commands

from core.checks import slash_is_bot_admin_4
import discord
from github import Github
from discord.ext import commands
from discord.app_commands import command, Group, guilds

from core.common import TECH_ID

if TYPE_CHECKING:
    from main import Timmy

QuestionListType = List[Dict[str, Union[bool, str, None]]]
GithubActionLiteral = Literal["ISSUE",]
IssueFeatureLiteral = Literal["Command", "Slash Command", "Dropdown or Button", "Other"]


class GithubControlModal(discord.ui.Modal):
    def __init__(
            self,
            bot: Timmy,
            type_: GithubActionLiteral,
            feature: IssueFeatureLiteral,
            github_client: Github,
            attachment: Optional[discord.Attachment] = None,
            gist_url: Optional[str] = None,
    ):
        super().__init__(timeout=None, title="Create Issue")

        self.bot = bot
        self._type = type_
        self._feature_type = feature
        self._attachment = attachment.url if attachment else None
        self._gist_url = gist_url if gist_url else None
        self._gh_client = github_client
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
                "title": "Additional Context",
                "required": False,
                "placeholder": "If there is anything else to say, please do so here."
            },
        ]
        for item_blueprint in self.transform(self._type):
            self.add_item(
                discord.ui.TextInput(
                    label=item_blueprint["title"],
                    required=item_blueprint["required"],
                    placeholder=item_blueprint["placeholder"] if item_blueprint["placeholder"] else None,
                    max_length=1024,
                    style=discord.TextStyle.paragraph,
                )
            )

    def transform(self, _type: GithubActionLiteral) -> QuestionListType:
        transformer_dict: Dict[GithubActionLiteral, QuestionListType] = {
            "ISSUE": self.issue_list
        }
        return transformer_dict[_type]

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        repo = self._gh_client.get_repo("School-Simplified/Timmy-SchoolSimplified")

        embed = discord.Embed(title=f"{self._feature_type} Issue", colour=discord.Colour.brand_green())

        issue_body = ""

        for item, question in zip(self.children, self.transform(self._type)):
            embed.add_field(
                name=question["title"],
                value=str(item),
                inline=False
            )
            issue_body += f"**{question['title']}**\n{str(item)}\n\n"

        issue = repo.create_issue(
            title=str(self.children[0]),
            body=f"**Issue Feature**\n{self._feature_type}\n\n" + issue_body + self._attachment,
        )
        issue.add_to_labels(repo.get_label(name="Discord"))
        url = f"https://github.com/School-Simplified/Timmy-SchoolSimplified/issues/{issue.number}"
        embed.description = f"[Created Issue!]({url})"
        await interaction.followup.send(embed=embed)


class GithubIssues(Group):
    def __init__(
            self,
            bot: Timmy,
            github_client: Github,
    ):
        super().__init__(
            name="issue",
            description="Open an issue for a bug related to the bot"
        )
        self.bot = bot
        self._github_client = github_client

    @property
    def cog(self) -> commands.Cog:
        return self.bot.get_cog("Github")

    @command(name="open")
    async def __open(
            self,
            interaction: discord.Interaction,
            feature: IssueFeatureLiteral,
            screenshot: discord.Attachment
    ):
        await interaction.response.send_modal(
            GithubControlModal(
                bot=self.bot,
                type_="ISSUE",
                feature=feature,
                attachment=screenshot,
                github_client=self._github_client
            )
        )

    @command(name="close")
    @slash_is_bot_admin_4()
    async def __close(self, interaction: discord.Interaction, issue: int, reason: Optional[str] = None):
        await interaction.response.defer(thinking=True)
        r = self._github_client.get_repo("School-Simplified/Timmy-SchoolSimplified")
        try:
            issue_ = r.get_issue(issue)
        except:
            return await interaction.followup.send("Couldn't find issue")
        issue_.edit(state="closed")
        url = f"https://github.com/School-Simplified/Timmy-SchoolSimplified/issues/{issue}"
        await interaction.followup.send(f"Closed issue {url}")
        if reason:
            issue_.create_comment(reason)


class GithubCommands(commands.Cog):
    def __init__(self, bot: Timmy):
        self.bot = bot
        self._github_client = Github(os.getenv("GH_TOKEN"))
        self.__cog_app_commands__.append(GithubIssues(self.bot, self._github_client))
        self.__cog_name__ = "Github"


async def setup(bot: Timmy):
    await bot.add_cog(GithubCommands(bot))
