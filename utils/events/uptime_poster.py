import os
import time

import psutil
from discord.ext import tasks, commands
import requests

from core.common import get_host_dir


class MetricPoster(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.instatus_metric_post.start()
        self.self_host = bool(os.getenv("SELF_HOST"))

    async def cog_unload(self):
        self.instatus_metric_post.stop()

    @tasks.loop(seconds=60)
    async def instatus_metric_post(self):
        """
        POST /v1/timmyos/metrics
        post request with bot.latency.
        Thanks, GitHub copilot <3
        """
        host_dir = get_host_dir()
        print(f"Host dir: {host_dir}")
        if host_dir == "/home/timmya" or host_dir == "/home/timmy-beta":
            ping_payload = {"value": round(self.bot.latency * 1000), "timestamp": time.time()}
            cpu_payload = {"value": psutil.cpu_percent(), "timestamp": time.time()}
            ram_payload = {"value": psutil.virtual_memory().percent, "timestamp": time.time()}

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + os.getenv("INSTATUS_TOKEN"),
            }
            ping_response = requests.request(
                "POST",
                "https://api.instatus.com/v1/cl69luezk0117y5lr0hll9h9y/metrics"
                "/cl6bb20bt92861xpnd3m5y8o4f",
                headers=headers,
                json=ping_payload,
            )
            cpu_response = requests.request(
                "POST",
                "https://api.instatus.com/v1/cl69luezk0117y5lr0hll9h9y/metrics"
                "/cl6bb1u6793568windnu7f5hw3",
                headers=headers,
                json=cpu_payload,
            )
            ram_response = requests.request(
                "POST",
                "https://api.instatus.com/v1/cl69luezk0117y5lr0hll9h9y/metrics"
                "/cl6bb1oae96997x8ndm6hf8gft",
                headers=headers,
                json=ram_payload,
            )
            print("Posted metrics")


    @instatus_metric_post.before_loop
    async def before_loop_(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(MetricPoster(bot))
