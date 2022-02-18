import os
import aiohttp
import discord
from dotenv import load_dotenv
from core import database
from core.checks import is_botAdmin
from discord.ext import commands
from core import redirect_sdk

load_dotenv()


class RedirectURL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.domain = "rs.schoolsimplified.org"
        self.raOBJ = redirect_sdk.RedirectClient(
            os.getenv("RP_TK"), domain="https://rs.schoolsimplified.org"
        )

    @commands.command(alliases=["redirectadd", "addredirect"])
    @is_botAdmin
    async def ra(self, ctx, redirect_code, destination_url: str):
        val = self.raOBJ.add_redirect(redirect_code, destination_url)
        await ctx.send(
            f"Redirect added for {destination_url} with redirect path /{redirect_code}\nCreated with the ID: {val.id}. In order to delete this redirect, you'll need this ID!\n\nAccess it at https://rs.schoolsimplified.org/{redirect_code}"
        )

    @commands.command(alliases=["redirectremove", "removeredirect"])
    @is_botAdmin
    async def rr(self, ctx, ID):
        self.raOBJ.del_redirect(ID)
        await ctx.send(f"Redirect removed for {ID}")

    @commands.command(alliases=["redirectlist", "listredirect"])
    @is_botAdmin
    async def rl(self, ctx):
        objlist = self.raOBJ.get_redirects()
        newlist = []
        for obj in objlist:
            newlist.append(
                f"**ID:** {obj.id} | **URL:** `https://{obj.domain}/{obj.source}` -> `{obj.destination}`"
            )
        newlist = "\n".join(newlist)
        embed = discord.Embed(
            title=f"Redirects for {self.raOBJ.domain}", color=discord.Color.blue()
        )
        embed.add_field(name="Redirects", value=newlist)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RedirectURL(bot))
