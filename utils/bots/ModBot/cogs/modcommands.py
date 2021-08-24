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
                    lambda m: m.name.lower().startswith(argument),
                    self.bot.users
                )
            if member is None:
                raise commands.UserNotFound(argument)
        else:
            try:
                member_converter = commands.UserConverter()
                user = await member_converter.convert(ctx, argument)
            except commands.UserNotFound:
                user = discord.utils.find(
                    lambda m: m.name.lower().startswith(argument),
                    ctx.guild.members
                )
            if user is None:
                raise commands.UserNotFound(argument)

        return member

class InfoCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['find'])
    @commands.has_any_role("Mod", "Senior Mod", "Head Mod")
    async def info(self, ctx, user: commands.Greedy[discord.User] = []):
        for user in user:
            #name = await User.convert(self, ctx, user)

            value = None
            typeval = None
            banreason = None

            embed = discord.Embed(title = "Queued Query", description = f"I have started a new query for {user.display_name}", color = discord.Color.gold())
            embed.set_footer(text = "This may take a moment.")
            msg = await ctx.send(embed = embed)

            member = ctx.guild.get_member(user.id)
            if member == None:
                banEntry = await ctx.guild.fetch_ban(user)

                if banEntry != None:
                    value = "<:deny:860926229335375892>"
                    typeval = "Banned"
                    banreason = banEntry.reason

                else:
                    value = "<:question~1:861794223027519518>"
                    typeval = "Not in the Server"
                    
            else:
                value = "<:confirm:860926261966667806>"
                typeval = "In the Server"


            if banreason == None:
                embed = discord.Embed(description = f"`ID: {user.id}` | {user.mention} found with the nickname: **{user.display_name}**\u0020", color = discord.Color.green())
                embed.set_author(name = {user.name}, icon_url = user.avatar_url, url = user.avatar_url)
                embed.add_field(name = "Membership Status", value = f"\u0020{value} `{typeval}`")


            else:
                embed = discord.Embed(description = f"`ID: {user.id}` | {user.mention} found with the nickname: {user.display_name}\u0020", color = discord.Color.green())
                embed.set_author(name = {user.name},icon_url = user.avatar_url, url = user.avatar_url)
                embed.add_field(name = "Membership Status", value = f"\u0020{value} `{typeval}`\n{Emoji.space}{Emoji.barrow}**Ban Reason:** {banreason}")
            await msg.edit(embed = embed)
    
    @info.error
    async def info_error(self, ctx, error):
        if isinstance(error, (commands.UserNotFound, commands.errors.UserNotFound)):
            embed = discord.Embed(title = "User Not Found", description = "Try using an actual user next time? :(", color = discord.Color.red())
            await ctx.send(embed = embed)
        
        elif isinstance(error, (commands.MissingRequiredArgument, commands.errors.MissingRequiredArgument)):
            embed = discord.Embed(title = "User Not Found", description = "Try using an actual user next time? :(", color = discord.Color.red())
            await ctx.send(embed = embed)
        else:
            raise error

def setup(bot):
    bot.add_cog(InfoCMD(bot))
