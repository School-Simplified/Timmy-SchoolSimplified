import discord
from core.common import *
from discord.ext import commands

config, _ = load_config("equelRoles")

def getEqualRank(query):
    if query not in config:
        return None
    else:
        return config[query]


async def roleNameCheck(self, name: str, guild: discord.Guild, user: discord.Member):
    check = getEqualRank(name)

    if check != None:
        if check in [role.name for role in guild.roles]:
            helper : discord.Role= discord.utils.get(guild.roles, name=check)
            print(check, guild, helper)
            await user.add_roles(helper)



    

class VerificationStaff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staffServer = 778406166735880202
        self.ServerIDs = [805593783684562965, 801974357395636254, 799855854182596618, 815753072742891532]

    @commands.Cog.listener("on_raw_reaction_add")
    async def StaffVerification(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id == self.staffServer and payload.message_id == 878682845021876234:
            staffServer : discord.Guild = await self.bot.fetch_guild(self.staffServer)
            StaffServerMember : discord.Member = await staffServer.fetch_member(payload.user_id)
            logchannel = await self.bot.fetch_channel(878774300335833158)

            VerifiedRoles = []
            VerifiedGuilds = []

            for ID in self.ServerIDs:
                server : discord.Guild = await self.bot.fetch_guild(ID)
                ServerMember : discord.Member = await server.fetch_member(payload.user_id)

                if ServerMember != None:
                    roleNames = [role for role in ServerMember.roles]

                    for role in roleNames:
                        check = getEqualRank(role.name)

                        if check != None:
                            markdownRole = f"`{check}` -> *{server.name}*"
                            markdownGuild = f"`{server.name}`"

                            if markdownRole not in VerifiedRoles:
                                VerifiedRoles.append(f"`{check}` -> *{server.name}*")
                            if markdownGuild not in VerifiedGuilds:
                                VerifiedGuilds.append(f"`{server.name}`")

                            if check in [role.name for role in staffServer.roles]:
                                print(role.id)
                                jsonROLE = discord.utils.get(staffServer.roles, name = check)

                                print(jsonROLE, server, ServerMember)
                                
                                await StaffServerMember.add_roles(jsonROLE, reason = "Verification RoleSync")

                else:
                    print("member not found")
                    continue
        
            totalguilds = "\n".join(VerifiedGuilds)
            totalroles = "\n".join(VerifiedRoles)
            

            embed = discord.Embed(title = "Verification Details", description = f"**Username:** {StaffServerMember.mention}\n**ID:** `{StaffServerMember.id}`", color = discord.Color.red())
            embed.set_author(name = StaffServerMember.display_name, url = StaffServerMember.avatar_url, icon_url = StaffServerMember.avatar_url)
            embed.add_field(name = "Guild's Found:", value = totalguilds)
            embed.add_field(name = "Role's Applied:", value = totalroles, inline = False)
            await logchannel.send(embed = embed)

            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = self.bot.get_user(payload.user_id)
            await message.remove_reaction("✅", user)

def setup(bot):
    bot.add_cog(VerificationStaff(bot))
