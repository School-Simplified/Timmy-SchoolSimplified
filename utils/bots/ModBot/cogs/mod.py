import math

import peewee
import discord
from core import common, database
from core.common import hexColors, Emoji
from discord.ext import commands


class PunishmentTag(commands.Cog):
    """Moderation commands"""

    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = "Moderation"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="modshield", id=957316915158728827)

    @staticmethod
    def get_by_index(index):
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
        except peewee.DoesNotExist:
            await ctx.send("Tag not found, please try again.")
        finally:
            database.db.close()

    @commands.command(aliases=["newp"])
    @commands.has_any_role(
        844013914609680384, "Head Moderator", "Senior Mod", "Moderator"
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
        except peewee.DoesNotExist:
            try:
                database.db.connect(reuse_if_open=True)
                tag: database.PunishmentTag = database.PunishmentTag.create(
                    tag_name=name, embed_title=title, text=text
                )
                tag.save()
                await ctx.send(f"Tag {tag.tag_name} has been created successfully.")
            except peewee.IntegrityError:
                await ctx.send("That tag name is already taken!")
        finally:
            database.db.close()

    @commands.command(aliases=["delp", "dp"])
    @commands.has_any_role(
        844013914609680384, "Head Moderator", "Senior Mod", "Moderator"
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
        except peewee.DoesNotExist:
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

    @commands.command(aliases=["find"])
    @commands.has_any_role(
        "Moderator", "Mod", "Senior Mod", "Head Mod", 844013914609680384, "HR"
    )
    async def info(
            self, ctx: commands.Context, user: commands.Greedy[discord.User] = []
    ):
        for user in user:
            user: discord.User = user

            value = None
            typeval = None
            banreason = None

            embed = discord.Embed(
                title="Queued Query",
                description=f"I have started a new query for {user.display_name}",
                color=discord.Color.gold(),
            )
            embed.set_footer(text="This may take a moment.")
            msg = await ctx.send(embed=embed)

            member = ctx.guild.get_member(user.id)
            if member is None:
                banEntry = await ctx.guild.fetch_ban(user)

                if banEntry is not None:
                    value = Emoji.deny
                    typeval = "Banned"
                    banreason = banEntry.reason

                else:
                    value = Emoji.question
                    typeval = "Not in the Server"

            else:
                value = Emoji.confirm
                typeval = "In the Server"

            if banreason is None:
                embed = discord.Embed(
                    description=f"`ID: {user.id}` | {user.mention} found with the nickname: **{user.display_name}**\u0020",
                    color=discord.Color.green(),
                )
                embed.set_author(
                    name={user.name}, icon_url=user.avatar.url, url=user.avatar.url
                )
                embed.add_field(
                    name="Membership Status", value=f"\u0020{value} `{typeval}`"
                )

            else:
                embed = discord.Embed(
                    description=f"`ID: {user.id}` | {user.mention} found with the nickname: {user.display_name}\u0020",
                    color=discord.Color.green(),
                )
                embed.set_author(
                    name={user.name}, icon_url=user.avatar.url, url=user.avatar.url
                )
                embed.add_field(
                    name="Membership Status",
                    value=f"\u0020{value} `{typeval}`\n{Emoji.space}{Emoji.barrow}**Ban Reason:** {banreason}",
                )

            await msg.edit(embed=embed)

    @info.error
    async def info_error(self, ctx, error):
        if isinstance(error, (commands.UserNotFound, commands.errors.UserNotFound)):
            embed = discord.Embed(
                title="User Not Found",
                description="Try using an actual user next time? :(",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)

        elif isinstance(
                error,
                (commands.MissingRequiredArgument, commands.errors.MissingRequiredArgument),
        ):
            embed = discord.Embed(
                title="User Not Found",
                description="Try using an actual user next time? :(",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(PunishmentTag(bot))
