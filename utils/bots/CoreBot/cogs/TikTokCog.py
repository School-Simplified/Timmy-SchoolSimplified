import os
import uuid

import discord
import requests
from discord.ext import commands

from core import redirect_sdk

url = "https://godownloader.com/api/tiktok-no-watermark-free?key=godownloader.com&url="


class TikTokNWM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.domain = "https://cdn.ssimpl.org"
        self.raOBJ = redirect_sdk.RedirectClient(
            os.getenv("RP_TK"), domain="https://cdn.ssimpl.org"
        )

    @commands.Cog.listener("on_message")
    async def remove_tiktok_wm(self, message: discord.Message):
        if message.author.bot:
            return
        if message.content.startswith("https://www.tiktok.com"):
            guild = await self.bot.fetch_guild(891521033700540457)
            emoji = await guild.fetch_emoji(905563298089541673)

            await message.add_reaction(emoji)
            response = requests.request("GET", f"{url}{message.content}")
            no_vm_url = response.json()["video_no_watermark"]
            rp = self.raOBJ.add_redirect(f"{str(uuid.uuid4())}", no_vm_url)
            await message.channel.send(f"https://{rp.source}")
            await message.clear_reactions()
            await message.add_reaction("✅")


async def setup(bot):
    await bot.add_cog(TikTokNWM(bot))
