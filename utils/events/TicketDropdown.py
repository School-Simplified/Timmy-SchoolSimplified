import typing

import discord
from core import database
from core.common import *
from discord.ext import commands

MasterSubjectOptions = [
    discord.SelectOption(label='Math Helpers', description='If you need help with Math, click here!', emoji='✖️'),
    discord.SelectOption(label='Science Helpers', description='If you need help with Science, click here!', emoji='🧪'),
    discord.SelectOption(label='Social Studies Helpers', description='If you need help with Social Studies, click here!', emoji='📙'),
    discord.SelectOption(label='English Helpers', description='If you need help with English, click here!', emoji='📖'),
    discord.SelectOption(label='Essay Helpers', description='If you need help with an Essay, click here!', emoji='✍️'),
    discord.SelectOption(label='Language Helpers', description='If you need help with a Language, click here!', emoji='🗣'),
    discord.SelectOption(label='Computer Science Helpers', description='If you need help with Computer Science, click here!', emoji='💻'),
    discord.SelectOption(label='Fine Art Helpers', description='If you need help with Fine Arts, click here!', emoji='🎨'),
    discord.SelectOption(label='Other Helpers', description='If you need help with anything else, click here!', emoji='🧐'),
]


#MasterSubjectView = discord.ui.View()
#MasterSubjectView.add_item(SelectMenuHandler(MasterSubjectOptions, "persistent_view:ticketdrop", "Select a subject you need help with!", 1,1, interaction_message = "Check your DM's!", ephemeral = True))


async def rawExport(self, channel: discord.TextChannel, response: discord.TextChannel, user: discord.User):
    transcript = await chat_exporter.export(channel, None)
    query = database.TicketInfo.select().where(database.TicketInfo.ChannelID == channel.id).get()
    TicketOwner = await self.bot.fetch_user(query.authorID)

    if transcript is None:
        return

    embed = discord.Embed(title = "Channel Transcript", color = discord.Colour.green())
    embed.set_author(name = f"{user.name}#{user.discriminator}", url = user.avatar.url, icon_url = user.avatar.url)
    embed.add_field(name = "Transcript Owner", value = TicketOwner.mention)
    embed.add_field(name = "Ticket Name", value = channel.name, inline = False)
    embed.add_field(name = "Category", value = channel.category.name)
    embed.set_footer(text = "Transcript Attached Below")

    transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{channel.name}.html")

    await response.send(embed = embed)
    await response.send(file=transcript_file)


def decodeDict(self, value: str) -> typing.Union[str, int]:
    """Returns the true value of a dict output and pair value.

    Args:
        value (str): Dict output

    Returns:
        typing.Union[str, int]: Raw output of the Dict and Pair value. 
    """

    EssayOptions = [
        discord.SelectOption(label='Essay Reviser'),
        discord.SelectOption(label='Other')
    ]

    EnglishOptions = [
        discord.SelectOption(label='English Language'),
        discord.SelectOption(label='English Literature'),
        discord.SelectOption(label='Other')
    ]

    MathOptions = [
        discord.SelectOption(label='Algebra'),
        discord.SelectOption(label='Geometry'),
        discord.SelectOption(label='Precalculous'),
        discord.SelectOption(label='Calculous'),
        discord.SelectOption(label='Statistics'),
        discord.SelectOption(label='Other')
    ]

    ScienceOptions = [
        discord.SelectOption(label='Biology'),
        discord.SelectOption(label='Chemistry'),
        discord.SelectOption(label='Biology'),
        discord.SelectOption(label='Physics'),
        discord.SelectOption(label='Psych'),
        discord.SelectOption(label='Other')
    ]

    SocialStudiesOptions = [
        discord.SelectOption(label='World History'),
        discord.SelectOption(label='US History'),
        discord.SelectOption(label='US Gov'),
        discord.SelectOption(label='Euro'),
        discord.SelectOption(label='Human Geo'),
        discord.SelectOption(label='Economy Helper'),
        discord.SelectOption(label='Other')
    ]

    LanguageOptions = [
        discord.SelectOption(label='French'),
        discord.SelectOption(label='Chinese'),
        discord.SelectOption(label='Korean'),
        discord.SelectOption(label='Spanish'),
        discord.SelectOption(label='Other')
    ]

    OtherOptions = [
        discord.SelectOption(label='Computer Science'),
        discord.SelectOption(label='Fine Arts'),
        discord.SelectOption(label='Research'),
        discord.SelectOption(label='SAT/ACT')
    ]

    decodeName = {
        "['Math Helpers']": "Math Helpers",
        "['Science Helpers']": "Science Helpers",
        "['Social Studies Helpers']": "Social Studies Helpers",
        "['English Helpers']": "English Helpers",
        "['Essay Helpers']": "Essay Helpers",
        "['Language Helpers']": "Language Helpers",
        "['Computer Science Helpers']": "Computer Science Helpers",
        "['Fine Art Helpers']": "Fine Art Helpers",
        "['Other Helpers']": "Other Helpers"
    }

    decodeOptList = {
        "['Math Helpers']": MathOptions,
        "['Science Helpers']": ScienceOptions,
        "['Social Studies Helpers']": SocialStudiesOptions,
        "['English Helpers']": EnglishOptions,
        "['Essay Helpers']": EssayOptions,
        "['Language Helpers']": LanguageOptions,
        "['Computer Science Helpers']": 800479815471333406,
        "['Fine Art Helpers']": 833210452758364210,
        "['Other Helpers']": OtherOptions
    }

    decodeID = {
        "['Math Helpers']": 800472371973980181,
        "['Science Helpers']": 800479815471333406,
        "['Social Studies Helpers']": 800481237608824882,
        "['English Helpers']": 800475854353596469,
        "['Essay Helpers']": 854945037875806220,
        "['Language Helpers']": 800477414361792562,
        "['Computer Science Helpers']": 800479815471333406,
        "['Fine Art Helpers']": 833210452758364210,
        "['Other Helpers']": 825917349558747166
    }
    name = decodeName[value]
    CategoryID = decodeID[value]
    if type(decodeOptList[value]) == int:
        OptList = name
    else:
        OptList = decodeOptList[value]

    return name, CategoryID, OptList


class DropdownTickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mainserver = 805593783684562965
        self.ServerIDs = [805593783684562965, 801974357395636254, 799855854182596618, 815753072742891532]



    @commands.Cog.listener("on_interaction")
    async def TicketDropdown(self, interaction: discord.Interaction):
        InteractionResponse = interaction.data
        print(InteractionResponse)
        

        if interaction.message == None:
            return
        

        try:
            val = InteractionResponse['custom_id']
        except KeyError:
            return

        if interaction.guild_id == self.mainserver and interaction.message.id == 901649671657762866 and InteractionResponse['custom_id'] == 'persistent_view:ticketdrop':
            channel = await self.bot.fetch_channel(interaction.channel_id)
            guild = await self.bot.fetch_guild(interaction.guild_id)
            author = interaction.user
            DMChannel = await author.create_dm()
            
            def check(m):
                return m.content is not None and m.channel == DMChannel and m.author.id is author.id

            ViewResponse = str(InteractionResponse["values"])
            print(ViewResponse)
            TypeSubject, CategoryID, OptList = decodeDict(self, ViewResponse)
            c = discord.utils.get(guild.category_channels, id = CategoryID)

            if not TypeSubject == OptList:
                MiscOptList = discord.ui.View()
                MiscOptList.add_item(SelectMenuHandler(OptList, place_holder = "Select a more specific subject!", select_user = author))
                
                embed = discord.Embed(title = "a) Ticket Info", color = discord.Color.gold())
                await DMChannel.send(embed = embed, view = MiscOptList)
                timeout = await MiscOptList.wait()
                if not timeout:
                    selection_str = MiscOptList.value 
                else:
                    return await DMChannel.send("Timed out, try again later.")
            else:
                selection_str = TypeSubject
            
            embed = discord.Embed(title = "1) Send Question", color = discord.Color.blue())
            await DMChannel.send(embed = embed)
            answer1 = await self.bot.wait_for('message', check=check)

            embed = discord.Embed(title = "2) Send Assignment Title", description = "**Acceptable Forms of Proof:**\n1) Images/Attachments.\n2) URL's such as Gyazo.", color = discord.Color.blue())
            await DMChannel.send(embed = embed)
            answer2 = await self.bot.wait_for('message', check=check)
            attachmentlist = []
            if answer2.attachments:
                for URL in answer2.attachments:
                    attachmentlist.append(URL.url)
            else:
                attachmentlist.append(answer2.content)


            num = len(c.channels)
            channel: discord.TextChannel = await guild.create_text_channel(f'{selection_str}-{num}', category = c)
            await channel.set_permissions(guild.default_role, read_messages = False, reason="Ticket Perms")

            roles = ['Board Member', 'CO', 'VP', 'Head Moderator', 'Moderator', 'Academic Manager', 'Lead Helper', 'Chat Helper', 'Bot: TeXit']
            for role in roles:
                RoleOBJ = discord.utils.get(guild.roles, name=role)
                await channel.set_permissions(RoleOBJ, read_messages = True, send_messages = True, reason="Ticket Perms")
            await channel.set_permissions(interaction.user, read_messages = True, send_messages = True, reason="Ticket Perms (User)")

            controlTicket = discord.Embed(title = "Control Panel", description = "To end this ticket, click the lock button!", color = discord.Colour.gold())
            LockControlButton = discord.ui.View()
            LockControlButton.add_item(ButtonHandler(style=discord.ButtonStyle.green, url=None, disabled=False,
                label="Lock", emoji="🔒", custom_id="ch_lock"))
            await channel.send(interaction.user.mention, embed = controlTicket, view = LockControlButton)

            AttachmentEmbed = discord.Embed(title = "Ticket Information", description = f"**Question:** {answer1}\n**Attachment URL:** (Assignment Title) {str(attachmentlist)}", color=discord.Color.blue())
            AttachmentEmbed.set_image(url = attachmentlist[0])
            await channel.send(embed = AttachmentEmbed)

            query = database.TicketInfo.create(ChannelID = channel.id, authorID = author.id)
            query.save()

        elif InteractionResponse['custom_id'] == 'ch_lock':
            channel = await self.bot.fetch_channel(interaction.channel_id)
            guild: discord.Guild = await self.bot.fetch_guild(interaction.guild_id)
            author = interaction.user

            query = database.TicketInfo.select().where(database.TicketInfo.ChannelID == interaction.channel_id).get()

            embed = discord.Embed(title = "Confirm?", description = "Click an appropriate button.", color = discord.Colour.red())
            ButtonViews = discord.ui.View()
            ButtonViews.add_item(ButtonHandler(style=discord.ButtonStyle.green, label = "Confirm", custom_id = "ch_lock_CONFIRM", emoji = "✅", button_user = author))
            ButtonViews.add_item(ButtonHandler(style=discord.ButtonStyle.red, label = "Cancel", custom_id = "ch_lock_CANCEL", emoji = "❌", button_user = author))
            timeout = await ButtonViews.wait()
            
            if not timeout:
                selection_str = ButtonViews.value 
                if "Confirm" in selection_str:
                    TicketOwner = await guild.fetch_member(query.authorID)
                    await channel.set_permissions(TicketOwner, read_messages = False, reason="Ticket Perms Close (User)")

                    embed = discord.Embed(title = "Support Staff Commands", description = "Click an appropriate button.", color = discord.Colour.red())
                    ButtonViews2 = discord.ui.View()

                    ButtonViews2.add_item(ButtonHandler(style=discord.ButtonStyle.green, label = "Close & Delete Ticket", custom_id = "ch_lock_C&D", emoji = "🔒"))
                    ButtonViews2.add_item(ButtonHandler(style=discord.ButtonStyle.blurple, label = "Create Transcript", custom_id = "ch_lock_T", emoji = "📝"))
                    ButtonViews2.add_item(ButtonHandler(style=discord.ButtonStyle.red, label = "Cancel", custom_id = "ch_lock_C", emoji = "❌"))

                    await channel.send(embed = embed, view = ButtonViews2)

                else:
                    await channel.send(f"{author.mention} Alright, canceling request.")
            else:
                await channel.send(f"{author} Timed out, try again later.")

        elif InteractionResponse['custom_id'] == 'ch_lock_C':
            channel = await self.bot.fetch_channel(interaction.channel_id)
            author = interaction.user

            await channel.send(f"{author.mention} Alright, canceling request.")
            await interaction.message.delete()

        elif InteractionResponse['custom_id'] == 'ch_lock_T':
            channel = await self.bot.fetch_channel(interaction.channel_id)
            ResponseLogChannel = await self.bot.fetch_channel(767434763337728030)
            author = interaction.user

            msg: discord.Message = await rawExport(self, channel, ResponseLogChannel, author)
            await channel.send(f"Transcript Created!\n> {msg.jump_url}")


    @commands.command()
    async def sendCHTKTView(self, ctx):
        MasterSubjectView = discord.ui.View()
        MasterSubjectView.add_item(SelectMenuHandler(MasterSubjectOptions, "persistent_view:ticketdrop", "masa short", 1,1, interaction_message = "Check your DM's!", ephemeral = True))
        await ctx.send("hello", view=MasterSubjectView)

def setup(bot):
    bot.add_cog(DropdownTickets(bot))
