import discord
from discord.ext import commands

from core.common import (
    ChID,
    DIGITAL_ID,
    HRID,
    MktID,
    StaffID,
    TechID,
    TutID,
    load_config,
)
from core.logging_module import get_log

_log = get_log(__name__)

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


class VerificationStaff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staffServer = {StaffID.g_staff: StaffID.ch_verification_logs}
        self.StaffServerIDs = [StaffID.g_staff]
        self.VerificationIDs = [DIGITAL_ID.ch_verification, StaffID.ch_verification]
        self.ServerIDs = [
            TechID.g_tech,
            ChID.g_ch,
            TutID.g_tut,
            MktID.g_mkt,
            HRID.g_hr,
        ]

    @commands.Cog.listener("on_interaction")
    async def StaffVerification(self, interaction: discord.Interaction):
        InteractionResponse = interaction.data

        if interaction.message is None:
            return

        if (
            interaction.guild_id in self.StaffServerIDs
            and interaction.channel.id in self.VerificationIDs
        ):
            staffServer: discord.Guild = self.bot.get_guild(interaction.guild_id)
            StaffServerMember: discord.Member = staffServer.get_member(
                interaction.user.id
            )

            if StaffServerMember is None:
                StaffServerMember: discord.Member = staffServer.get_member(
                    interaction.user.id
                )

            if StaffServerMember is None:
                try:
                    await interaction.response.send_message(
                        "An error occurred while trying to verify your status, please contact a staff member! (Error Code: TM-NOMEMBERFOUND)",
                        ephemeral=True,
                    )
                except discord.InteractionResponded:
                    try:
                        await interaction.followup.send(
                            "An error occurred while trying to verify your status, "
                            "please contact a staff member! (Error Code: TM-NOMEMBERFOUND)",
                            ephemeral=True,
                        )
                    except:
                        await interaction.channel.send(
                            f"{interaction.user.mention} An error occurred while "
                            f"trying to verify your status, please contact a staff member! (Error Code: "
                            f"TM-NOMEMBERFOUND)",
                            delete_after=10.0,
                        )
                finally:
                    return

            VerificationChannel = interaction.channel
            logchannel = self.bot.get_channel(self.staffServer[interaction.guild_id])

            VerifiedRoles = []
            VerifiedGuilds = []

            for ID in self.ServerIDs:
                server: discord.Guild = self.bot.get_guild(ID)
                try:
                    ServerMember: discord.Member = server.get_member(
                        interaction.user.id
                    )

                except Exception as e:
                    _log.error("member not found")
                    continue

                else:
                    roleNames = [role for role in ServerMember.roles]

                    for role in roleNames:
                        check = getEqualRank(role.name)
                        _log.info(f"CHECK: {check}")

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

    # @commands.command()
    # async def pasteVerificationButton(self, ctx):
    #     button = VerifyButton()
    #     await ctx.send("Click here to verify", view=button)
    #
    # @commands.command()
    # async def pasteVerificationEmbed(self, ctx: commands.Context):
    #     embed = discord.Embed(
    #         title="Verification",
    #         description=f"To get your staff roles, go to <#{DIGITAL_ID.ch_waitingRoom}> and say what teams you are part of!",
    #         color=discord.Colour.blurple(),
    #     )
    #     embed.set_footer(
    #         text="School Simplified • 08/26/2021", icon_url=Others.ss_logo_png
    #     )
    #     await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(VerificationStaff(bot))
