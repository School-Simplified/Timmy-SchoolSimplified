import datetime
from datetime import datetime

import discord
from discord.ext import commands

from core.common import MainID


class MessageLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = [MainID.ch_senior_mods, MainID.ch_moderators]

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        if int(message.channel.id) in self.channels:
            embed = discord.Embed(
                title="Deleted Message Log",
                description=f"**{message.author.mention}** sent this in **{message.channel.mention}**",
                color=discord.Color.red(),
            )

            member = message.guild.get_member(message.author.id)

            embed.set_author(name=message.author.name, icon_url=member.avatar.url)

            embed.add_field(name="Message", value=message.content, inline=True)

            val = datetime.today().strftime("%I:%M %p")

            embed.set_footer(
                text=f"Author: {message.author.id} | Message ID: {message.id} • Today at {val}"
            )

            channel = self.bot.get_channel(MainID.ch_mod_logs)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        if int(before.channel.id) in self.channels:
            embed: discord.Embed = discord.Embed(
                title=f"Editted Message Log",
                description=f"**{before.author.mention}** sent this in **{before.channel.mention}**",
                color=discord.Color.gold(),
            )

            member = before.guild.get_member(before.author.id)

            embed.set_author(name=before.author.name, icon_url=member.avatar.url)
            embed.add_field(name="Before", value=before.content)
            embed.add_field(name="After", value=after.content, inline=False)

            val = datetime.today().strftime("%I:%M %p")

            embed.set_footer(
                text=f"Author: {before.author.id} | Message ID: {before.id} • Today at {val}"
            )

            channel = self.bot.get_channel(MainID.ch_mod_logs)
            await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(MessageLogs(bot))
