import asyncio
from datetime import datetime
import os

import discord
import pytz
from core.checks import is_botAdmin
from core.common import ButtonHandler, Emoji, GSuiteVerify, access_secret
from discord.ext import commands
from google_auth_oauthlib.flow import Flow

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"


class GSuiteLogin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flow = access_secret(
            "svc_c",
            True,
            1,
            [
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
            "urn:ietf:wg:oauth:2.0:oob",
        )
        """self.flow = Flow.from_client_secrets_file(
            'gsheetsadmin/staff_verifyClient.json',
            scopes=['https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile'],
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )"""
        self.staffrole = 932066545117585430
        self.logchannel = 932066545885134904
        self.est = pytz.timezone("US/Eastern")

    @commands.Cog.listener("on_interaction")
    async def GSuiteVerify(self, interaction: discord.Interaction):
        InteractionResponse = interaction.data
        if interaction.message is None:
            return

        try:
            val = InteractionResponse["custom_id"]
        except KeyError:
            return

        if InteractionResponse["custom_id"] == "persistent_view:gsuiteverify":

            def check(m):
                return (
                    m.content is not None
                    and m.channel == dm_channel
                    and m.author.id is author.id
                )

            channel = await self.bot.fetch_channel(interaction.channel_id)
            guild = interaction.message.guild
            author = interaction.user
            dm_channel = await author.create_dm()

            auth_url, _ = self.flow.authorization_url(prompt="consent")
            auth_url = auth_url + "&hb=schoolsimplified.org"
            # auth_url = auth_url.replace('auth', 'auth/oauthchooseaccount', 1)
            embed = discord.Embed(
                title="GSuite Verification",
                description="Click on the button below and sign in with your **personal** "
                "@schoolsimplified.org account.\nOnce you sign in you should get a "
                "code, copy and paste that here.",
                color=discord.Color.red(),
            )
            embed.add_field(
                name="Getting Error Code '403: org_internal'?",
                value="Make sure you sign in with your @schoolsimplified.org **Google Account**. If you "
                "are immediately being redirected to that webpage, make sure you sign in on your "
                "browser first and then try clicking the verification button again. ",
            )
            embed.set_footer(
                text="NOTE: This token is not stored and is only used to determine your identity."
            )

            view = discord.ui.View()
            emoji = Emoji.timmyBook
            view.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.green,
                    url=auth_url,
                    disabled=False,
                    label="Click here to sign in with your GSuite account!",
                    emoji=emoji,
                )
            )
            await dm_channel.send(embed=embed, view=view)
            await dm_channel.send("Now paste your authentication code here:")

            try:
                answer1 = await self.bot.wait_for("message", timeout=200.0, check=check)
                if (
                    answer1.content is None
                    or answer1.content == ""
                    or answer1.content == " "
                ):
                    return await dm_channel.send(
                        "No message was sent, try again later..."
                    )
                else:
                    try:
                        self.flow.fetch_token(code=answer1.content)
                    except Exception as e:
                        return await dm_channel.send("Invalid code, try again later...")
                    else:
                        session = self.flow.authorized_session()
                        respjson = session.get(
                            "https://www.googleapis.com/userinfo/v2/me"
                        ).json()
                        firstname = respjson["given_name"]
                        if firstname == "SS" or firstname == "PS":
                            return await dm_channel.send(
                                "You are not allowed to authenticate with Department Accounts, please use your "
                                "**personal** account to authenticate."
                            )
                        else:
                            embed = discord.Embed(
                                title="Authentication Successful",
                                description=f"Hello {firstname}, you have successfully "
                                f"authenticated with your GSui"
                                f"te account, {respjson['email']}.",
                                color=discord.Color.green(),
                            )
                            embed.set_footer(text="Assigning you your staff role.")
                            await dm_channel.send(embed=embed)

                            member: discord.Member = guild.get_member(author.id)
                            role = guild.get_role(self.staffrole)
                            await member.add_roles(
                                role,
                                reason="Passed Verification: {}".format(
                                    respjson["email"]
                                ),
                            )

                            now = datetime.now()
                            now = now.astimezone(pytz.timezone("US/Eastern")).strftime(
                                "%m/%d/%Y %I:%-M %p"
                            )
                            logchannel: discord.TextChannel = (
                                await self.bot.fetch_channel(self.logchannel)
                            )

                            embed = discord.Embed(
                                title="GSuite Authentication",
                                description=f"{member.mention} has successfully authenticated with "
                                f"their GSuite account.",
                                color=discord.Color.green(),
                            )
                            embed.add_field(
                                name="Verification Details",
                                value="**Name:** {}\n**Email:** {}\n**Date:** {} EST".format(
                                    f"{respjson['given_name']} {respjson['family_name']}",
                                    respjson["email"],
                                    now,
                                ),
                            )
                            embed.set_footer(
                                text="This action was performed by {}".format(
                                    member.display_name
                                )
                            )
                            await logchannel.send(embed=embed)

            except asyncio.TimeoutError:
                await dm_channel.send(
                    "Looks like you didn't respond in time, please try again later!"
                )

    @commands.command()
    @is_botAdmin
    async def pasteGSuiteButton(self, ctx):
        embed = discord.Embed(
            title="Alternate Verification Method",
            description="If you have a @schoolsimplified.org Google Account, choose this method to "
            "get immediately verified.",
            color=discord.Color.green(),
        )
        GSuiteButton = GSuiteVerify()
        await ctx.send(embed=embed, view=GSuiteButton)


def setup(bot):
    bot.add_cog(GSuiteLogin(bot))
