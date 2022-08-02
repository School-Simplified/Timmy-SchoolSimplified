import asyncio
import sys
import time
from datetime import timedelta
from typing import List, Literal

import discord
import psutil
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from google.cloud import texttospeech
from sentry_sdk import Hub

from core import database
from core.checks import is_botAdmin, is_botAdmin2
from core.common import (
    TechID,
    Emoji,
    NitroConfirmFake,
    SelectMenuHandler,
    Colors,
    Others,
    MainID,
)
from core.common import access_secret


class TicTacToeButton(discord.ui.Button["TicTacToe"]):
    def __init__(self, x: int, y: int, xUser: discord.User, yUser: discord.User):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.xUser = xUser

        self.y = y
        self.yUser = yUser

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return
        if view.current_player == view.X and self.xUser.id == interaction.user.id:
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now {self.yUser.mention}'s turn"

        elif view.current_player == view.O and self.yUser.id == interaction.user.id:
            self.style = discord.ButtonStyle.success
            self.label = "O"
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now {self.xUser.mention}'s turn"

        elif not interaction.user.id == view.current_player and interaction.user in [
            self.yUser,
            self.xUser,
        ]:
            return await interaction.response.send_message(
                f"{interaction.user.mention} It's not your turn!", ephemeral=True
            )
        else:
            return await interaction.response.send_message(
                f"{interaction.user.mention} Woah! You can't join this game "
                f"as you weren't invited, if you'd like to play you can start "
                f"a session by doing `+ttc @UserYouWannaPlayAgainst`!",
                ephemeral=True,
            )

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f"{self.xUser.mention} won!"
            elif winner == view.O:
                content = f"{self.yUser.mention} won!"
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


# This is our actual board View
class TicTacToe(discord.ui.View):
    # This tells the IDE or linter that all our children will be TicTacToeButtons
    # This is not required
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self, XPlayer, OPlayer):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        self.XPlayer = XPlayer
        self.OPlayer = OPlayer

        # Our board is made up of 3 by 3 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y, XPlayer, OPlayer))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


load_dotenv()


class MiscCMD(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.__cog_name__ = "General"
        self.bot = bot
        self.interaction = []

        self.client = Hub.current.client

        self.whitelistedRoles = [
            MainID.r_coding_club,
            MainID.r_debate_club,
            MainID.r_music_club,
            MainID.r_cooking_club,
            MainID.r_chess_club,
            MainID.r_book_club,
            MainID.r_advocacy_club,
            MainID.r_speech_club,
        ]

        self.decodeDict = {
            "['Simplified Coding Club']": 883169286665936996,
            "['Simplified Debate Club']": 883170141771272294,
            "['Simplified Music Club']": 883170072355561483,
            "['Simplified Cooking Club']": 883162279904960562,
            "['Simplified Chess Club']": 883564455219306526,
            "['Simplified Book Club']": 883162511560560720,
            "['Simplified Advocacy Club']": 883169000866070539,
            "['Simplified Speech Club']": 883170166161149983,
        }

        self.options = [
            discord.SelectOption(
                label="Simplified Coding Club", description="", emoji="💻"
            ),
            discord.SelectOption(
                label="Simplified Debate Club", description="", emoji="💭"
            ),
            discord.SelectOption(
                label="Simplified Music Club", description="", emoji="🎵"
            ),
            discord.SelectOption(
                label="Simplified Cooking Club", description="", emoji="🍱"
            ),
            discord.SelectOption(
                label="Simplified Chess Club", description="", emoji="🏅"
            ),
            discord.SelectOption(
                label="Simplified Book Club", description="", emoji="📚"
            ),
            discord.SelectOption(
                label="Simplified Advocacy Club", description="", emoji="📰"
            ),
            discord.SelectOption(
                label="Simplified Speech Club", description="", emoji="🎤"
            ),
        ]

    @property
    def display_emoji(self) -> str:
        return Emoji.schoolsimplified

    @commands.command(aliases=["ttc", "tictactoe"])
    async def tic(self, ctx: commands.Context, user: discord.User = None):
        if user is None:
            return await ctx.send(
                "lonely :(, sorry but you need a person to play against!"
            )
        elif user == self.bot.user:
            return await ctx.send("i'm good")
        elif user == ctx.author:
            return await ctx.send(
                "lonely :(, sorry but you need an actual person to play against, not yourself!"
            )

        await ctx.send(
            f"Tic Tac Toe: {ctx.author.mention} goes first",
            view=TicTacToe(ctx.author, user),
        )

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def suggest(self, ctx, suggestion):
        embed = discord.Embed(
            title="Confirmation",
            description="Are you sure you want to submit this suggestion? Creating irrelevant "
            "suggestions will warrant a blacklist and you will be subject to a "
            "warning/mute.",
            color=discord.Colour.blurple(),
        )
        embed.add_field(name="Suggestion Collected", value=suggestion)
        embed.set_footer(
            text="Double check this suggestion || MAKE SURE THIS SUGGESTION IS RELATED TO THE BOT, NOT THE DISCORD "
            "SERVER! "
        )

        message = await ctx.send(embed=embed)
        reactions = ["✅", "❌"]
        for emoji in reactions:
            await message.add_reaction(emoji)

        def check2(reaction, user):
            return user == ctx.author and (
                str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌"
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=150.0, check=check2
            )
            if str(reaction.emoji) == "❌":
                await ctx.send("Okay, I won't send this.")
                await message.delete()
                return
            else:
                await message.delete()
                guild = self.bot.get_guild(TechID.g_tech)
                channel = guild.get_channel(TechID.ch_tracebacks)

                embed = discord.Embed(
                    title="New Suggestion!",
                    description=f"User: {ctx.author.mention}\nChannel: {ctx.channel.mention}",
                    color=discord.Colour.blurple(),
                )
                embed.add_field(name="Suggestion", value=suggestion)

                await channel.send(embed=embed)
                await ctx.send(
                    "I have sent in the suggestion! You will get a DM back depending on its status!"
                )

        except asyncio.TimeoutError:
            await ctx.send(
                "Looks like you didn't react in time, please try again later!"
            )

    @suggest.error
    async def suggest_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            msg = "You can't suggest for: `{} minutes and {} seconds`".format(
                round(m), round(s)
            )
            await ctx.send(msg)

        else:
            raise error

    @commands.command(aliases=["donation"])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def donate(self, ctx: commands.Context):
        timmyDonation_png = discord.File(
            Others.timmy_donation_path, filename=Others.timmy_donation_png
        )

        embedDonate = discord.Embed(
            color=Colors.ss_blurple,
            title=f"Donate",
            description=f"Thank you for your generosity in donating to School Simplified. "
            f"We do not charge anything for our services, and your support helps to further our mission "
            f"to *empower the next generation to revolutionize the future through learning*."
            f"\n\n**Donate here: https://schoolsimplified.org/donate**",
        )
        embedDonate.set_footer(text="Great thanks to all our donors!")
        embedDonate.set_thumbnail(url=f"attachment://{Others.timmy_donation_png}")
        await ctx.send(embed=embedDonate, file=timmyDonation_png)

    @commands.command()
    @is_botAdmin
    async def pingmasa(self, ctx, *, msg=None):
        masa = self.bot.get_user(736765405728735232)
        if msg is not None:
            await ctx.send(masa.mention + f" {msg}")
        else:
            await ctx.send(masa.mention)

    @app_commands.command(description="Ban a user from a specific server feature.")
    @app_commands.describe(
        user="The user to service ban",
        role="What should the user be banned from?",
        reason="Why is the user being banned?",
    )
    @app_commands.guilds(MainID.g_main)
    async def miscban(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        role: Literal["debate", "count", "ticket"],
        reason: str,
    ):
        modRole = discord.utils.get(interaction.user.guild.roles, id=MainID.r_moderator)
        if modRole not in interaction.user.roles:
            return await interaction.response.send_message(
                f"{interaction.user.mention} You do not have the required permissions to use this command.",
                ephemeral=True,
            )
        roleName = {
            "debate": [MainID.r_debate_ban, "Debate"],
            "count": [MainID.r_count_ban, "Count"],
            "ticket": [MainID.r_ticket_ban, "Ticket"],
        }[role]

        role = discord.utils.get(interaction.user.guild.roles, id=roleName[0])
        if role not in user.roles:
            updateReason = f"{roleName[1]} Ban requested by {interaction.user.name} | Reason: {reason}"
            await user.add_roles(role, reason=updateReason)
            await interaction.response.send_message(
                f"{interaction.user.mention} {user.mention} has been banned from {roleName[1]}."
            )
        else:
            updateReason = f"{roleName[1]} Unban requested by {interaction.user.name} | Reason: {reason}"
            await user.remove_roles(role, reason=updateReason)
            await interaction.response.send_message(
                f"{interaction.user.mention} {user.mention} has been unbanned from {roleName[1]}."
            )

    @commands.command()
    async def join(self, ctx, *, vc: discord.VoiceChannel):
        await vc.connect()
        await ctx.send("ok i did join")

    @commands.command()
    @is_botAdmin
    async def error_test(self, ctx):
        """This command is used to test error handling"""
        raise discord.DiscordException

    @commands.command()
    async def ping(self, ctx):
        database.db.connect(reuse_if_open=True)

        q: database.Uptime = (
            database.Uptime.select().where(database.Uptime.id == 1).get()
        )
        current_time = float(time.time())
        difference = int(round(current_time - float(q.UpStart)))
        text = str(timedelta(seconds=difference))

        pingembed = discord.Embed(
            title="Pong! ⌛",
            color=discord.Colour.gold(),
            description="Current Discord API Latency",
        )
        pingembed.set_author(
            name="Timmy", url=Others.timmy_laptop_png, icon_url=Others.timmy_happy_png
        )
        pingembed.add_field(
            name="Ping & Uptime:",
            value=f"```diff\n+ Ping: {round(self.bot.latency * 1000)}ms\n+ Uptime: {text}\n```",
        )

        pingembed.add_field(
            name="System Resource Usage",
            value=f"```diff\n- CPU Usage: {psutil.cpu_percent()}%\n- Memory Usage: {psutil.virtual_memory().percent}%\n```",
            inline=False,
        )
        pingembed.add_field(name="Status Page", value="[Click here](https://status.timmy.ssimpl.org/)")
        pingembed.set_footer(
            text=f"TimmyOS Version: {self.bot.version}", icon_url=ctx.author.avatar.url
        )

        await ctx.send(embed=pingembed)

        database.db.close()

    @commands.command()
    async def help(self, ctx):
        # view = discord.ui.View()
        # emoji = Emoji.timmyBook
        # view.add_item(
        #     ButtonHandler(
        #         style=discord.ButtonStyle.green,
        #         url="https://timmy.schoolsimplified.org",
        #         disabled=False,
        #         label="Click Here to Visit the Documentation!",
        #         emoji=emoji,
        #     )
        # )
        #
        # embed = discord.Embed(title="Help Command", color=discord.Colour.gold())
        # embed.add_field(
        #     name="Documentation Page",
        #     value="Click the button below to visit the documentation!",
        # )
        # embed.set_footer(text="DM SpaceTurtle#0001 for any questions or concerns!")
        # embed.set_thumbnail(url=Others.timmyBook_png)
        await ctx.send("The help command is now a slash command! Use `/help` for help.")

    @commands.command()
    async def nitro(self, ctx: commands.Context):
        await ctx.message.delete()

        embed = discord.Embed(
            title="A WILD GIFT APPEARS!",
            description="**Nitro:**\nExpires in 48 hours.",
            color=Colors.dark_gray,
        )
        embed.set_thumbnail(url=Others.nitro_png)
        await ctx.send(embed=embed, view=NitroConfirmFake())

    @commands.command()
    @is_botAdmin2
    async def kill(self, ctx):
        embed = discord.Embed(
            title="Confirm System Abortion",
            description="Please react with the appropriate emoji to confirm your choice!",
            color=discord.Colour.dark_orange(),
        )
        embed.add_field(
            name="WARNING",
            value="Please not that this will kill the bot immediately and it will not be online unless a "
            "developer manually starts the proccess again!"
            "\nIf you don't respond in 5 seconds, the process will automatically abort.",
        )
        embed.set_footer(
            text="Abusing this system will subject your authorization removal, so choose wisely you fucking pig."
        )

        message = await ctx.send(embed=embed)

        reactions = ["✅", "❌"]
        for emoji in reactions:
            await message.add_reaction(emoji)

        def check2(reaction, user):
            return user == ctx.author and (
                str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌"
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=5.0, check=check2
            )
            if str(reaction.emoji) == "❌":
                await ctx.send("Aborted Exit Process")
                await message.delete()
                return

            else:
                await message.delete()
                database.db.connect(reuse_if_open=True)
                NE = database.AdminLogging.create(
                    discordID=ctx.author.id, action="KILL"
                )
                NE.save()
                database.db.close()

                if self.client is not None:
                    self.client.close(timeout=2.0)

                embed = discord.Embed(
                    title="Initiating System Exit...",
                    description="Goodbye!",
                    color=discord.Colour.dark_orange(),
                )
                message = await ctx.send(embed=embed)

                sys.exit(0)

        except asyncio.TimeoutError:
            await ctx.send(
                "Looks like you didn't react in time, automatically aborted system exit!"
            )
            await message.delete()

    @commands.command()
    @commands.has_role(MainID.r_club_president)
    async def role(
        self,
        ctx: commands.Context,
        users: commands.Greedy[discord.Member],
        roles: commands.Greedy[discord.Role],
    ):
        """
        Gives an authorized role to every user provided.

        Requires:
            Club President Role to be present on the user.

        Args:
            ctx (commands.Context): Context
            users (commands.Greedy[discord.User]): List of Users
            roles (commands.Greedy[discord.Role]): List of Roles
        """

        embed = discord.Embed(
            title="Starting Mass Role Function",
            description="Please wait until I finish the role operation, you'll see this message update when I am "
            "finished!",
            color=discord.Color.gold(),
        )

        msg = await ctx.send(embed=embed)

        for role in roles:
            if role.id not in self.whitelistedRoles:
                await ctx.send(
                    f"Role: `{role}` is not whitelisted for this command, removing `{role}`."
                )

                roles = [value for value in roles if value != role]
                break

        for user in users:
            for role in roles:
                await user.add_roles(
                    role, reason=f"Mass Role Operation requested by {ctx.author.name}."
                )

        embed = discord.Embed(
            title="Mass Role Operation Complete",
            description=f"I have given `{str(len(users))}` users `{str(len(roles))}` roles.",
            color=discord.Color.green(),
        )

        UserList = []
        RoleList = []

        for user in users:
            UserList.append(user.mention)
        for role in roles:
            RoleList.append(role.mention)

        UserList = ", ".join(UserList)
        RoleList = ", ".join(RoleList)

        embed.add_field(
            name="Detailed Results",
            value=f"{Emoji.person}: {UserList}\n\n{Emoji.activity}: {RoleList}\n\n**Status:**  {Emoji.confirm}",
        )
        embed.set_footer(text="Completed Operation")

        await msg.edit(embed=embed)

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.role)
    async def clubping(self, ctx: commands.Context, *, message=""):
        view = discord.ui.View()
        view.add_item(
            SelectMenuHandler(
                self.options,
                place_holder="Select a club to ping!",
                select_user=ctx.author,
            )
        )

        msg = await ctx.send("Select a role you want to ping!", view=view)
        await view.wait()
        await msg.delete()
        ViewResponse = str(view.children[0].values)
        RoleID = self.decodeDict[ViewResponse]
        await ctx.send(f"<@&{RoleID}>\n{message}")

    @app_commands.command(description="Play a game of TicTacToe with someone!")
    @app_commands.describe(user="The user you want to play with.")
    async def tictactoe(self, interaction: discord.Interaction, user: discord.Member):
        if user is None:
            return await interaction.response.send_message(
                "lonely :(, sorry but you need a person to play against!"
            )
        elif user == self.bot.user:
            return await interaction.response.send_message("i'm good.")
        elif user == interaction.user:
            return await interaction.response.send_message(
                "lonely :(, sorry but you need an actual person to play against, not yourself!"
            )

        await interaction.response.send_message(
            f"Tic Tac Toe: {interaction.user.mention} goes first",
            view=TicTacToe(interaction.user, user),
        )

    @commands.command()
    @is_botAdmin
    async def say(self, ctx, *, message):
        NE = database.AdminLogging.create(
            discordID=ctx.author.id, action="SAY", content=message
        )
        NE.save()

        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    @is_botAdmin
    async def sayvc(self, ctx, *, text=None):
        await ctx.message.delete()

        if not text:
            # We have nothing to speak
            await ctx.send(
                f"Hey {ctx.author.mention}, I need to know what to say please."
            )
            return

        vc = ctx.voice_client  # We use it more then once, so make it an easy variable
        if not vc:
            # We are not currently in a voice channel
            await ctx.send(
                "I need to be in a voice channel to do this, please use the connect command."
            )
            return

        NE = database.AdminLogging.create(
            discordID=ctx.author.id, action="SAYVC", content=text
        )
        NE.save()

        # Lets prepare our text, and then save the audio file
        TTSClient = texttospeech.TextToSpeechClient(
            credentials=access_secret("ttscreds", True, 2)
        )

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = TTSClient.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with open("text.mp3", "wb") as out:
            out.write(response.audio_content)

        try:
            vc.play(
                discord.FFmpegPCMAudio("text.mp3"),
                after=lambda e: print(f"Finished playing: {e}"),
            )

            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = 1

        except discord.ClientException as e:
            await ctx.send(f"A client exception occurred:\n`{e}`")

        except TypeError as e:
            await ctx.send(f"TypeError exception:\n`{e}`")


async def setup(bot: commands.Bot):
    await bot.add_cog(MiscCMD(bot))
