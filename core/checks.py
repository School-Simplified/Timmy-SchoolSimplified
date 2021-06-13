'''
SETUP:

If you require a specific command to be protected, you can use the built in @is_botAdmin check or create your own one here!

If you wish to use the @is_botAdmin check, add your Discord ID to "adminIDs".

Otherwise, use the same format to make your own check. 
'''

from discord.ext import commands

adminIDs = [409152798609899530, 491741248152141836, 450476337954553858, 449579826278563860, 415629932798935040]

def predicate(ctx):
    return ctx.author.id in adminIDs

is_botAdmin = commands.check(predicate)
