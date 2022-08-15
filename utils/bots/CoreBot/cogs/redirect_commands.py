import datetime
import os
from datetime import datetime
from typing import Dict, List

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from core import redirect_sdk, database
from core.common import Others, TechID, StaffID
from core.paginate import RedirectPageSource, RoboPages

load_dotenv()


async def redirect_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    # Inactive due to 75 choice limit
    rp_client = redirect_sdk.RedirectClient(
        os.getenv("RP_TK"), domain="https://ssimpl.org"
    )
    lor = rp_client.get_redirects()
    choices = [name.source for name in lor]
    return [
        app_commands.Choice(name=redirect, value=redirect)
        for redirect in choices
        if current.lower() in redirect.lower()
    ]


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
    @app_commands.guilds(TechID.g_tech, StaffID.g_staff_resources)
    async def ra(
        self,
        interaction: discord.Interaction,
        redirect_code: str,
        destination_url: str,
        sub_domain: str = None,
    ):
        if sub_domain is None:
            try:
                val = self.raOBJ.add_redirect(redirect_code, destination_url)
            except redirect_sdk.UnprocessableEntity as e:
                errors = "\n".join(e.errors[0])
                embed = discord.Embed(
                    title="Unprocessable Entity", color=discord.Color.brand_red()
                )
                embed.add_field(name="Unable to Add Redirect", value=errors)
                embed.set_thumbnail(url=Others.timmy_dog_png)

                return await interaction.response.send_message(
                    embed=embed, ephemeral=False
                )
            else:
                query = database.RedirectLogs.create(
                    redirect_id=val.id,
                    from_url=redirect_code,
                    to_url=destination_url,
                    sub_domain=sub_domain,
                    created_at=datetime.now(),
                )
                query.save()
                embed = discord.Embed(
                    title="Redirect Added", color=discord.Color.brand_green()
                )
                embed.add_field(
                    name="Redirect Code", value=redirect_code
                )
                embed.add_field(
                    name="Redirect ID", value=f"`{val.id}`\n\nUse this ID to modify/delete this redirect."
                )
                embed.add_field(name="Destination URL", value=destination_url, inline=False)
                embed.add_field(name="Subdomain", value=sub_domain)
                embed.add_field(name="Test it out?", value="[https://ssimpl.org/{}](https://ssimpl.org/{})".format(redirect_code, redirect_code), inline=False)
                embed.set_thumbnail(url=Others.timmy_happy_png)
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url, url=interaction.user.avatar.url)

                await interaction.response.send_message(
                    embed=embed, ephemeral=False
                )
        else:
            if not ".ssimpl.org" in sub_domain:
                sub_domain += ".ssimpl.org"
            query = database.ApprovedSubDomains.select().where(
                database.ApprovedSubDomains.sub_domain == sub_domain
            )
            if query.exists():
                try:
                    val = self.raOBJ.add_redirect(
                        redirect_code, destination_url, sub_domain
                    )
                except redirect_sdk.UnprocessableEntity as e:
                    errors = "\n".join(e.errors[0])
                    embed = discord.Embed(
                        title="Unprocessable Entity", color=discord.Color.brand_red()
                    )
                    embed.add_field(name="Unable to Add Redirect", value=errors)
                    embed.set_thumbnail(url=Others.timmy_dog_png)
                    return await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
                else:
                    query = database.RedirectLogs.create(
                        redirect_id=val.id,
                        from_url=redirect_code,
                        to_url=destination_url,
                        sub_domain=sub_domain,
                        created_at=datetime.now(),
                    )
                    query.save()
                    await interaction.response.send_message(
                        f"Redirect added for {destination_url} with redirect path /{redirect_code}\nCreated with the ID: {val.id}. In order to delete this redirect, you'll need this ID!\n\nAccess it at https://{sub_domain}.ssimpl.org/{redirect_code}",
                        ephemeral=True,
                    )
            else:
                await interaction.response.send_message(
                    f"{sub_domain} is not an approved subdomain. Please contact a staff member to add it.",
                    ephemeral=True,
                )

    @app_commands.command(name="redirect-remove", description="Remove a redirect.")
    @app_commands.describe(
        redirect_id="Specify an ID or URL PATH to remove a redirect.",
        subdomain="Specify the subdomain if using URL Path to remove a redirect.",
    )
    @app_commands.guilds(TechID.g_tech, StaffID.g_staff_resources)
    async def rr(
        self, interaction: discord.Interaction, redirect_id: str, subdomain: str = None
    ):
        self.raOBJ.del_redirect(redirect_id, subdomain)
        query = database.RedirectLogs.select().where(
            database.RedirectLogs.redirect_id == redirect_id
        )
        embed = discord.Embed(
            title="Redirect Removed", color=discord.Color.brand_green()
        )

        if query.exists():
            query = query.get()
            embed.add_field(
                name="Redirect Code", value=query.from_url
            )
            embed.add_field(name="Destination URL", value=query.to_url)
            query.delete_instance()

        embed.add_field(name="Redirect ID", value=redirect_id)
        embed.add_field(name="Subdomain", value=subdomain)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url, url=interaction.user.avatar.url)
        await interaction.response.send_message(
            embed=embed, ephemeral=False
        )

    @app_commands.command(name="redirect-list", description="List all redirects.")
    @app_commands.guilds(TechID.g_tech, StaffID.g_staff_resources)
    async def rl(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        obj_list = self.raOBJ.get_redirects()
        entries: List[Dict[str, str]] = []
        for obj in obj_list:
            entries.append(
                dict(
                    name=f"**ID:** {obj.id}",
                    value=f"**URL:** `https://{obj.domain}/{obj.source}` -> `{obj.destination}`",
                )
            )
        embed = discord.Embed(
            title=f"Redirects for {self.raOBJ.domain}", color=discord.Color.blue()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url,
                         url=interaction.user.avatar.url)
        source = RedirectPageSource(entries, per_page=6, embed=embed)
        await RoboPages(
            source, bot=self.bot, interaction=interaction, compact=True
        ).start()

    @app_commands.command(
        name="redirect-info", description="Get information about a specific redirect."
    )
    @app_commands.describe(
        redirect_id="Specify an ID or URL PATH to get info about a redirect.",
        subdomain="Specify the subdomain if using URL Path to get info about a redirect.",
    )
    @app_commands.guilds(TechID.g_tech, StaffID.g_staff_resources)
    async def ri(
        self, interaction: discord.Interaction, redirect_id: str, subdomain: str = None
    ):
        await interaction.response.defer(thinking=True)
        obj = self.raOBJ.fetch_redirect(redirect_id, subdomain)
        if obj is None:
            return await interaction.followup.send(
                f"Redirect not found for {redirect_id}"
            )
        embed = discord.Embed(
            title=f"Redirect Info for {obj.source}", color=discord.Color.blue()
        )
        embed.add_field(name="ID", value=obj.id)
        embed.add_field(name="Source", value=obj.source)
        embed.add_field(name="Destination", value=obj.destination)
        embed.add_field(name="Created At", value=obj.created_at)
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RedirectURL(bot))
