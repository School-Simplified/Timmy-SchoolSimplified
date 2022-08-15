from discord.ext import commands


class DeprecatedRegularCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["f"])
    async def filters(self, ctx):
        return

    @commands.command()
    async def Fmodify(self, ctx):
        return

    @commands.group(aliases=["pre"])
    async def prefix(self, ctx):
        return

    @commands.group(aliases=["cog"])
    async def cogs(self, ctx):
        return

    @commands.command(name="gitpull")
    async def _gitpull(self, ctx):
        return

    @commands.group()
    async def w(self, ctx):
        return

    @commands.command(aliases=["ttc", "tictactoe"])
    async def tic(self, ctx):
        return

    @commands.command()
    async def suggest(self, ctx):
        return

    @commands.command(aliases=["donation"])
    async def donate(self, ctx):
        return

    @commands.command()
    async def help(self, ctx):
        return

    @commands.command()
    async def role(self, ctx):
        return

    @commands.command()
    async def clubping(self, ctx):
        return

    @commands.command()
    async def say(self, ctx):
        return

    @commands.command()
    async def sayvc(self, ctx):
        return

    @commands.command(aliases=["punishment"])
    async def p(self, ctx):
        return

    @commands.command(aliases=["newp"])
    async def pmod(self, ctx):
        return

    @commands.command(aliases=["delp", "dp"])
    async def deletep(self, ctx):
        return

    @commands.command(aliases=["ltag"])
    async def listtag(self, ctx):
        return

    @commands.command(aliases=["find"])
    async def info(self, ctx):
        return

    @commands.command()
    async def send_mgm_embed(self, ctx):
        return

    @commands.command()
    async def leadershipPost(self, ctx):
        return

    @commands.command(name="webcommission", aliases=["wc"])
    async def webcommission(self, ctx):
        return

    @commands.command()
    async def webcommission_list(self, ctx):
        return

    @commands.command()
    async def ticketdropdown(self, ctx):
        return

    @commands.command(name="schedule")
    async def schedule(self, ctx):
        return

    @commands.command()
    async def startmusic(self, ctx):
        return

    @commands.command()
    async def startgame(self, ctx):
        return

    @commands.command()
    async def startyt(self, ctx):
        return

    @commands.command()
    async def rename(self, ctx):
        return

    @commands.command()
    async def end(self, ctx):
        return

    @commands.command()
    async def forceend(self, ctx):
        return

    @commands.command()
    async def lock(self, ctx):
        return

    @commands.command()
    async def settutor(self, ctx):
        return

    @commands.command()
    async def unlock(self, ctx):
        return

    @commands.command()
    async def permit(self, ctx):
        return

    @commands.command()
    async def voicelimit(self, ctx):
        return

    @commands.command()
    async def disconnect(self, ctx):
        return

    @commands.command(aliases=["start"])
    async def startVC(self, ctx):
        return

    @commands.command()
    async def close(self, ctx: commands.Context):
        return

    @commands.command()
    async def sendCHTKTView(self, ctx):
        return

    @commands.command()
    async def pasteGSuiteButton(self, ctx):
        return

async def setup(bot):
    await bot.add_cog(DeprecatedRegularCommands(bot))