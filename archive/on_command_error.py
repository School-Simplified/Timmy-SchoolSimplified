import json
import os
import random
import traceback
from pathlib import Path

import discord
import requests
from core import database
from discord.ext import commands


def random_rgb(seed=None):
    if seed is not None:
        random.seed(seed)
    return discord.Colour.from_rgb(random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))


def stackoverflow(q):
    q = str(q)
    baseUrl = "https://stackoverflow.com/search?q="
    error = q.replace(" ","+")
    error = error.replace(".","")
    stackURL = baseUrl + error 
    return stackURL

class GithubError(commands.CommandError):
    pass


class CustomError(Exception):
    def __init__(self, times: int, msg: str):
        self.times = times
        self.msg = msg
        self.pre = "This is a custom error:"
        self.message = f"{self.pre} {self.msg*self.times}"
        super().__init__(self.message)


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.TechGuild = 805593783684562965
        self.TracebackChannel = 851949397533392936

    @commands.command()
    async def error(self, ctx, times: int = 20, msg="error"):
        raise CustomError(int(times), msg)
        

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error: Exception):
        tb = error.__traceback__
        etype = type(error)
        exception = traceback.format_exception(etype, error, tb, chain=True)
        exception_msg = ""
        for line in exception:
            exception_msg += line
        
        error = getattr(error, 'original', error)

        if ctx.command.name == "rule":
            return "No Rule..."
        
        if isinstance(error, (commands.CheckFailure, commands.CheckAnyFailure)):
            return

        if hasattr(ctx.command, 'on_error'):
            return

        elif isinstance(error, (commands.CommandNotFound, commands.errors.CommandNotFound)):
            print("Ignored error: " + str(ctx.command))
            return

        elif isinstance(error, (commands.MissingRequiredArgument, commands.TooManyArguments)):
            em = discord.Embed(title = "Missing/Extra Required Arguments Passed In!", description = "You have missed one or several arguments in this command", color = 0xf5160a)
            em.set_thumbnail(url = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
            em.set_footer(text = "Consult the Help Command if you are having trouble or call over a Bot Manager!")
            await ctx.send(embed = em)
            return

        elif isinstance(error, commands.BadArgument):
            em = discord.Embed(title = "Bad Argument!", description = "Unable to parse arguments, check what arguments you provided.", color = 0xf5160a)
            em.set_thumbnail(url = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
            em.set_footer(text = "Consult the Help Command if you are having trouble or call over a Bot Manager!")
            await ctx.send(embed = em)
            return

        elif isinstance(error, (commands.MissingAnyRole, commands.MissingRole, commands.MissingPermissions, commands.errors.MissingAnyRole, commands.errors.MissingRole, commands.errors.MissingPermissions)):
            em = discord.Embed(title = "Invalid Permissions!", description = "You do not have the associated role in order to successfully invoke this command! Contact an administrator/developer if you believe this is invalid.", color = 0xf5160a)
            em.set_thumbnail(url = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
            em.set_footer(text = "Consult the Help Command if you are having trouble or call over a Bot Manager!")
            await ctx.send(embed = em)
            return

        elif isinstance(error, (commands.CommandOnCooldown, commands.errors.CommandOnCooldown)):
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)

            msg = "This command cannot be used again for {} minutes and {} seconds" \
                .format(round(h), round(m), round(s))

            embed = discord.Embed(title = "Command On Cooldown", description = msg, color = discord.Color.red())
            await ctx.send(embed = embed)
            


        else:
            error_file = Path("error.txt")
            error_file.touch()
            with error_file.open("w") as f:
                f.write(exception_msg)
            with error_file.open("r") as f:
                #config, _ = core.common.load_config()
                data = "\n".join([l.strip() for l in f])

                GITHUB_API="https://api.github.com"
                API_TOKEN=os.getenv("GIST")
                url=GITHUB_API+"/gists"
                print(f"Request URL: {url}")                    
                headers={'Authorization':'token %s'%API_TOKEN}
                params={'scope':'gist'}
                payload={"description":"Timmy encountered a Traceback!","public":True,"files":{"error":{"content": f"{data}"}}}
                res=requests.post(url,headers=headers,params=params,data=json.dumps(payload))
                j=json.loads(res.text)
                ID = j['id']
                gisturl = f"https://gist.github.com/{ID}"
                print(gisturl)

                permitlist = []
                query = database.Administrators.select().where(database.Administrators.TierLevel >= 3)
                for user in query:
                    permitlist.append(user.discordID)

                if ctx.author.id not in permitlist:
                    embed = discord.Embed(title = "Traceback Detected!", description = "Timmy here has ran into an error!\nPlease check what you sent and/or check out the help command!", color = 0xfc3d03)
                    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/875233489727922177/876610305852051456/unknown.png")
                    embed.set_footer(text = f"Error: {str(error)}")
                    await ctx.send(embed = embed)
                else:
                    embed = discord.Embed(title = "Traceback Detected!", description = "Timmy here has ran into an error!\nTraceback has been attached below.", color = 0xfc3d03)
                    embed.add_field(name = "GIST URL", value = gisturl)
                    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/875233489727922177/876610305852051456/unknown.png")
                    embed.set_footer(text = f"Error: {str(error)}")
                    await ctx.send(embed = embed)

                guild = self.bot.get_guild(self.TechGuild)
                channel = guild.get_channel(self.TracebackChannel)

                embed2 = discord.Embed(title = "Traceback Detected!", description = f"**Information**\n**Server:** {ctx.message.guild.name}\n**User:** {ctx.message.author.mention}\n**Command:** {ctx.command.name}", color= 0xfc3d03)
                embed2.add_field(name = "Gist URL", value = f"[Uploaded Traceback to GIST](https://gist.github.com/{ID})")
                await channel.send(embed = embed2)

                error_file.unlink()

        raise error
        

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
