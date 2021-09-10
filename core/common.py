import asyncio
import io
import json
from pathlib import Path
import typing
from typing import List, Tuple

import chat_exporter
import discord
from discord.ext import commands
from discord import Button, ui, ButtonStyle, SelectOption


async def rawExport(self, channel, response, user: discord.User):
    transcript = await chat_exporter.export(channel, None, "EST")

    if transcript is None:
        return

    embed = discord.Embed(title = "Channel Transcript", description = f"**Channel:** {channel.name}\n**User Invoked:** {user.name}*\nTranscript Attached Below*", color = discord.Colour.green())
    transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{channel.name}.html")

    await response.send(embed = embed)
    await response.send(file=transcript_file)

async def paginate_embed(bot: discord.Client, ctx, embed: discord.Embed, population_func, end: int, begin: int = 1, page=1):
    emotes = ["◀️", "▶️"]

    def check_reaction(reaction, user):
        return user == ctx.author and str(reaction.emoji) in emotes

    embed = await population_func(embed, page)
    if isinstance(embed, discord.Embed):
        message = await ctx.send(embed=embed)
    else:
        await ctx.send(str(type(embed)))
        return
    await message.add_reaction(emotes[0])
    await message.add_reaction(emotes[1])
    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check_reaction)
            if user == bot.user:
                continue
            if str(reaction.emoji) == emotes[1] and page < end:
                page += 1
                embed = await population_func(embed, page)
                await message.remove_reaction(reaction, user)
                await message.edit(embed=embed)
            elif str(reaction.emoji) == emotes[0] and page > begin:
                page -= 1
                embed = await population_func(embed, page)
                await message.remove_reaction(reaction, user)
                await message.edit(embed=embed)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            break

def load_config(name) -> Tuple[dict, Path]:
    config_file = Path(f"utils/bots/RoleSync/{name}.json") 
    config_file.touch(exist_ok=True)
    if config_file.read_text() == "":
        config_file.write_text("{}")
    with config_file.open("r") as f:
        config = json.load(f)
    return config, config_file


def prompt_config(msg, key):
    config, config_file = load_config()
    if key not in config:
        config[key] = input(msg)
        with config_file.open("w+") as f:
            json.dump(config, f, indent=4)

def prompt_config2(msg, key):
    config, config_file = load_config()
    config[key] = msg
    with config_file.open("w+") as f:
        json.dump(config, f, indent=4)


class Emoji:
    space = '<:space:834967357632806932>'
    confirm = "<:confirm:860926261966667806>"
    deny = "<:deny:860926229335375892>"
    warn = "<:warn:860926255443345409>"
    lock = "<:lock:860926195087835137>"
    unlock = "<:unlock:860926246937427989>"
    time = "<:time:860926238737825793>"
    loading = None
    redissue = "<:issue:860587949263290368>"
    archive = "<:file:861794167578689547>"
    cycle = "<:cycle:861794132585611324>"
    calender = "<:calendar:861794038739238943>"
    addgear = "<:add5x:862875088311025675>"
    minusgear = "<:minusgear:862875088217702421>"
    invalidchannel = "<:invalidchannel:862875088361619477>"
    barrow = "<:barrow:862572842985193502>"
    person = "<:person:883771751127990333>"
    activity = "<:note:883771751190908989>"


rulesDict = {
    1: f"All Terms of Service and Community Guidelines apply. && {Emoji.barrow} https://discord.com/terms\n{Emoji.barrow} https://discord.com/guidelines",
    2: f"Keep chats and conversations mainly in English. && {Emoji.barrow} Full-blown conversations in a different language that disrupt the environment are not allowed.\n{Emoji.barrow} Disrupting an existing conversation in English in voice chat is not allowed.",
    3: f"Keep chats and conversations relevant. && {Emoji.barrow} Keep discussions about politics or anything else in <#773366189648642069>.\n{Emoji.barrow} Ask homework questions in the homework channels or tickets.",
    4: f"No content that does not belong in a school server. && {Emoji.barrow} No inappropriate avatars, statuses, about me, usernames, or nicknames.\n{Emoji.barrow} No sharing of content that glorifies or promotes suicide or self-harm.\n{Emoji.barrow} No trolling, raiding, epileptic, disturbing, suggestive, or offensive behavior.\n{Emoji.barrow} No sexist, racist, homophobic, transphobic, xenophobic, islamophobic, pedophilic, creepy behavior, etc.",
    5: f"No advertising or self-promotion (unless given explicit permission). && {Emoji.barrow} Self-advertising a website, group, or anything else through DMs, VC or in the server is not allowed.\n{Emoji.barrow} Explicitly asking users to look at advertisements in status/About Me is not allowed.",
    6: f"No toxic behavior or harassment. && {Emoji.barrow} No discriminatory jokes or language towards an individual or group due to race, ethnicity, nationality, sex, gender, sexual orientation, religious affiliation, or disabilities.\n{Emoji.barrow} Disrespect of members is not allowed, especially if it is continuous, repetitive, or severe.\n{Emoji.barrow} Encouraging toxicity, harassment, bullying, and anything of the sort is prohibited.",
    7: f"No illegal or explicit material. && {Emoji.barrow} Discussing or sharing illegal content is prohibited. This includes, but is not limited to: copyrighted content, pirated content, illegal activities, crimes, IPGrabbers, phishing links.\n{Emoji.barrow} Any form of NSFW, NSFL, or explicit content (pornographic, overtly sexual, overly gory) is prohibited.",
    8: f"No DDoS, dox, death or any other sort of threats. && {Emoji.barrow} Indirect or direct threats to harm someone else are strictly prohibited and causes for immediate ban.\n{Emoji.barrow} DDoS (Distributed Denial of Service): sending a large amount of requests in a short amount of time.\n{Emoji.barrow} Dox: revealing any private information of another member, such as real name or address, without consent.",
    9: f"No slurs and excessive or harmful profanity usage. && {Emoji.barrow} Using or attempting to use slurs and racist terms is prohibited.\n{Emoji.barrow} Excessive profanity, verbal abuse and insults are prohibited.",
    10: f"No cheating in any form. && {Emoji.barrow} It is strictly prohibited to cheat or engage in academic dishonesty anywhere in the server.",
    11: f"No spamming in any form. && {Emoji.barrow} Spamming links, images, messages, roles, emojis, emotes, emote reactions, or anything else is not allowed.",
    12: f"No impersonation in any form. && {Emoji.barrow} Changing your username or avatar to something similar as any staff or members with the intent to mimic them and create confusion is prohibited. ",
    13: f"No disruptive behavior in voice chat. && {Emoji.barrow} No continuous hopping between voice chats.\n{Emoji.barrow} No starting and closing streams in short intervals.\n{Emoji.barrow} No loud, annoying, or high-pitched noises.\n{Emoji.barrow} No voice changers if asked to stop.",
    14: f"No evading user blocks, punishments, or bans by using alternate accounts. && {Emoji.barrow} Sending unwanted, repeated friend requests or messages to contact someone who has blocked you is prohibited.\n{Emoji.barrow} Creating alternate accounts to evade a punishment or ban, harass or impersonate someone, or participate in a raid are all strictly prohibited.\n{Emoji.barrow} To discuss punishments or warnings, create a support ticket or talk to a moderator in DMs.",
}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SelectMenuHandler(ui.Select):
    """Adds a SelectMenu to a specific message and returns it's value when option selected.

        Args:
            options (typing.List[SelectOption]): List of discord.SelectOption's
            custom_id (typing.Union[str, None], optional): Custom ID of the View. Defaults to None.
            place_holder (typing.Union[str, None], optional): Place Holder string for the View. Defaults to None.
            max_values (int, optional): Maximum values that are selectable. Defaults to 1.
            min_values (int, optional): Minimum values that are selectable. Defaults to 1.
            disabled (bool, optional): If the button is disabled or not. Defaults to False.
            persistent (bool, optional): If this view is persistent or not. Defaults to True.
            select_user (typing.Union[discord.Member, discord.User, None], optional): The user that can perform this action, leave blank for everyone. Defaults to None.
        """

    def __init__(self,
                 options: typing.List[SelectOption],
                 custom_id: typing.Union[str, None] = None,
                 place_holder: typing.Union[str, None] = None,
                 max_values: int = 1,
                 min_values: int = 1,
                 disabled: bool = False,
                 persistent: bool = True,
                 select_user: typing.Union[discord.Member, discord.User, None] = None,
                 ):
        self.options_ = options
        self.custom_id_ = custom_id
        self.select_user = select_user
        self.disabled_ = disabled
        self.persistent_ = persistent
        self.placeholder_ = place_holder
        self.max_values_ = max_values
        self.min_values_ = min_values
        super().__init__(placeholder=self.placeholder_, options=self.options_, disabled=self.disabled_,
                         max_values=self.max_values_, min_values=self.min_values_)
        if self.custom_id_:
            super().__init__(custom_id=self.custom_id_)

    async def callback(self, interaction: discord.Interaction):
        if self.select_user is None or interaction.user == self.select_user:
            self.view.value = self.values[0]
            
            if not self.persistent_:
                self.view.stop()

class ButtonHandler(ui.Button):
    """Adds a Button to a specific message and returns it's value when pressed.

        Args:
            style (ButtonStyle): Label for the button
            label (typing.Union[str, None], optional): Custom ID that represents this button. Defaults to None.
            custom_id (typing.Union[str, None], optional): Style for this button. Defaults to None.
            emoji (typing.Union[str, None], optional): An emoji for this button. Defaults to None.
            url (typing.Union[str, None], optional): A URL for this button. Defaults to None.
            disabled (bool, optional): If this button should be disabled. Defaults to False.
            persistent (bool, optional): If this view is persistent or not. Defaults to True.
            button_user (typing.Union[discord.Member, discord.User, None], optional): The user that can perform this action, leave blank for everyone. Defaults to None.
        """

    def __init__(self,
                 style: ButtonStyle,
                 label: typing.Union[str, None] = None,
                 custom_id: typing.Union[str, None] = None,

                 emoji: typing.Union[str, None] = None,
                 url: typing.Union[str, None] = None,
                 disabled: bool = False,
                 persistent: typing.Union[float, None] = None,
                 button_user: typing.Union[discord.Member, discord.User, None] = None
                 ):
        self.label_ = label
        self.custom_id_ = custom_id
        self.style_ = style
        self.emoji_ = emoji
        self.url_ = url
        self.disabled_ = disabled
        self.button_user = button_user
        self.persistent_ = persistent
        super().__init__(label=self.label_, custom_id=self.custom_id_, style=self.style_, emoji=self.emoji_,
                         url=self.url_, disabled=self.disabled_, timeout = self.timeout)
        if self.custom_id_:
            super().__init__(custom_id=self.custom_id_)

    async def callback(self, interaction: discord.Interaction):
        if self.button_user is None or self.button_user == interaction.user:
            if self.custom_id_ is None:
                self.view.value = None
            else:
                self.view.value = self.custom_id

            if not self.persistent_:
                self.view.stop()


def getGuildList(bot: commands.Bot, exemptServer: List[int] = None) -> list:
    guildList = []
    for guild in bot.guilds:
        if guild.id in exemptServer:
            continue
        guildList.append(guild.id)

    return guildList