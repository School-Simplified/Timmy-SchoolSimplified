from aiohttp import web
from flask import Flask
from discord.ext import commands, tasks
import discord
import os
import aiohttp

app = Flask(__name__)

class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app.route('/')
    async def index(self):
        return 'https://timmy.schoolsimplified.org'

async def setup(bot):
    await app.run(debug=False, port=80, host='0.0.0.0')
    await bot.add_cog(Webserver(bot))
