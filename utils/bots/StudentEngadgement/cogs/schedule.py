import datetime
from typing import List, Dict, Literal, TYPE_CHECKING, Union

import discord.utils
import pytz
from discord.ext import commands, tasks

from core.common import Colors, ScheduleView, SETID

if TYPE_CHECKING:
    from main import Timmy

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
    def __init__(self, bot: Timmy):
        self._schedule: Dict[
            TaskLiteral, Dict[Literal["_type", "_schedule"], List[Union[Literal["rachel", "ignore"], int]]]
        ] = {
            "Motivation": {
                "_type": "DAILY",
                "_schedule": [
                    806289946624393216,
                    869561723101786162,
                    "ignore",
                    806289946624393216,
                    "ignore",
                    "rachel",
                    869561723101786162,
                ]  # first index is monday
            },
            "Weekly Puzzle": {
                "_type": "WEEKLY"
            },
            "Opportunities": {
                "_type": "WEEKLY",
                "date": "12"
            },
            "Daily Question": {
                "_type": "DAILY"
            },
            "Media Recommendations": {
                "_type": "WEEKLY"
            },
            "Art Appreciation": {
                "_type": "WEEKLY"
            },
            "Daily Laugh": {
                "_type": "DAILY"
            },
        }
        self.bot = bot

    @commands.Cog.listener('on_ready')
    async def _on_ready(self) -> None:
        self._reminder_loop.start()

    @tasks.loop(time=[datetime.time(tzinfo=pytz.timezone("America/New_York"))])
    async def _reminder_loop(self):
        day: int = discord.utils.utcnow().astimezone(pytz.timezone("America/New_York")).isoweekday()
        await self._handle_motivation(day, self._schedule["Motivation"])

    async def _handle_motivation(
            self, day: int, dict_: Dict
    ) -> None:
        embed = discord.Embed(
            color=Colors.blurple,
            title="Reminder!",
            description="Reminder to complete the motivational quote for today!"
        )
        await self._dm_member(embed=embed, user_id=await self._get_user_id(day=day, dict_=dict_), _type="Motivation")


    async def _get_user_id(
            self, day: int, dict_: Dict[Literal["_type", "_schedule"], List[Union[Literal["rachel", "ignore"], int]]]
    ) -> Union[int, Literal["rachel", "ignore"]]:
        schedule_list = dict_["_schedule"]
        return schedule_list[day]

    async def _dm_member(self, embed: discord.Embed, user_id: Union[int, str], _type: TaskLiteral) -> None:
        if user_id in ["rachel", "ignore"]:
            return
        server = self.bot.get_guild(SETID.g_set)
        member = server.get_member(user_id)
        await member.send(embed=embed, view=ScheduleView(self.bot, task=_type))




