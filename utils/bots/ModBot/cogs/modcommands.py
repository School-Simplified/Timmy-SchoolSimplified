import discord
from discord.ext import commands
from core.common import Emoji
import difflib


class User(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            int(argument)
        except ValueError:
            try:
                member_converter = commands.UserConverter()
                member = await member_converter.convert(ctx, argument)
            except commands.UserNotFound:
                member = discord.utils.find(
                    lambda m: m.name.lower().startswith(argument), self.bot.users
                )
            if member is None:
                raise commands.UserNotFound(argument)
        else:
            try:
                member_converter = commands.UserConverter()
                user = await member_converter.convert(ctx, argument)
            except commands.UserNotFound:
                user = discord.utils.find(
                    lambda m: m.name.lower().startswith(argument), ctx.guild.members
                )
            if user is None:
                raise commands.UserNotFound(argument)

        return member


class InfoCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["find"])
    @commands.has_any_role(
        "Moderator", "Mod", "Senior Mod", "Head Mod", "Secret Service"
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


def setup(bot):
    bot.add_cog(InfoCMD(bot))
