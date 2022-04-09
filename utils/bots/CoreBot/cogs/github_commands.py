from __future__ import annotations

import os
from typing import Dict, List, Literal, TYPE_CHECKING, Union

import discord
from github import Github
from discord.ext import commands
from discord.app_commands import command

if TYPE_CHECKING:
    from main import Timmy

QuestionListType = List[Dict[str, Union[bool, str, None]]]
GithubActionLiteral = Literal["ISSUE",]
IssueFeatureLiteral = Literal["Command", "Slash Command", "Dropdown or Button", "Other"]


class GithubControlModal(discord.ui.Modal):
    def __init__(
            self,
            bot: 'Timmy',
            _type: GithubActionLiteral,
            feature: IssueFeatureLiteral,
            attachment: discord.Attachment,
            github_client: Github,
    ):
        super().__init__(timeout=None)

        self.bot = bot
        self._type = _type
        self._feature_type = feature
        self._attachment = attachment.url
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
        for text_input in self.transform(self._type):
            self.add_item(
                discord.ui.TextInput(
                    label=text_input["title"],
                    required=text_input["required"],
                    placeholder=text_input["placeholder"] if text_input["placeholder"] else None,
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
        await interaction.response.defer()

        embed = discord.Embed(title=f"{self._feature_type} Issue", colour=discord.Colour.brand_green())

        issue_body = ""

        for item, question in zip(self.children, self.transform(self._type)):
            embed.add_field(
                name=question["title"],
                value=str(item),
                inline=False
            )
            issue_body += f"**{question['title']}**\n{str(item)}\n\n"

        repo = self._gh_client.get_repo("School-Simplified/Timmy-SchoolSimplified")

        issue = repo.create_issue(
            title=str(self.children[0]),
            body=f"**Issue Feature**\n{self._feature_type}\n\n" + issue_body + self._attachment,
            labels=[
                repo.get_label(name="Discord")
            ]
        )
        embed.description = f"[Created Issue!]({issue.url})"
        await interaction.followup.send(embed=embed)


class GithubCommands(commands.Cog):
    def __init__(self, bot: 'Timmy'):
        self.bot = bot
        self._github_client = Github(os.getenv("GH_TOKEN"))

    @command(name="open-issue")
    async def __issue(
            self,
            interaction: discord.Interaction,
            feature: IssueFeatureLiteral,
            screenshot: discord.Attachment
    ):
        await interaction.response.send_modal(
            GithubControlModal(
                bot=self.bot,
                _type="ISSUE",
                feature=feature,
                attachment=screenshot,
                github_client=self._github_client
            )
        )


async def setup(bot: 'Timmy'):
    await bot.add_cog(GithubCommands(bot))
