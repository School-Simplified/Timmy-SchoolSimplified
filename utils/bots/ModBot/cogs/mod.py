import asyncio
import math

import discord
import peewee
from discord import app_commands
from discord.ext import commands

from core import common, database
from core.common import Colors, Emoji, MainID, DiscID


class PunishmentTag(commands.Cog):
    """Moderation commands"""

    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = "Moderation"

    @property
    def display_emoji(self) -> str:
        return Emoji.mod_shield

    @staticmethod
    def get_by_index(index):
        for i, t in enumerate(database.PunishmentTag.select()):
            if i + 1 == index:
                return t

    PT = app_commands.Group(
        name="punishment-tags",
        description="Manage the punishment tags",
        guild_ids=[MainID.g_main, DiscID.g_disc],
    )

    @PT.command(name="activate", description="Activate a punishment tag")
    @app_commands.describe(
        tag_name="The name of the punishment tag to send.",
    )
    async def p(self, interaction: discord.Interaction, tag_name: str):
        """Activate a tag"""
        try:
            database.db.connect(reuse_if_open=True)
            try:
                tag_name = int(tag_name)
                tag = self.get_by_index(tag_name)
            except ValueError:
                tag: database.PunishmentTag = (
                    database.PunishmentTag.select()
                    .where(database.PunishmentTag.tag_name == tag_name)
                    .get()
                )
            embed = discord.Embed(
                title=tag.embed_title, description=tag.text, color=Colors.mod_blurple
            )
            await interaction.response.send_message(embed=embed)
        except peewee.DoesNotExist:
            await interaction.response.send_message("Tag not found, please try again.")
        finally:
            database.db.close()

    # TODO: Make text a more better interface to edit.
    @PT.command(name="new-or-edit", description="Create or edit a punishment tag")
    @app_commands.checks.has_any_role(
        844013914609680384, "Head Moderator", "Senior Mod", "Moderator"
    )
    @app_commands.describe(
        name="The name of the punishment tag to create or edit.",
        title="The title of the embed.",
        text="The text of the embed.",
    )
    async def pmod(self, interaction: discord.Interaction, name, title, *, text):
        """Modify a tag, or create a new one if it doesn't exist."""
        try:
            database.db.connect(reuse_if_open=True)
            tag: database.PunishmentTag = (
                database.PunishmentTag.select()
                .where(database.PunishmentTag.tag_name == name)
                .get()
            )
            tag.text = text
            tag.embed_title = title
            tag.save()
            await interaction.response.send_message(f"Tag {tag.tag_name} has been modified successfully.")
        except peewee.DoesNotExist:
            try:
                database.db.connect(reuse_if_open=True)
                tag: database.PunishmentTag = database.PunishmentTag.create(
                    tag_name=name, embed_title=title, text=text
                )
                tag.save()
                await interaction.response.send_message(f"Tag {tag.tag_name} has been created successfully.")
            except peewee.IntegrityError:
                await interaction.response.send_message("That tag name is already taken!")
        finally:
            database.db.close()

    @PT.command(name="delete", description="Delete a punishment tag")
    @commands.has_any_role(
        844013914609680384, "Head Moderator", "Senior Mod", "Moderator"
    )
    @app_commands.describe(
        name="The name of the punishment tag to delete.",
    )
    async def deletep(self, interaction: discord.Interaction, name):
        """Delete a tag"""
        try:
            database.db.connect(reuse_if_open=True)
            try:
                name = int(name)
                tag = self.get_by_index(name)
            except ValueError:
                tag: database.PunishmentTag = (
                    database.PunishmentTag.select()
                    .where(database.PunishmentTag.tag_name == name)
                    .get()
                )
            tag.delete_instance()
            await interaction.response.send_message(f"{tag.tag_name} has been deleted.")
        except peewee.DoesNotExist:
            await interaction.response.send_message("Tag not found, please try again.")
        finally:
            database.db.close()

    @commands.command(name="list", description="List all punishment tags.")
    @app_commands.describe(pages="Page index to start at.")
    async def listtag(self, interaction: discord.Interaction, page=1):
        """List all tags in the database"""
        msg = await interaction.response.send_message("Loading...", ephermal=True)
        await asyncio.sleep(1.2)
        await msg.delete()

        def get_end(page_size: int):
            database.db.connect(reuse_if_open=True)
            tags: int = database.PunishmentTag.select().count()
            return math.ceil(tags / 10)

        async def populate_embed(embed: discord.Embed, page: int):
            """Used to populate the embed in listtag command"""
            tag_list = ""
            embed.clear_fields()
            database.db.connect(reuse_if_open=True)
            if database.PunishmentTag.select().count() == 0:
                tag_list = "No tags found"
            for i, tag in enumerate(database.PunishmentTag.select().paginate(page, 10)):
                tag_list += f"{i+1+(10*(page-1))}. {tag.tag_name}\n"
            embed.add_field(name=f"Page {page}", value=tag_list)
            database.db.close()
            return embed

        embed = discord.Embed(title="Tag List")
        embed = await common.paginate_embed(
            self.bot, interaction, embed, populate_embed, get_end(10), page=page
        )


async def setup(bot):
    await bot.add_cog(PunishmentTag(bot))
