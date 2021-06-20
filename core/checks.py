'''
SETUP:

If you require a specific command to be protected, you can use the built in @is_botAdmin check or create your own one here!

If you wish to use the @is_botAdmin check, add your Discord ID to "adminIDs".

Otherwise, use the same format to make your own check. 
'''

from discord.ext import commands
from core import database


#adminIDs = [409152798609899530, 491741248152141836, 450476337954553858, 449579826278563860, 409730612434567179]

def predicate(ctx):
    adminIDs = []

    for admin in database.Administrators:
        adminIDs.append(admin.discordID)

    return ctx.author.id in adminIDs

is_botAdmin = commands.check(predicate)
