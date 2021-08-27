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


class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label='Verify', style=discord.ButtonStyle.blurple, custom_id='persistent_view:verify', emoji = "✅")
    async def verify(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True


class VerificationStaff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staffServer = 778406166735880202
        self.ServerIDs = [805593783684562965, 801974357395636254, 799855854182596618, 815753072742891532]

    @commands.Cog.listener("on_interaction")
    async def StaffVerification(self, interaction: discord.Interaction):
        if interaction.guild_id == self.staffServer and interaction.message.id == 880814251420303410:
            print(interaction.user.id)

            staffServer : discord.Guild = await self.bot.fetch_guild(self.staffServer)
            print(staffServer)

            StaffServerMember : discord.Member = staffServer.get_member(interaction.user.id)
            print(StaffServerMember)
            if StaffServerMember == None:
                print("h")
                StaffServerMember : discord.Member = await staffServer.fetch_member(interaction.user.id)
                print(StaffServerMember)


            if StaffServerMember == None:
                return print("huh")
            VerificationChannel :discord.TextChannel = await self.bot.fetch_channel(878681438462050356)
            logchannel = await self.bot.fetch_channel(878774300335833158)

            VerifiedRoles = []
            VerifiedGuilds = []

            for ID in self.ServerIDs:
                server : discord.Guild = await self.bot.fetch_guild(ID)
                try:
                    ServerMember : discord.Member = await server.fetch_member(interaction.user.id)

                except Exception as e:
                    print("member not found")
                    continue

                else:
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

        
            totalguilds = "\n".join(VerifiedGuilds)
            totalroles = "\n".join(VerifiedRoles)
            if len(totalroles) > 0:
                embed = discord.Embed(title = "Verification Details", description = f"**Username:** {StaffServerMember.mention}\n**ID:** `{StaffServerMember.id}`", color = discord.Color.red())
                embed.set_author(name = StaffServerMember.display_name, url = StaffServerMember.avatar.url, icon_url = StaffServerMember.avatar.url)
                embed.add_field(name = "Guild's Found:", value = totalguilds)
                embed.add_field(name = "Role's Applied:", value = totalroles, inline = False)
                await logchannel.send(embed = embed)

                VerifiedRole :discord.Role = discord.utils.get(staffServer.roles, name = "Staff")
                await StaffServerMember.add_roles(VerifiedRole, reason = "[Verification RoleSync] Passed Verification")
                
                try:
                    await interaction.response.send_message('You have been verified!', ephemeral=True)
                except discord.errors.InteractionResponded:
                    try:
                        await interaction.followup.send("You have been verified!", ephemeral=True)
                    except:
                        await VerificationChannel.send(f"{interaction.user.mention} You have been verified!", delete_after=10.0)
            else:
                embed = discord.Embed(title = "Verification Details", description = f"**Username:** {StaffServerMember.mention}\n**ID:** `{StaffServerMember.id}`", color = discord.Color.red())
                embed.set_author(name = StaffServerMember.display_name, url = StaffServerMember.avatar.url, icon_url = StaffServerMember.avatar.url)
                embed.add_field(name = "Guild's Found:", value = totalguilds)
                embed.add_field(name = "Role's Applied:", value = "None Found, they don't appear to hold a position in any sub-server!", inline = False)
                await logchannel.send(embed = embed)

                VerifiedRole :discord.Role = discord.utils.get(staffServer.roles, name = "Staff")
                await StaffServerMember.add_roles(VerifiedRole, reason = "[Verification RoleSync] Passed Verification")
                
                try:
                    await interaction.response.send_message("I didn't seem to find any roles to give you, please try requesting them in <#878679747255750696>!", ephemeral=True)
                except discord.errors.InteractionResponded:
                    try:
                        await interaction.followup.send("I didn't seem to find any roles to give you, please try requesting them in <#878679747255750696>!", ephemeral=True)
                    except:
                        await VerificationChannel.send(f"{interaction.user.mention} I didn't seem to find any roles to give you, please try requesting them in <#878679747255750696>!", delete_after=10.0)

    @commands.command()
    async def pasteVerificationButton(self, ctx):
        button = VerifyButton()
        await ctx.send("Click here to verify", view = button)

    @commands.command()
    async def pasteVerificationEmbed(self, ctx: commands.Context):
        embed = discord.Embed(title = "Verification", description = "To get your staff roles, go to <#878679747255750696> and say what teams you are part of!", color = discord.Colour.blurple())
        embed.set_footer(text = "School Simplified • 08/26/2021", icon_url = "https://media.discordapp.net/attachments/864060582294585354/878682781352362054/ss_current.png")
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(VerificationStaff(bot))
