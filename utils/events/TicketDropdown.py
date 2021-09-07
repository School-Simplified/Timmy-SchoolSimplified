import typing
import discord
from core.common import *
from discord.ext import commands

def decodeDict(self, value: str) -> typing.Union[str, int]:
    """Returns the true value of a dict output and pair value.

    Args:
        value (str): Dict output

    Returns:
        typing.Union[str, int]: Raw output of the Dict and Pair value. 
    """
    decodeName = {
        "['Math Helpers']": "Math Helpers",
        "['Science Helpers']": "Science Helpers",
        "['Social Studies Helpers']": "Social Studies Helpers",
        "['English Helpers']": "English Helpers",
        "['Essay Helpers']": "Essay Helpers",
        "['Language Helpers']": "Language Helpers",
        "['Computer Science Helpers']": "Computer Science Helpers",
        "[Fine Art Helpers']": "Fine Art Helpers",
        "['Other Helpers']": "Other Helpers"
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
    return name, CategoryID



class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    options = [
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

    @discord.ui.select(custom_id='persistent_view:ticketdrop', placeholder='Select a subject you need help with!', min_values=1, max_values=1, options=options)
    async def ticketsubject(self, button: discord.ui.View, interaction: discord.Interaction):
        self.value = True



class DropdownTickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mainserver = 763119924385939498
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

        if interaction.guild_id == self.mainserver and interaction.message.id == 111 and InteractionResponse['custom_id'] == 'persistent_view:ticketdrop':
            return
            channel = await self.bot.fetch_channel(interaction.channel_id)
            guild = await self.bot.fetch_guild(interaction.guild_id)
            author = interaction.user
            
            def check(m):
                return m.content is not None and m.channel == channel and m.author.id is author.id

            ViewResponse = str(InteractionResponse.children[0].values)
            TypeSubject, CategoryID = decodeDict[ViewResponse]
            c = discord.utils.get(guild.category_channels, id = CategoryID)
            
            embed = discord.Embed(title = "Ticket Info", description = TypeSubject, color = discord.Color.red())
            await author.send(embed = embed)
            
            embed = discord.Embed(title = "1) Send Question", color = discord.Color.blue())
            await author.send(embed = embed)
            answer1 = await self.bot.wait_for('message', check=check)

            embed = discord.Embed(title = "2) Send Assignment Title", color = discord.Color.blue())
            await author.send(embed = embed)
            answer2 = await self.bot.wait_for('message', check=check)

            num = len(c.channels)
            channel: discord.TextChannel = await guild.create_text_channel(f'ticket-{num}', category = c)
            await channel.set_permissions(guild.default_role, read_messages = False, reason="Ticket Perms")

            roles = ['Board Member', 'CO', 'VP', 'Head Moderator', 'Moderator', 'Academic Manager', 'Lead Helper', 'Chat Helper', 'Bot: TeXit']
            for role in roles:
                RoleOBJ = discord.utils.get(guild.roles, name=role)
                await channel.set_permissions(RoleOBJ, read_messages = True, send_messages = True, reason="Ticket Perms")
            await channel.set_permissions(interaction.user, read_messages = True, send_messages = True, reason="Ticket Perms (User)")

            #await channel.send(interaction.user.mention, view = )









    @commands.command()
    async def pasteView(self, ctx):
        button = TicketDropdownView()
        await ctx.send("Click something!", view = button)



def setup(bot):
    bot.add_cog(DropdownTickets(bot))
