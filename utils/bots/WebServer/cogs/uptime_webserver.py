from aiohttp import web
from discord.ext import commands, tasks
import discord
import os
import aiohttp

app = web.Application()
routes = web.RouteTableDef()


class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.web_server.start()

        @routes.get('/')
        async def welcome(request: web.Request):
            return web.HTTPTemporaryRedirect('https://timmy.schoolsimplified.org')
            #return web.Response(text="Hello, world")

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=8080)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Webserver(bot))