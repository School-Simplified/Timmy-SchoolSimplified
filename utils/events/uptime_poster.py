import os
import time

from discord.ext import tasks, commands
import requests


class MetricPoster(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.instatus_metric_post.start()

    async def cog_unload(self):
        self.instatus_metric_post.stop()

    @tasks.loop(seconds=60)
    async def instatus_metric_post(self):
        """
        POST /v1/timmyos/metrics
        post request with bot.latency.
        Thanks, GitHub copilot <3
        """

        payload = {
            "value": round(self.bot.latency * 1000),
            "timestamp": time.time()
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + os.getenv("INSTATUS_TOKEN")
        }
        response = requests.request("POST", "https://api.instatus.com/v1/cl69luezk0117y5lr0hll9h9y/metrics"
                                            "/cl69p8y0b11647velr16gs6ial", headers=headers, json=payload)
        print(response.text)
        print(response.status_code)
        if response.status_code == 200:
            print("Successfully posted metric")
        else:
            print("Failed to post metric")

    @instatus_metric_post.before_loop
    async def before_loop_(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(MetricPoster(bot))
