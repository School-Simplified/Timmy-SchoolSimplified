"""
SETUP:

If you require a specific command to be protected, you can use the built in @is_botAdmin check or create your own one here!

If you wish to use the @is_botAdmin check, DM Space.".

Otherwise, use the same format to make your own check. 
"""

import typing
import os
import re
from discord.ext import commands
from core import database
from core.common import MKT_ID


def predicate_LV1(ctx) -> bool:
    adminIDs = []

    query = database.Administrators.select().where(
        database.Administrators.TierLevel >= 1
    )
    for admin in query:
        adminIDs.append(admin.discordID)

    return ctx.author.id in adminIDs


is_botAdmin = commands.check(predicate_LV1)


def predicate_LV2(ctx):
    adminIDs = []

    query = database.Administrators.select().where(
        database.Administrators.TierLevel >= 2
    )
    for admin in query:
        adminIDs.append(admin.discordID)

    return ctx.author.id in adminIDs


is_botAdmin2 = commands.check(predicate_LV2)


def predicate_LV3(ctx):
    adminIDs = []

    query = database.Administrators.select().where(
        database.Administrators.TierLevel >= 3
    )
    for admin in query:
        adminIDs.append(admin.discordID)

    return ctx.author.id in adminIDs


is_botAdmin3 = commands.check(predicate_LV3)


def predicate_LV4(ctx):
    adminIDs = []

    query = database.Administrators.select().where(
        database.Administrators.TierLevel >= 4
    )
    for admin in query:
        adminIDs.append(admin.discordID)

    return ctx.author.id in adminIDs


is_botAdmin4 = commands.check(predicate_LV4)


def mktCommissionAdd(ctx):
    rolesID = [
        MKT_ID.r_designManager,
        MKT_ID.r_designTeam,
        MKT_ID.r_discordManager,
        MKT_ID.r_discordTeam,
        MKT_ID.r_contentCreatorManager,
    ]

    return any(role.id in rolesID for role in ctx.author.roles)


is_mktCommissionAuthorized = commands.check(mktCommissionAdd)


def notHostTimmyA(ctx):
    runPath = os.path.realpath(__file__)
    runDir = re.search("/home/[^/]*", runPath)

    if runDir is not None:
        runDir = runDir.group(0)
    else:
        runDir = None

    return not runDir == "/home/timmya"


isnot_hostTimmyA = commands.check(notHostTimmyA)
