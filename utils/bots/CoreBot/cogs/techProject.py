import discord
from core.checks import is_botAdmin3
from discord.ext import commands
from core.common import SelectMenuHandler, TempConfirm, LockButton, TECH_ID, Emoji


async def createChannel(
    self,
    ctx: commands.Context,
    type: str,
    member: discord.Member,
    discordEmbed: discord.Embed,
):
    if type == "Bot Developer Team":
        DDM = ctx.guild.get_role(TECH_ID.r_developerManager)
        ADT = ctx.guild.get_role(TECH_ID.r_assistantBotDevManager)
        DT = ctx.guild.get_role(TECH_ID.r_botDeveloper)

        RolePerms = [DDM, ADT, DT]
        Title = "developer"
        embed = discord.Embed(
            title="Developer Ticket",
            description=f"Welcome {member.mention}! A developer will be with you shortly.",
            color=discord.Color.green(),
        )
        category = discord.utils.get(
            ctx.guild.categories, id=TECH_ID.cat_developerComms
        )

    else:
        raise BaseException("ERROR: unknown type")

    num = len(category.channels)
    channel: discord.TextChannel = await ctx.guild.create_text_channel(
        f"{Title}-{num}", category=category
    )
    await channel.set_permissions(
        ctx.guild.default_role, read_messages=False, reason="Ticket Perms"
    )
    await channel.set_permissions(
        member, read_messages=True, reason="Ticket Perms"
    )

    for role in RolePerms:
        await channel.set_permissions(
            role, send_messages=True, read_messages=True, reason="Ticket Perms"
        )
        await channel.set_permissions(
            role, send_messages=True, read_messages=True, reason="Ticket Perms"
        )

    controlTicket = discord.Embed(
        title="Control Panel",
        description="To end this ticket, click the lock button!",
        color=discord.Colour.gold(),
    )
    PermLockInstance = LockButton(self.bot)
    await channel.send(member.mention)
    await channel.send(embed=controlTicket, view=PermLockInstance)

    await channel.send(embed=embed)
    return channel


class TechProjectCMD(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.decodeDict = {
            "['Bot Developer Team']": "Bot Developer Team",
            "['Website Team']": "Website Team",
        }

    @commands.command()
    async def techembedc(self, ctx):
        embed = discord.Embed(
            title="Technical Team Commissions", color=discord.Color.green()
        )
        embed.add_field(
            name="Developer Commissions",
            value="If you'd like to start a Developer Commission, please fill out the form via `+request` and a ticket will autoamtically be created for you!",
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def request(self, ctx: commands.Context):
        if ctx.guild.id != TECH_ID.g_tech:
            return

        await ctx.message.delete()

        channel = await ctx.author.create_dm()
        await ctx.send(f"{ctx.author.mention} Check DMs!")

        def check(m):
            return (
                m.content is not None
                and m.channel == channel
                and m.author.id is ctx.author.id
            )

        embed = discord.Embed(
            title="Reminders",
            description="1) Please remember that you need to have prior permission "
            "(if you aren't a manager) before requesting a tech team project!"
            "\n\n2) Make sure the responses you provide are **short** and **to the point!**"
            "\n3) **If you have any questions, DM a Technical VP!**",
            color=discord.Colour.red(),
        )
        await channel.send(embed=embed)

        embed = discord.Embed(
            title="Q1: What is a descriptive title for your project?",
            color=discord.Colour.gold(),
        )
        await channel.send(embed=embed)
        answer1 = await self.bot.wait_for("message", check=check)

        embed = discord.Embed(
            title="Q2: Which of these categories does your project suggestion fit under?",
            color=discord.Colour.gold(),
        )

        options = [
            discord.SelectOption(
                label="Bot Developer Team",
                description="If you need a Discord Bot or a modification to one, click here!",
                emoji="🤖",
            ),
            discord.SelectOption(
                label="Website Team",
                description="If you need changes done to the website, click here!",
                emoji="👨‍💻",
            ),
        ]

        view = discord.ui.View()
        view.add_item(
            SelectMenuHandler(
                options,
                place_holder="Select a category that relates to your commission!",
            )
        )

        await channel.send(embed=embed, view=view)
        await view.wait()

        ViewResponse = str(view.children[0].values)
        answer2 = self.decodeDict[ViewResponse]

        if answer2 == "Website Team":
            embed = discord.Embed(
                title="Website Team Commissions",
                description="Hey there! Website Team Commissions are to be created on **School Simplified's GitHub Page**."
                "\n> You can create one here: https://github.com/HazimAr/School-Simplified/issues/new/choose",
                color=discord.Colour.red(),
            )
            embed.set_footer(text="Canceliing Commission Request...")
            await channel.send(embed=embed)
            return

        embed = discord.Embed(
            title="Q3: Which team is this project for?", color=discord.Colour.gold()
        )
        await channel.send(embed=embed)
        answer3 = await self.bot.wait_for("message", check=check)

        embed = discord.Embed(
            title="Q4: Please write a brief description of the project. ",
            color=discord.Colour.gold(),
        )
        await channel.send(embed=embed)
        answer4 = await self.bot.wait_for("message", check=check)

        embed = discord.Embed(
            title="Q5: Have you received approval from a manager for this project (or are you a manager yourself)?",
            color=discord.Colour.gold(),
        )
        await channel.send(embed=embed)
        answer5 = await self.bot.wait_for("message", check=check)

        embed = discord.Embed(title="Q6: Anything else?", color=discord.Colour.gold())
        await channel.send(embed=embed)
        answer6 = await self.bot.wait_for("message", check=check)

        buttonView = TempConfirm()
        embed = discord.Embed(
            title="Confirm Responses...",
            description="Are you ready to submit these responses?",
            color=discord.Colour.gold(),
        )
        message = await channel.send(embed=embed, view=buttonView)
        await buttonView.wait()

        if buttonView.value is None:
            return await channel.send("Timed out, try again later.")

        elif not buttonView.value:
            return

        elif buttonView.value:
            NPR = discord.Embed(
                title="New Project Request",
                description=f"Project Requested by {ctx.author.mention}",
                color=discord.Colour.green(),
            )
            NPR.add_field(
                name="Q1: What is a descriptive title for your project?",
                value=answer1.content,
            )
            NPR.add_field(
                name="Q2: Which of these categories does your project suggestion fit under?",
                value=answer2,
            )
            NPR.add_field(
                name="Q3: Which team is this project for?", value=answer3.content
            )
            NPR.add_field(
                name="Q4: Please write a brief description of the project.",
                value=answer4.content,
            )
            NPR.add_field(
                name="Q5: Have you received approval from a manager for this project (or are you a manager yourself)?",
                value=answer5.content,
            )
            NPR.add_field(name="Q6: Anything else?", value=answer6.content)

            PJC = await self.bot.fetch_channel(TECH_ID.ch_commissionLogs)
            try:
                msg = await PJC.send(embed=NPR)
            except:
                await channel.send(
                    "Error sending the response, maybe you hit the character limit?"
                )
            else:
                member = ctx.guild.get_member(ctx.author.id)
                TicketCH = await createChannel(self, ctx, answer2, member, NPR)

                await TicketCH.send("Submitted Report:", embed=NPR)
                await channel.send(
                    f"**Ticket Created!**"
                    f"\n> Please use {TicketCH.mention} if you wish to follow up on your commission!"
                )

    @commands.command()
    @is_botAdmin3
    async def projectR(self, ctx, user: discord.User, type, projectname, *, notes=None):
        embed = discord.Embed(
            title="Project Announcement",
            description="The assignee that has taken up your project request has an update for you!",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Status",
            value=f"Project Status: `{type}`"
            f"\n-> Project: {projectname}"
            f"\n-> Project Assignee: {ctx.author.mention}",
        )
        embed.set_footer(
            text="DM's are not monitored, DM your Project Requester for more information."
        )
        if notes is not None:
            embed.add_field(name="Notes", value=notes)

        await user.send(embed=embed)
        await ctx.send("Sent report!\n", embed=embed)


def setup(bot):
    bot.add_cog(TechProjectCMD(bot))
