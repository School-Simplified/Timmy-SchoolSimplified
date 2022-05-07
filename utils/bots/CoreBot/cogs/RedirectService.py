import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from core import redirect_sdk
from core.common import Others, TechID
from core.paginate import Pages, RedirectPageSource, RoboPages
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

    @app_commands.command(name="redirect-add", description="Add a redirect URL")
    @app_commands.describe(
        redirect_code="The URL path you want to use.",
        destination_url="The destination URL to redirect to.",
    )
    @app_commands.guilds(TechID.g_tech)
    async def ra(self, interaction: discord.Interaction, redirect_code: str, destination_url: str):
        try:
            val = self.raOBJ.add_redirect(redirect_code, destination_url)
        except redirect_sdk.UnprocessableEntity as e:
            errors = "\n".join(e.errors[0])
            embed = discord.Embed(title="Unprocessable Entity", color=discord.Color.brand_red())
            embed.add_field(name="Unable to Add Redirect", value=errors)
            embed.set_thumbnail(url=Others.timmy_dog_png)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                f"Redirect added for {destination_url} with redirect path /{redirect_code}\nCreated with the ID: {val.id}. In order to delete this redirect, you'll need this ID!\n\nAccess it at https://ssimpl.org/{redirect_code}",
                ephemeral=True,
            )

    @app_commands.command(name="redirect-remove", description="Remove a redirect.")
    @app_commands.describe(redirect_id="Specify an ID or URL PATH to remove a redirect.")
    @app_commands.guilds(TechID.g_tech)
    async def rr(self, interaction: discord.Interaction, redirect_id: str):
        self.raOBJ.del_redirect(redirect_id)
        await interaction.response.send_message(f"Redirect removed for {redirect_id}")

    @app_commands.command(name="redirect-list", description="List all redirects.")
    @app_commands.guilds(TechID.g_tech)
    async def rl(self, interaction: discord.Interaction):
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
        await RoboPages(source, bot=self.bot, interaction=interaction, compact=True).start()

    @app_commands.command(name="redirect-info", description="Get info about a redirect.")
    @app_commands.describe(redirect_id="Specify an ID or URL PATH to get info about a redirect.")
    @app_commands.guilds(TechID.g_tech)
    async def ri(self, interaction: discord.Interaction, redirect_id: str):
        obj = self.raOBJ.fetch_redirect(redirect_id)
        embed = discord.Embed(
            title=f"Redirect Info for {obj.source}", color=discord.Color.blue()
        )
        embed.add_field(name="ID", value=obj.id)
        embed.add_field(name="Source", value=obj.source)
        embed.add_field(name="Destination", value=obj.destination)
        embed.add_field(name="Domain", value=obj.domain)
        embed.add_field(name="Created At", value=obj.created_at)
        await interaction.response.send_message(embed=embed)



async def setup(bot):
    await bot.add_cog(RedirectURL(bot))
