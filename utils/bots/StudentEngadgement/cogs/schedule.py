from __future__ import annotations

import datetime
from typing import List, Dict, Literal, TYPE_CHECKING, TypeVar, Union

import discord.utils
import pytz
from discord.ext import commands, tasks

from core.common import Colors, ScheduleView, SETID

if TYPE_CHECKING:
    from main import Timmy
    T = TypeVar("T")

TaskLiteral = Literal[
    "Motivation",
    "Weekly Puzzle",
    "Opportunities",
    "Daily Question",
    "Media Recommendations",
    "Art Appreciation",
    "Daily Laugh",
]


class SetScheduleCog(commands.Cog):
    def __init__(self, bot: 'Timmy'):
        self._schedule: Dict[
            TaskLiteral, Dict[Literal["_type", "_schedule"], Union[str, List[Union[Literal["rachel", "ignore"], int]]]]
        ] = {
            "Motivation": {
                "_type": "DAILY",
                "_schedule": [
                    869561723101786162,
                    869561723101786162,
                    706668075545526273,
                    869561723101786162,
                    768198790590103614,
                    672955248444309504,
                    672955248444309504,
                ]  # first index is monday
            },
            "Weekly Puzzle": {
                "_type": "WEEKLY",
            },
            "Opportunities": {
                "_type": "WEEKLY",
            },
            "Daily Question": {
                "_type": "DAILY",
                "_schedule": [
                    422540484079255572,
                    337250887858782209,
                    422540484079255572,
                    422540484079255572,
                    706668075545526273,
                    337250887858782209,
                    132848537435242496
                ]
            },
            "Media Recommendations": {
                "_type": "WEEKLY"
            },
            "Art Appreciation": {
                "_type": "WEEKLY"
            },
            "Daily Laugh": {
                "_type": "DAILY",
                "_schedule": [
                    422540484079255572,
                    132848537435242496,
                    422540484079255572,
                    599302211272441876,
                    422540484079255572,
                    132848537435242496,
                    599302211272441876

                ]
            },
        }
        self.bot = bot
        self._reminder_loop.start()

    @tasks.loop(time=[datetime.time(tzinfo=pytz.timezone("America/New_York"), hour=9)])
    async def _reminder_loop(self):
        print("starting task")
        """
        Handles daily reminders
        """
        day: int = discord.utils.utcnow().astimezone(pytz.timezone("America/New_York")).isoweekday()
        await self._handle_motivation(day, self._schedule["Motivation"])
        await self._handle_question(day, self._schedule["Daily Question"])
        await self._handle_laugh(day, self._schedule["Daily Laugh"])

    @tasks.loop(hours=1)
    async def _weekly_reminders_loop(self):
        """
        Handles weekly reminders
        """
        day: int = discord.utils.utcnow().astimezone(pytz.timezone("America/New_York")).isoweekday()
        hour: int = discord.utils.utcnow().astimezone(pytz.timezone("America/New_York")).hour
        if day != 7:
            return
        if hour < 9:
            return
        pass  # Implement later

    async def _handle_motivation(
            self, day: int, dict_: Dict
    ) -> None:
        if self._get_user_id(day=day, dict_=dict_) == "ignore":
            return
        embed = discord.Embed(
            color=Colors.blurple,
            title="Reminder!",
            description="Reminder to complete the motivational quote for today! "
                        "Once you have completed your quote please press the completed button below. "
                        "If you cannot complete it please select the red button below. "
        )
        await self._dm_member(embed=embed, user_id=self._get_user_id(day=day, dict_=dict_), _type="Motivation")

    async def _handle_question(
            self, day: int, dict_: Dict
    ) -> None:
        if self._get_user_id(day=day, dict_=dict_) == "ignore":
            return
        embed = discord.Embed(
            color=Colors.blurple,
            title="Reminder!",
            description="Reminder to complete the daily question for today! "
                        "Once you have completed your question please press the completed button below. "
                        "If you cannot complete it please select the red button below. "
        )
        await self._dm_member(embed=embed, user_id=self._get_user_id(day=day, dict_=dict_), _type="Daily Question")

    async def _handle_laugh(
            self, day: int, dict_: Dict
    ) -> None:
        if self._get_user_id(day=day, dict_=dict_) == "ignore":
            return
        embed = discord.Embed(
            color=Colors.blurple,
            title="Reminder!",
            description="Reminder to complete the daily laugh for today! "
                        "Once you have completed your meme/pickup line please press the completed button below. "
                        "If you cannot complete it please select the red button below. "
        )
        await self._dm_member(embed=embed, user_id=self._get_user_id(day=day, dict_=dict_), _type="Daily Laugh")

    def _get_user_id(
            self,
            day: int,
            dict_: Dict[Literal["_type", "_schedule"], Union[str, List[Union[Literal["rachel", "ignore"], int]]]]
    ) -> Union[int, Literal["rachel", "ignore"]]:
        schedule_list = dict_["_schedule"]
        return schedule_list[day - 1]

    async def _dm_member(
            self, embed: discord.Embed, user_id: Union[int, str], _type: TaskLiteral
    ) -> None:
        if user_id in ["rachel", "ignore"] or isinstance(user_id, str):
            return
        server = self.bot.get_guild(SETID.g_set)
        member = server.get_member(user_id)
        await member.send(embed=embed, view=ScheduleView(self.bot, task=_type))
        print(f"Sent {member} reminder dm")


async def setup(bot: Timmy):
    await bot.add_cog(SetScheduleCog(bot))
