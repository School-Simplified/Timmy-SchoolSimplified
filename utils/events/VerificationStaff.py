import discord
from core.common import *
from discord.ext import commands

config, _ = load_config("equelRoles")


def getEqualRank(query):
    if query not in config:
        return None
    else:
        return list(config[query])


async def roleNameCheck(self, name: str, guild: discord.Guild, user: discord.Member):
    check = getEqualRank(name)

    if check is not None:
        if check in [role.name for role in guild.roles]:
            helper: discord.Role = discord.utils.get(guild.roles, name=check)
            await user.add_roles(helper)


class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(
        label="Verify",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:verify",
        emoji="✅",
    )
    async def verify(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True


class VerificationStaff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staffServer = {STAFF_ID.g_staff: STAFF_ID.ch_verificationLogs}
        self.StaffServerIDs = [STAFF_ID.g_staff]
        self.VerificationIDs = [DIGITAL_ID.ch_verification, STAFF_ID.ch_verification]
        self.ServerIDs = [
            TECH_ID.g_tech,
            CH_ID.g_ch,
            TUT_ID.g_tut,
            MKT_ID.g_mkt,
            HR_ID.g_hr,
        ]

    @commands.Cog.listener("on_interaction")
    async def StaffVerification(self, interaction: discord.Interaction):
        InteractionResponse = interaction.data
        print(InteractionResponse)

        if interaction.message is None:
            return

        if (
            interaction.guild_id in self.StaffServerIDs
            and interaction.channel.id in self.VerificationIDs
        ):
            print(interaction.user.id)

            staffServer: discord.Guild = await self.bot.fetch_guild(
                interaction.guild_id
            )
            print(staffServer)
            StaffServerMember: discord.Member = staffServer.get_member(
                interaction.user.id
            )

            print(StaffServerMember)
            if StaffServerMember is None:
                print("h")
                StaffServerMember: discord.Member = await staffServer.fetch_member(
                    interaction.user.id
                )
                print(StaffServerMember)

            if StaffServerMember is None:
                try:
                    await interaction.response.send_message(
                        "<:sadturtl:879197443600834600> An error occurred while trying to verify your status, please contact a staff member! (Error Code: TM-NOMEMBERFOUND)",
                        ephemeral=True,
                    )
                except discord.InteractionResponded:
                    try:
                        await interaction.followup.send(
                            "<:sadturtl:879197443600834600> An error occurred while trying to verify your status, "
                            "please contact a staff member! (Error Code: TM-NOMEMBERFOUND)",
                            ephemeral=True,
                        )
                    except:
                        await interaction.channel.send(
                            f"{interaction.user.mention} <:sadturtl:879197443600834600> An error occurred while "
                            f"trying to verify your status, please contact a staff member! (Error Code: "
                            f"TM-NOMEMBERFOUND)",
                            delete_after=10.0,
                        )
                finally:
                    return

            VerificationChannel = interaction.channel
            logchannel = await self.bot.fetch_channel(
                self.staffServer[interaction.guild_id]
            )

            VerifiedRoles = []
            VerifiedGuilds = []

            for ID in self.ServerIDs:
                server: discord.Guild = await self.bot.fetch_guild(ID)
                try:
                    ServerMember: discord.Member = await server.fetch_member(
                        interaction.user.id
                    )

                except Exception as e:
                    print("member not found")
                    continue

                else:
                    roleNames = [role for role in ServerMember.roles]

                    for role in roleNames:
                        check = getEqualRank(role.name)
                        print(f"CHECK: {check}")

                        if check is not None:
                            checkSTR = ", ".join(check)
                            markdownRole = f"`{checkSTR}` -> *{server.name}*"
                            markdownGuild = f"`{server.name}`"

                            if markdownRole not in VerifiedRoles:
                                VerifiedRoles.append(f"`{checkSTR}` -> *{server.name}*")
                            if markdownGuild not in VerifiedGuilds:
                                VerifiedGuilds.append(f"`{server.name}`")

                            for elem in check:
                                if elem in [role.name for role in staffServer.roles]:
                                    jsonROLE = discord.utils.get(
                                        staffServer.roles, name=elem
                                    )
                                    print(f"ELEM: {elem}")
                                    print(f"JSONROLE: {jsonROLE}")
                                    print(f"SubServer: {server}")
                                    print(f"Member: {ServerMember}")

                                    await StaffServerMember.add_roles(
                                        jsonROLE, reason="Verification RoleSync"
                                    )

            totalguilds = "\n".join(VerifiedGuilds)
            totalroles = "\n".join(VerifiedRoles)
            if len(VerifiedRoles) > 0:
                embed = discord.Embed(
                    title="Verification Details",
                    description=f"**Username:** {StaffServerMember.mention}\n**ID:** `{StaffServerMember.id}`",
                    color=discord.Color.red(),
                )
                embed.set_author(
                    name=StaffServerMember.display_name,
                    url=StaffServerMember.avatar.url,
                    icon_url=StaffServerMember.avatar.url,
                )
                embed.add_field(name="Guild's Found:", value=totalguilds)
                embed.add_field(name="Role's Applied:", value=totalroles, inline=False)
                await logchannel.send(embed=embed)

                VerifiedRole: discord.Role = discord.utils.get(
                    staffServer.roles, name="Member"
                )
                await StaffServerMember.add_roles(
                    VerifiedRole, reason="[Verification RoleSync] Passed Verification"
                )

                try:
                    await interaction.response.send_message(
                        "You have been verified!", ephemeral=True
                    )
                except discord.InteractionResponded:
                    try:
                        await interaction.followup.send(
                            "You have been verified!", ephemeral=True
                        )
                    except:
                        await VerificationChannel.send(
                            f"{interaction.user.mention} You have been verified!",
                            delete_after=10.0,
                        )
            else:

                embed = discord.Embed(
                    title="Verification Details",
                    description=f"**Username:** {StaffServerMember.mention}\n**ID:** `{StaffServerMember.id}`",
                    color=discord.Color.red(),
                )
                embed.set_author(
                    name=StaffServerMember.display_name,
                    url=StaffServerMember.avatar.url,
                    icon_url=StaffServerMember.avatar.url,
                )
                embed.add_field(name="Guild's Found:", value=f"No Guilds...")
                embed.add_field(
                    name="Role's Applied:",
                    value="None Found, they don't appear to hold a position in any sub-server!",
                    inline=False,
                )

                await logchannel.send(embed=embed)

                try:
                    await interaction.response.send_message(
                        "I didn't seem to find any roles to give you, please try requesting them in "
                        "<#878679747255750696>!",
                        ephemeral=True,
                    )
                except discord.InteractionResponded:
                    try:
                        await interaction.followup.send(
                            "I didn't seem to find any roles to give you, please try requesting them in "
                            "<#878679747255750696>!",
                            ephemeral=True,
                        )
                    except:
                        await VerificationChannel.send(
                            f"{interaction.user.mention} I didn't seem to find any roles to give you, please try "
                            f"requesting them in <#878679747255750696>!",
                            delete_after=10.0,
                        )

    @commands.command()
    async def pasteVerificationButton(self, ctx):
        button = VerifyButton()
        await ctx.send("Click here to verify", view=button)

    @commands.command()
    async def pasteVerificationEmbed(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Verification",
            description=f"To get your staff roles, go to <#{DIGITAL_ID.ch_waitingRoom}> and say what teams you are part of!",
            color=discord.Colour.blurple(),
        )
        embed.set_footer(
            text="School Simplified • 08/26/2021", icon_url=Others.ssLogo_png
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(VerificationStaff(bot))
