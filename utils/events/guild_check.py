import discord
from discord.ext import commands

from core import database
from core.common import Others


class GuildCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """
        This event triggers when the bot joins a guild; Used to verify if the guild is approved.
        """
        query = database.AuthorizedGuilds.select().where(
            database.AuthorizedGuilds.guildID == guild.id
        )
        if not query.exists():
            embed = discord.Embed(
                title="Unable to join guild!",
                description="This guild is not authorized to use Timmy!",
                color=discord.Color.brand_red(),
            )
            embed.set_thumbnail(url=Others.timmy_dog_png)
            embed.set_footer(text="Please contact an IT administrator for help.")
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(embed=embed)
                    break
            await guild.leave()
        else:
            query = query.get()
            embed = discord.Embed(
                title="Guild Authorized!",
                description=f"This guild was authorized by <@{query.authorizedUserID}>.",
                color=discord.Color.brand_green(),
            )
            embed.set_thumbnail(url=Others.timmy_dog_png)
            embed.set_footer(text="Contact an IT administrator for any questions.")
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(embed=embed)
                    break


async def setup(bot: commands.Bot):
    await bot.add_cog(GuildCheck(bot))
