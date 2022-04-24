from discord.ext import commands
from flask import Flask

app = Flask(__name__)

class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app.route('/')
    async def index(self):
        return 500

async def setup(bot):
    await app.run(debug=False, port=80, host='0.0.0.0')
    await bot.add_cog(Webserver(bot))
