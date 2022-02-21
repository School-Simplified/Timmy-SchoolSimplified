import asyncio
import discord
from discord.ext import commands
from core.common import hexColors as hex
from core.common import MAIN_ID, STAFF_ID, DIGITAL_ID, TECH_ID, MKT_ID, TUT_ID, HR_ID


class VotingBot(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.acceptedGuilds = [MAIN_ID.g_main, STAFF_ID.g_staff, DIGITAL_ID.g_digital, TECH_ID.g_tech, MKT_ID.g_mkt, TUT_ID.g_tut, HR_ID.g_hr]

    """
    vote create: creates a voting
        1. Server (it will automatically get send in announcement channel)
        2. Duration
        3. Text
        4. Options (would be buttons)

        - Embed displays a timestamp and notes that the vote can't get undo
        - When someone voted, he gets a ephemeral message, that the person has voted on X
        - If the person votes again, he gets an ephemeral message, that he already voted

    vote list: lists every voting (finished and ongoing votings)
        - Votings have an unique ID
        - Votings have a status: ongoing or expired                                            
        - Votings have expiration date or when it expired
        - Votings have user, who created the voting
        - Channel and server

    vote stats <ID>: shows stats of the voting
        - ID
        - status
        - expiration date or when it expired
        - user, who created the voting
        - channel and server
        - Text of the voting
        - Options of the voting
        - Diagram (on ongoing and on expired votings)
        
        
    vote end <ID>: Immediately ends a voting
    
    vote delete <ID>: Deletes a voting and ends the voting if ongoing
    """

    @commands.group(invoke_without_command=True)
    @commands.has_any_role()
    async def vote(self, ctx):
        pass

    @vote.command()
    async def create(self, ctx: commands.Context):

        acceptedGuildsStr = ""
        for guildID in self.acceptedGuilds:
            acceptedGuild = self.bot.get_guild(guildID)
            print(f"{guildID}: {acceptedGuild}")

            acceptedGuildsStr += f"- {acceptedGuild.name} (`{acceptedGuild.id}`)\n"

        embedServer = discord.Embed(
            color=hex.ss_blurple,
            title="Create voting",
            description="Please provide the server/s (name or ID) in which the voting should get sent. Use commas (`,`) to "
                        "send it to multiple servers."
                        "\n**Accepted servers:**"
                        f"\n{acceptedGuildsStr}"
                        "\n\n**NOTE**: it will automatically send the voting into the __general announcement channel__ of "
                        "the server."
        )
        embedServer.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
        embedServer.set_footer(text="Type 'cancel' to cancel | Timeout after 60s")
        msgSetup = await ctx.send(embed=embedServer)


        def check(messageCheck: discord.Message):
            return messageCheck.channel == ctx.channel and messageCheck.author == ctx.author

        index = 0
        while True:
            try:
                msgResponse: discord.Message = await self.bot.wait_for('message', check=check, timeout=60)
            except asyncio.TimeoutError:
                embedTimeout = discord.Embed(
                    color=hex.red_error,
                    title="Create voting",
                    description="Setup canceled due to timeout.",

                )
                embedTimeout.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                embedTimeout.set_footer(text="Use 'vote create' to start again")
                await msgSetup.edit(embed=embedTimeout)

            else:
                msgContent = msgResponse.content

                if msgContent.lower() == "cancel":
                    embedCancel = discord.Embed(
                        color=hex.red_cancel,
                        title="Create voting",
                        description="Setup canceled."
                    )
                    embedCancel.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                    embedCancel.set_footer(text="Use 'vote create' to start again")
                    await msgSetup.edit(embed=embedCancel)
                    break

                if index == 0:

                    if "," in msgContent:
                        guilds = []

                        guildsStrList = msgContent.split(",")
                        for guildStr in guildsStrList:

                            stripGuildStr = guildStr.strip()
                            guildsStrList[guildsStrList.index(guildStr)] = stripGuildStr

                            if stripGuildStr.isdigit():
                                guild = self.bot.get_guild(int(stripGuildStr))
                                guilds.append(guild)

                            else:
                                guild = discord.utils.get(self.bot.guilds, name=stripGuildStr)

                            guilds.append(guild)

                        if any(guildInList is None for guildInList in guilds):
                            embedNotFound = discord.Embed(
                                color=hex.red_error,
                                title="Create voting",
                                description=f"Couldn't find one or more of the given guilds, please try again."
                            )
                            embedNotFound.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                            embedNotFound.set_footer(text="Use 'vote create' to start again")
                            msgNotFound = await ctx.send(embed=embedNotFound)
                            await msgNotFound.delete(delay=5)
                            continue
                        print(guilds)

                    else:
                        guildStr = msgContent.strip()

                        if guildStr.isdigit():
                            guild = self.bot.get_guild(int(msgContent))
                        else:
                            guild = discord.utils.get(self.bot.guilds, name=guildStr)

                        if guild is None:
                            embedNotFound = discord.Embed(
                                color=hex.red_error,
                                title="Create voting",
                                description=f"Couldn't found one or more of the given guilds, please try again."
                            )
                            embedNotFound.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                            embedNotFound.set_footer(text="Use 'vote create' to start again")
                            msgNotFound = await ctx.send(embed=embedNotFound)
                            await msgNotFound.delete(delay=5)
                            continue
                        print(guild)
                    index += 1



def setup(bot):
    bot.add_cog(VotingBot(bot))
