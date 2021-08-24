import inspect
import io
import logging
import os
import subprocess
import textwrap
import traceback
from contextlib import redirect_stdout
from datetime import datetime

import discord
from core import database
from core.checks import is_botAdmin3
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
class Eval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("EvalCMD: Cog Loaded!")

    @commands.command(name='eval')
    @is_botAdmin3
    async def _eval(self, ctx: commands.Context, *, body):
        NE = database.AdminLogging.create(discordID=ctx.author.id, action="EVAL", content = body)
        NE.save()

        """Evaluates python code"""
        env = {
            'ctx': ctx,
            'self': self,
            'bot': self.bot,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'source': inspect.getsource
        }

        def cleanup_code(content):
            """Automatically removes code blocks from the code."""
            # remove ```py\n```
            if content.startswith('```') and content.endswith('```'):
                return '\n'.join(content.split('\n')[1:-1])

            # remove `foo`
            return content.strip('` \n')

        env.update(globals())

        body = cleanup_code(body)
        stdout = io.StringIO()
        err = out = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        def paginate(text: str):
            '''Simple generator that paginates text.'''
            last = 0
            pages = []
            for curr in range(0, len(text)):
                if curr % 1980 == 0:
                    pages.append(text[last:curr])
                    last = curr
                    appd_index = curr
            if appd_index != len(text) - 1:
                pages.append(text[last:curr])
            return list(filter(lambda a: a != '', pages))

        try:
            exec(to_compile, env)
        except Exception as e:
            value = e.__class__.__name__
            value2 = e
            if os.getenv("Name") in value:
                value = value.replace(os.getenv("Name"), "Space")
            if os.getenv("Name") in value2:
                value2 = value2.replace(os.getenv("Name"), "Space")

            err = await ctx.send(f'```py\n{value}: {value2}\n```')
            return await ctx.message.add_reaction('\u2049')
        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            if os.getenv("Name") in value:
                value = value.replace(os.getenv("Name"), "Space")
            err = await ctx.send(f'```py\n{value}{traceback.format_exc().replace(os.getenv("Name"), "Space")}\n```')
        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    try:

                        out = await ctx.send(f'```py\n{value}\n```')
                    except:
                        paginated_text = paginate(value)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                out = await ctx.send(f'```py\n{page}\n```')
                                break
                            await ctx.send(f'```py\n{page}\n```')
            else:
                try:
                    out = await ctx.send(f'```py\n{value}{ret}\n```')
                except:
                    paginated_text = paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f'```py\n{page}\n```')
                            break
                        await ctx.send(f'```py\n{page}\n```')

        if out:
            await ctx.message.add_reaction('\u2705')  # tick
        elif err:
            await ctx.message.add_reaction('\u2049')  # x
        else:
            await ctx.message.add_reaction('\u2705')


    @commands.command()
    @is_botAdmin3
    async def shell(self, ctx, *, command):
        NE = database.AdminLogging.create(discordID=ctx.author.id, action="SHELL")
        NE.save()

        timestamp = datetime.now()
        author = ctx.author
        guild = ctx.guild
        output = ""
        try:
            p = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
            output += p.stdout
            embed = discord.Embed(title="Shell Process", description=f"Shell Process started by {author.mention}",
                                color=0x4c594b)
            num_of_fields = len(output) // 1014 + 1
            for i in range(num_of_fields):
                embed.add_field(name="Output" if i == 0 else "\u200b",
                                value="```bash\n" + output[i * 1014:i + 1 * 1014] + "\n```")
            embed.set_footer(text=guild.name + " | Date: " + str(timestamp.strftime(r"%x")))
            await ctx.send(embed=embed)
        except Exception as error:
            tb = error.__traceback__
            etype = type(error)
            exception = traceback.format_exception(etype, error, tb, chain=True)
            exception_msg = ""
            for line in exception:
                exception_msg += line
            embed = discord.Embed(title="Shell Process", description=f"Shell Process started by {author.mention}",
                                color=0x4c594b)
            num_of_fields = len(output) // 1014 + 1
            for i in range(num_of_fields):
                embed.add_field(name="Output" if i == 0 else "\u200b",
                                value="```bash\n" + exception_msg[i * 1014:i + 1 * 1014] + "\n```")
            embed.set_footer(text=guild.name + " | Date: " + str(timestamp.strftime(r"%x")))
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Eval(bot))
