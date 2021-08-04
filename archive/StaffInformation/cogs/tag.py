import asyncio
import math

import discord
from core import common, database
from discord.ext import commands
from discord.ext.commands.core import command


class Tags(commands.Cog):
    """Commands related to our dynamic tag system."""

    def __init__(self, bot):
        self.bot = bot

    def get_by_index(self, index):
        for i, t in enumerate(database.Tag.select()):
            if i+1 == index:
                return t

    @commands.command()
    async def ntag(self, ctx, embedTitle, URL, *, text):
        def check(m):
            return m.content is not None and m.channel == ctx.channel and m.author is not self.bot.user and m.author == ctx.author

        await ctx.send("Designate this tag a tagname, make it short and one word.")
        tagName = await self.bot.wait_for('message', check=check)

        try:
            query = database.Tag.create(tag_name = tagName, embed_title = embedTitle, imageURL = URL, text = text)
        except Exception as e:
            await ctx.send(f"ERROR:\n{e}")
        else:
            await ctx.send(f"Successfully created Tag with ID {query.id}")

        
    @commands.command()
    async def deltag(self, ctx, idOrName: str):
        try:
            SQ = int(idOrName)
        except ValueError:
            query = database.Tag.select().where(tag_name=idOrName)
        else:
            query = database.Tag.select().where(id = SQ)
        if query.exists():
            query = query.get()
            query.delete_instance()

            await ctx.send("Successfully deleted tag!")
        else:
            return await ctx.send(f"No tag with ID/Name {idOrName}")

    @commands.command(aliases=['ltag'])
    async def listtag(self, ctx, page=1):
        """List all tags in the database"""
        def get_end(page_size: int):
            database.db.connect(reuse_if_open=True)
            tags: int = database.Tag.select().count()
            return math.ceil(tags/10)

        async def populate_embed(embed: discord.Embed, page: int):
            """Used to populate the embed in listtag command"""
            tag_list = ""
            embed.clear_fields()
            database.db.connect(reuse_if_open=True)
            if database.Tag.select().count() == 0:
                tag_list = "No tags found"
            for i, tag in enumerate(database.Tag.select().paginate(page, 10)):
                tag_list += f"{i+1+(10*(page-1))}. {tag.tag_name}\n"
            embed.add_field(name=f"Page {page}", value=tag_list)
            database.db.close()
            return embed

        embed = discord.Embed(title="Tag List")
        embed = await common.paginate_embed(self.bot, ctx, embed, populate_embed, get_end(10), page=page)


def setup(bot):
    bot.add_cog(Tags(bot))
