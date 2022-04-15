from __future__ import annotations

import os
from typing import Dict, Literal, TYPE_CHECKING, Union, List, Optional
import discord
from github import Github

from core.common import TECH_ID

QuestionListType = List[Dict[str, Union[bool, str, None]]]
GithubActionLiteral = Literal[
    "ISSUE",
    "FEEDBACK",
]
IssueFeatureLiteral = Literal["Command", "Slash Command", "Dropdown or Button", "Other"]

if TYPE_CHECKING:
    from main import Timmy


class GithubControlModal(discord.ui.Modal):
    def __init__(
            self,
            bot: Timmy,
            type_: GithubActionLiteral,
            github_client: Github,
            feature: Optional[IssueFeatureLiteral] = None,
            attachment: Optional[discord.Attachment] = None,
            gist_url: Optional[str] = None,
    ):
        super().__init__(
            timeout=None,
            title="Create Issue" if type_ == "ISSUE"
            else "Submit Feedback" if type_ == "FEEDBACK"
            else " "
        )

        self.bot = bot
        self._type = type_
        self._feature_type = feature if feature else None
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
                "placeholder": "A simple summary of your bug report",
            },
            {
                "title": "Additional Context",
                "required": False,
                "placeholder": "If there is anything else to say, please do so here.",
            },
        ]
        self.feedback_list: QuestionListType = [
            {
                "title": "What did you try to do?",
                "required": True,
                "placeholder": None
            },
            {
                "title": "Describe the steps to reproduce the issue",
                "required": True,
                "placeholder": None
            },
            {
                "title": "What happened?",
                "required": True,
                "placeholder": None
            },
            {
                "title": "What was supposed to happen?",
                "required": True,
                "placeholder": None
            },
            {
                "title": "Anything else?",
                "required": False,
                "placeholder": "Add pictures or links here to help us understand your issue."
            }
        ]
        for item_blueprint in self._transform():
            self.add_item(
                discord.ui.TextInput(
                    label=item_blueprint["title"],
                    required=item_blueprint["required"],
                    placeholder=item_blueprint["placeholder"]
                    if item_blueprint["placeholder"]
                    else None,
                    max_length=1024,
                    style=discord.TextStyle.paragraph,
                )
            )

    def _transform(self) -> QuestionListType:
        transformer_dict: Dict[GithubActionLiteral, QuestionListType] = {
            "ISSUE": self.issue_list,
            "FEEDBACK": self.feedback_list,
        }
        return transformer_dict[self._type]


    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        repo = self._gh_client.get_repo("School-Simplified/Timmy-SchoolSimplified")
        if self._type == "ISSUE":
            return await self._issue_dispatch_to_gh(repo=repo, interaction=interaction)
        elif self._type == "FEEDBACK":
            return await self._feedback_dispatch_to_gh(repo=repo, interaction=interaction)

    async def _issue_dispatch_to_gh(self, repo, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{self._feature_type} Issue", colour=discord.Colour.brand_green()
        )

        issue_body = ""

        for item, question in zip(self.children, self._transform()):
            embed.add_field(name=question["title"], value=str(item), inline=False)
            none_text = "None"
            issue_body += f"**{question['title']}**\n{str(item) if str(item) != '' else none_text}\n\n"

        issue = repo.create_issue(
            title=str(self.children[0]),
            body=f"**Issue Feature**\n{self._feature_type}\n\n"
                 + issue_body
                 + self._attachment,
        )
        issue.add_to_labels(repo.get_label(name="Discord"))
        url = f"https://github.com/School-Simplified/Timmy-SchoolSimplified/issues/{issue.number}"
        embed.description = f"[Created Issue!]({url})"
        await interaction.followup.send(embed=embed)

    async def _feedback_dispatch_to_gh(self, repo, interaction: discord.Interaction):
        response = (
            f"- User Action: {self.children[0]}\n\n"
            f"- Steps to reproduce the issue: {self.children[1]}\n\n"
            f"- What happened: {self.children[2]}\n\n"
            f"- Expected Result: {self.children[3]}\n\n"
            f"- Anything else: {self.children[4]}\n\n"
            f"- Gist: {self._gist_url}"
        )
        issue = repo.create_issue(
            title=f"{interaction.user.name} | {interaction.user.id} Issue/Feedback",
            body=f"**Feedback:**\n\n{response}"
        )
        issue.add_to_labels(repo.get_label(name="Discord"), repo.get_label(name="question"))
        url = f"https://github.com/School-Simplified/Timmy-SchoolSimplified/issues/{issue.number}"
        await interaction.followup.send(
            "Your issue has been submitted!\nA developer will reach out soon to respond to your issue."
        )

        dev_channel = self.bot.get_channel(TECH_ID.ch_tracebacks)
        embed = discord.Embed(
            title="New Issue",
            description=f"{interaction.user.mention} has submitted a new issue! `#{issue.number}` "
                        f"\n[Click here to view the issue]({url})",
            color=discord.Color.brand_red(),
        )
        await dev_channel.send(embed=embed)


class FeedbackButton(discord.ui.View):
    def __init__(self, bot: Timmy, gist_url: str):
        super().__init__(timeout=500.0)
        self.value = None
        self.bot = bot
        self.gist_url = gist_url

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

    @discord.ui.button(
        label="Submit Feedback",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:feedback_button",
        emoji="📝",
    )
    async def feedback_button(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button,
    ):
        return await interaction.response.send_modal(
            GithubControlModal(
                bot=self.bot,
                type_="FEEDBACK",
                github_client=Github(os.getenv("GH_TOKEN")),
                gist_url=self.gist_url
            )
        )


# class FeedbackModel(discord.ui.Modal, title="Submit Feedback"):
#     def __init__(self, bot) -> None:
#         super().__init__()
#         self.bot = bot
#         self.add_item(
#             discord.ui.TextInput(
#                 label="What did you try to do?",
#                 style=discord.TextStyle.long,
#             )
#         )
#         self.add_item(
#             discord.ui.TextInput(
#                 label="Describe the steps to reproduce the issue",
#                 style=discord.TextStyle.long,
#             )
#         )
#         self.add_item(
#             discord.ui.TextInput(
#                 label="What happened?",
#                 style=discord.TextStyle.long,
#             )
#         )
#         self.add_item(
#             discord.ui.TextInput(
#                 label="What was supposed to happen?",
#                 style=discord.TextStyle.long,
#             )
#         )
#         self.add_item(
#             discord.ui.TextInput(
#                 label="Anything else?",
#                 style=discord.TextStyle.long,
#                 placeholder="Add pictures or links here to help us understand your issue.",
#                 required=False,
#             )
#         )
#
#     async def on_submit(self, interaction: discord.Interaction):
#         ...

