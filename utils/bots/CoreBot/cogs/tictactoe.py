from typing import List
from discord.ext import commands
import discord
from core.common import MAIN_ID


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


class TicTacToeBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ttc", "tictactoe"])
    async def tic(self, ctx: commands.Context, user: discord.User = None):
        if not ctx.channel.id == MAIN_ID.ch_commands:
            await ctx.message.delete()
            return await ctx.send(
                f"{ctx.author.mention}"
                f"\nMove to <#{MAIN_ID.ch_commands}> to play Tic Tac Toe!"
            )

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


def setup(bot):
    bot.add_cog(TicTacToeBot(bot))
