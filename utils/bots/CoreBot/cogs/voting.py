import asyncio
import discord
from discord.ext import commands
from core.checks import isnot_hostTimmyA
from core.common import hexColors as hex
from core.common import Emoji as e
from core.common import MAIN_ID, STAFF_ID, DIGITAL_ID, TECH_ID, MKT_ID, TUT_ID, CH_ID, HR_ID


class VotingBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.acceptedGuilds = [
            MAIN_ID.g_main,
            STAFF_ID.g_staff,
            DIGITAL_ID.g_digital,
            TECH_ID.g_tech,
            MKT_ID.g_mkt,
            TUT_ID.g_tut,
            CH_ID,
            HR_ID.g_hr,
        ]

    """
    vote create: creates a voting
        1. Server (it will automatically get send in announcement channel)
        2. Text
        3. Options (would be buttons)
        4. Durations


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
    @commands.has_any_role() # TODO
    async def vote(self, ctx):
        pass

    @vote.command()
    @isnot_hostTimmyA
    async def create(self, ctx: commands.Context):

        acceptedGuildsStr = ""
        for guildID in self.acceptedGuilds:
            acceptedGuild = self.bot.get_guild(guildID)
            print(f"{guildID}: {acceptedGuild}")

            acceptedGuildsStr += f"- {acceptedGuild.name} (`{acceptedGuild.id}`)\n"

        embedServer = discord.Embed(
            color=hex.ss_blurple,
            title="Create voting",
            description="Please provide the server/s (name or ID) in which the voting should get sent. You can send "
            "it to multiple servers by separating the servers with commas (`,`)."
            "\n**Accepted servers:**"
            f"\n{acceptedGuildsStr}"
            "\n\n**NOTE**: it will automatically send the voting into the __general announcement channel__ of "
            "the server.",
        )
        embedServer.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
        embedServer.set_footer(text="Type 'cancel' to cancel | Timeout after 60s")
        msgSetup = await ctx.send(embed=embedServer)

        def check(messageCheck: discord.Message):
            return (
                messageCheck.channel == ctx.channel
                and messageCheck.author == ctx.author
            )

        guilds = []
        text = None
        options = []

        index = 0
        while True:
            try:
                msgResponse: discord.Message = await self.bot.wait_for(
                    "message", check=check, timeout=60
                )
            except asyncio.TimeoutError:
                embedTimeout = discord.Embed(
                    color=hex.red_error,
                    title="Create Voting",
                    description="Setup canceled due to timeout.",
                )
                embedTimeout.set_author(
                    name=f"{ctx.author}", icon_url=ctx.author.avatar.url
                )
                embedTimeout.set_footer(text="Use 'vote create' to start again")
                await msgSetup.edit(embed=embedTimeout)

            else:
                msgContent = msgResponse.content

                if msgContent.lower() == "cancel":
                    embedCancel = discord.Embed(
                        color=hex.red_cancel,
                        title="Create Voting",
                        description="Setup canceled."
                    )
                    embedCancel.set_author(
                        name=f"{ctx.author}", icon_url=ctx.author.avatar.url
                    )
                    embedCancel.set_footer(text="Use 'vote create' to start again")
                    await msgSetup.edit(embed=embedCancel)
                    break

                if index == 0:

                    embedNotFound = discord.Embed(
                        color=hex.red_error,
                        title="Create voting",
                        description=f"Couldn't find one or more of the given guilds, please try again."
                    )
                    embedNotFound.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                    embedNotFound.set_footer(text="Use 'vote create' to start again")

                    if "," in msgContent:

                        guildsStrList = msgContent.split(",")
                        for guildStr in guildsStrList:

                            stripGuildStr = guildStr.strip()
                            guildsStrList[guildsStrList.index(guildStr)] = stripGuildStr

                            if stripGuildStr.isdigit():
                                guild = self.bot.get_guild(int(stripGuildStr))
                                guilds.append(guild)

                            else:
                                guild = discord.utils.get(
                                    self.bot.guilds, name=stripGuildStr
                                )

                            guilds.append(guild)

                        if any(guildInList is None for guildInList in guilds):

                            msgNotFound = await ctx.send(embed=embedNotFound)
                            await msgNotFound.delete(delay=7)
                            continue

                        print(guilds)

                    else:
                        guildStr = msgContent.strip()

                        if guildStr.isdigit():
                            guild = self.bot.get_guild(int(msgContent))
                        else:
                            guild = discord.utils.get(self.bot.guilds, name=guildStr)

                        if guild is None:
                            msgNotFound = await ctx.send(embed=embedNotFound)
                            await msgNotFound.delete(delay=7)
                            continue

                        guilds.append(guild)

                    embedText = discord.Embed(
                        color=hex.ss_blurple,
                        title="Create Voting",
                        description="Please provide the text you want to add to the voting."
                        "\n\n**Example:**"
                        "\nHey everyone,"
                        "\nWhich programming language is better? Please vote now!"
                        f"\n{e.pythonLogo} Python | {e.javascriptLogo} JavaScript"
                        f"\n\n(In the example above you would choose Python of course {e.blobamused})",
                    )
                    embedText.set_author(
                        name=f"{ctx.author}", icon_url=ctx.author.avatar.url
                    )
                    embedText.set_footer(
                        text="Type 'cancel' to cancel | Timeout after 60s"
                    )
                    await msgSetup.edit(embed=embedText)

                    index += 1

                elif index == 1:
                    text = msgContent
                    print(text)

                    embedText = discord.Embed(
                        color=hex.ss_blurple,
                        title="Create Voting",
                        description="Please provide the options for the voting by separating the options with commas (`,`). "
                        "They will shown as buttons."
                        f"\n\nFrom the example on the last message, the options would be: "
                        f"{e.pythonLogo} Python, {e.javascriptLogo} JavaScript",
                    )
                    embedText.set_author(
                        name=f"{ctx.author}", icon_url=ctx.author.avatar.url
                    )
                    embedText.set_footer(
                        text="Type 'cancel' to cancel | Timeout after 60s"
                    )
                    await msgSetup.edit(embed=embedText)

                    index += 1

                elif index == 2:
                    optionsStrList = msgContent.split(",")
                    for optionStr in optionsStrList:
                        options.append(optionStr.strip())

                    print(options)

                    embedDuration = discord.Embed(
                        color=hex.ss_blurple,
                        title="Create Voting",
                        description="Please provide the duration of the voting."
                                    "\n**Example:**"
                                    "\n`2d4h5m50s` -> would be 2 days, 4 hours, 5m and 50 seconds."
                    )
                    embedDuration.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar.url)
                    embedDuration.set_footer(text="Type 'cancel' to cancel | Timeout after 60s")
                    await msgSetup.edit(embed=embedDuration)

                    index += 1

                elif index == 3:
                    pass
                    # TODO

def setup(bot):
    bot.add_cog(VotingBot(bot))