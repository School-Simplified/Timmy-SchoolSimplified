import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from core import redirect_sdk
from core.paginate import Pages, RedirectPageSource
from core.checks import is_botAdmin

load_dotenv()


class RedirectURL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.domain = "https://ssimpl.org"
        self.raOBJ = redirect_sdk.RedirectClient(
            os.getenv("RP_TK"), domain="https://ssimpl.org"
        )
        self.__cog_name__ = "Redirect URL"

    @property
    def display_emoji(self) -> str:
        return "🖇️"

    @commands.command(alliases=["redirectadd", "addredirect"])
    @is_botAdmin
    async def ra(self, ctx, redirect_code, destination_url: str):
        val = self.raOBJ.add_redirect(redirect_code, destination_url)
        await ctx.send(
            f"Redirect added for {destination_url} with redirect path /{redirect_code}\nCreated with the ID: {val.id}. In order to delete this redirect, you'll need this ID!\n\nAccess it at https://ssimpl.org/{redirect_code}"
        )

    @commands.command(alliases=["redirectremove", "removeredirect"])
    @is_botAdmin
    async def rr(self, ctx, ID):
        self.raOBJ.del_redirect(ID)
        await ctx.send(f"Redirect removed for {ID}")

    @commands.command(alliases=["redirectlist", "listredirect"])
    @is_botAdmin
    async def rl(self, ctx: commands.Context):
        objlist = self.raOBJ.get_redirects()
        entries = []
        for obj in objlist:
            entries.append(
                dict(
                    name=f"**ID:** {obj.id}",
                    value=f"**URL:** `https://{obj.domain}/{obj.source}` -> `{obj.destination}`"
                )
            )
        embed = discord.Embed(
            title=f"Redirects for {self.raOBJ.domain}", color=discord.Color.blue()
        )
        source = RedirectPageSource(entries, per_page=6, embed=embed)
        await Pages(source, bot=self.bot, ctx=ctx, compact=True).start()


async def setup(bot):
    await bot.add_cog(RedirectURL(bot))
