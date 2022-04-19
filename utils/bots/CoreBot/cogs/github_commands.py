from __future__ import annotations

import os
from typing import Literal, TYPE_CHECKING, Optional

from core.checks import slash_is_bot_admin_4
import discord
from github import Github
from discord.ext import commands
from discord.app_commands import command, Group
from core.gh_modals import GithubControlModal

if TYPE_CHECKING:
    from main import Timmy

IssueFeatureLiteral = Literal["Command", "Slash Command", "Dropdown or Button", "Other"]


class GithubIssues(Group):
    def __init__(
            self,
            bot: Timmy,
            github_client: Github,
    ):
        super().__init__(
            name="issue", description="Open an issue for a bug related to the bot"
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
            screenshot: discord.Attachment,
    ):
        await interaction.response.send_modal(
            GithubControlModal(
                bot=self.bot,
                type_="ISSUE",
                feature=feature,
                attachment=screenshot,
                github_client=self._github_client,
            )
        )

    @command(name="close")
    @slash_is_bot_admin_4()
    async def __close(
            self, interaction: discord.Interaction, issue: int, reason: Optional[str] = None
    ):
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
