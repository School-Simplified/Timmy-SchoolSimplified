import math

import discord
import peewee

from core import common, database
from discord.ext import commands


class CTag(commands.Cog):
    """Commands related to our dynamic tag system."""

    def __init__(self, bot):
        self.bot = bot


    @staticmethod
    def get_by_index(index):
        for i, t in enumerate(database.CTag.select()):
            if i + 1 == index:
                return t


    @commands.command(aliases=["chathelper"])
    async def c(self, ctx, tag_name):
        """Activates a tag"""

        try:
            database.db.connect(reuse_if_open=True)
            try:
                tag_name = int(tag_name)
                tag = self.get_by_index(tag_name)
            except ValueError:
                tag: database.CTag = (
                    database.CTag.select()
                    .where(database.CTag.tag_name == tag_name)
                    .get()
                )
            embed = discord.Embed(title=tag.embed_title, description=tag.text)
            await ctx.send(embed=embed)

        except peewee.DoesNotExist:
            await ctx.send("Tag not found, please try again.")
        finally:
            database.db.close()

    @commands.command(aliases=["newc"])
    @commands.has_any_role(
        844013914609680384, "Head Moderator", "Senior Mod", "Moderator"     # 844013914609680384: Secret Service Admin role in 'MAIN_ID.g_main'
    )
    async def cmod(self, ctx, name, title, *, text):            # don't let this recognize tag number, name is a required field for new tags. - Fire
        """Modifies a tag, or create a new one if it doesn't exist."""

        try:
            database.db.connect(reuse_if_open=True)
            tag: database.CTag = (
                database.CTag.select().where(database.CTag.tag_name == name).get()
            )
            tag.text = text
            tag.embed_title = title
            tag.save()
            await ctx.send(f"Tag {tag.tag_name} has been modified successfully.")

        except peewee.DoesNotExist:
            try:
                database.db.connect(reuse_if_open=True)
                tag: database.CTag = database.CTag.create(
                    tag_name=name, embed_title=title, text=text
                )
                tag.save()
                await ctx.send(f"Tag {tag.tag_name} has been created successfully.")

            except peewee.IntegrityError:
                await ctx.send("That tag name is already taken!")

        finally:
            database.db.close()

    @commands.command(aliases=["delc", "cp"])
    @commands.has_any_role(
        844013914609680384, "Head Moderator", "Senior Mod", "Moderator"         # 844013914609680384: Secret Service Admin role in 'MAIN_ID.g_main'
    )
    async def deletec(self, ctx, name):
        """Deletes a tag"""

        try:
            database.db.connect(reuse_if_open=True)
            try:
                name = int(name)
                tag = self.get_by_index(name)
            except ValueError:
                tag: database.CTag = (
                    database.CTag.select().where(database.CTag.tag_name == name).get()
                )
            tag.delete_instance()
            await ctx.send(f"{tag.tag_name} has been deleted.")

        except peewee.DoesNotExist:
            await ctx.send("Tag not found, please try again.")

        finally:
            database.db.close()

    @commands.command(aliases=["lc"])
    async def listc(self, ctx, page=1):
        """
        Lists all tags in the database
        """

        def _get_end(page_size: int):
            database.db.connect(reuse_if_open=True)
            tags: int = database.CTag.select().count()
            return math.ceil(tags / 10)

        async def populate_embed(embed: discord.Embed, page: int):
            """
            Used to populate the embed in listtag command
            """

            tag_list = ""
            embed.clear_fields()

            database.db.connect(reuse_if_open=True)
            if database.CTag.select().count() == 0:
                tag_list = "No tags found"

            for i, tag in enumerate(database.CTag.select().paginate(page, 10)):
                tag_list += f"{i+1+(10*(page-1))}. {tag.tag_name}\n"

            embed.add_field(name=f"Page {page}", value=tag_list)
            database.db.close()

            return embed

        embed = discord.Embed(title="Tag List")
        embed = await common.paginate_embed(
            self.bot, ctx, embed, populate_embed, _get_end(10), page=page
        )


async def setup(bot):
    await bot.add_cog(CTag(bot))
