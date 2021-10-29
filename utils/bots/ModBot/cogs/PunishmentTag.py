import math

import discord
from core import common, database
from core.common import hexColors
from discord.ext import commands


class PunishmentTag(commands.Cog):
    """Commands related to our dynamic tag system."""

    def __init__(self, bot):
        self.bot = bot

    def get_by_index(self, index):
        for i, t in enumerate(database.PunishmentTag.select()):
            if i + 1 == index:
                return t

    @commands.command(aliases=["punishment"])
    async def p(self, ctx, tag_name):
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
                title=tag.embed_title, description=tag.text, color=hexColors.mod_blurple
            )
            await ctx.send(embed=embed)
        except database.DoesNotExist:
            await ctx.send("Tag not found, please try again.")
        finally:
            database.db.close()

    @commands.command(aliases=["newp"])
    @commands.has_any_role(
        "Secret Service", "Head Moderator", "Senior Mod", "Moderator"
    )
    # don't let this recognize tag number, name is a required field for new tags. - Fire
    async def pmod(self, ctx, name, title, *, text):
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
            await ctx.send(f"Tag {tag.tag_name} has been modified successfully.")
        except database.DoesNotExist:
            try:
                database.db.connect(reuse_if_open=True)
                tag: database.PunishmentTag = database.PunishmentTag.create(
                    tag_name=name, embed_title=title, text=text
                )
                tag.save()
                await ctx.send(f"Tag {tag.tag_name} has been created successfully.")
            except database.IntegrityError:
                await ctx.send("That tag name is already taken!")
        finally:
            database.db.close()

    @commands.command(aliases=["delp", "dp"])
    @commands.has_any_role(
        "Secret Service", "Head Moderator", "Senior Mod", "Moderator"
    )
    async def deletep(self, ctx, name):
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
            await ctx.send(f"{tag.tag_name} has been deleted.")
        except database.DoesNotExist:
            await ctx.send("Tag not found, please try again.")
        finally:
            database.db.close()

    @commands.command(aliases=["ltag"])
    async def listtag(self, ctx, page=1):
        """List all tags in the database"""

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
            self.bot, ctx, embed, populate_embed, get_end(10), page=page
        )


def setup(bot):
    bot.add_cog(PunishmentTag(bot))
