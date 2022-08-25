import os
import sys

import discord
import discord.ext.test as dpytest
import pytest
from discord.ext import commands
from pathlib import Path


def get_extensions():
    extensions = ["jishaku"]
    if sys.platform == "win32" or sys.platform == "cygwin":
        dirpath = "\\"
    else:
        dirpath = "/"

    for file in Path("utils").glob("**/*.py"):

        if any(dev_symbol in file.name for dev_symbol in ["!", "DEV", "view_models"]):
            continue
        extensions.append(str(file).replace(dirpath, ".").replace(".py", ""))
    return extensions


@pytest.fixture
def bot(event_loop):
    bot = commands.Bot(
        command_prefix="/", event_loop=event_loop, intents=discord.Intents.all()
    )
    bot.remove_command("help")
    dpytest.configure(bot)
    return bot


@pytest.mark.asyncio
async def test_cogs(bot):
    os.environ["PyTestMODE"] = "True"
    for ext in get_extensions():
        await bot.load_extension(ext)


def pytest_sessionfinish():
    print("Session finished")
