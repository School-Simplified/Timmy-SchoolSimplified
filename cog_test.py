import os
import sys
from pathlib import Path

import discord.ext.test as dpytest
import pytest
from discord.ext import commands


def get_extensions():
    extensions = []
    extensions.append("jishaku")
    if sys.platform == "win32" or sys.platform == "cygwin":
        dirpath = "\\"
    else:
        dirpath = "/"

    for file in Path("utils").glob("**/*.py"):
        if "!" in file.name or "DEV" in file.name:
            continue
        extensions.append(str(file).replace(dirpath, ".").replace(".py", ""))
    return extensions


@pytest.fixture
def bot(event_loop):
    bot = commands.Bot(loop=event_loop)
    bot.remove_command("help")
    dpytest.configure(bot)
    return bot


@pytest.mark.asyncio
async def test_cogs(bot):
    os.environ["PyTestMODE"] = "True"
    for ext in get_extensions():
        bot.load_extension(ext)


def pytest_sessionfinish():
    print("Session finished")
