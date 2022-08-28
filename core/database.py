import os
from datetime import datetime
from distutils.util import strtobool

from dotenv import load_dotenv
from flask import Flask
import peewee
from peewee import (
    AutoField,
    BigIntegerField,
    BooleanField,
    CharField,
    DateTimeField,
    IntegerField,
    Model,
    MySQLDatabase,
    SqliteDatabase,
    TextField,
)

from core.logging_module import get_log

load_dotenv()
_log = get_log(__name__)
useDB = True

if not os.getenv("PyTestMODE"):
    useDB = input(
        "Do you want to use MySQL? (y/n)\nThis option should be avoided if you are testing new database structures, "
        "do not use MySQL Production if you are testing table modifications. "
    )
    useDB = strtobool(useDB)

"""
Change to a SqliteDatabase if you don't have any MySQL Credentials.
If you do switch, comment/remove the MySQLDatabase variable and uncomment/remove the # from the SqliteDatabase instance. 
"""

if os.getenv("DATABASE_IP") is None:
    db = SqliteDatabase("data.db")
    _log.info("No Database IP found in .env file, using SQLite!")

elif os.getenv("DATABASE_IP") is not None:
    # useDB = bool(input(f"{bcolors.WARNING}Do you want to use MySQL? (y/n)\n    > This option should be avoided if you are testing new database structures, do not use MySQL Production if you are testing table modifications.{bcolors.ENDC}"))
    if useDB:
        try:
            db = MySQLDatabase(
                os.getenv("DATABASE_COLLECTION"),
                user=os.getenv("DATABASE_USERNAME"),
                password=os.getenv("DATABASE_PASSWORD"),
                host=os.getenv("DATABASE_IP"),
                port=int(os.getenv("DATABASE_PORT")),
            )
            _log.info("Successfully connected to the MySQL Database")
        except Exception as e:
            _log.warning(
                f"Unable to connect to the MySQL Database:\n    > {e}\n\nSwitching to SQLite..."
            )
            db = SqliteDatabase("data.db")
    else:
        db = SqliteDatabase("data.db")
        if not os.getenv("PyTestMODE"):
            _log.info(f"Successfully connected to the SQLite Database")
        else:
            _log.info(f"Testing environment detected, using SQLite Database")


def iter_table(model_dict: dict):
    """Iterates through a dictionary of tables, confirming they exist and creating them if necessary."""
    for key in model_dict:
        if not db.table_exists(key):
            db.connect(reuse_if_open=True)
            db.create_tables([model_dict[key]])
            db.close()
        else:
            db.connect(reuse_if_open=True)
            for column in model_dict[key]._meta.sorted_fields:
                if not db.column_exists(key, column.name):
                    db.create_column(key, column.name)
            db.close()


"""
DATABASE FILES

This file represents every database table and the model they follow. When fetching information from the tables, consult the typehints for possible methods!

"""


class BaseModel(Model):
    """Base Model class used for creating new tables."""

    class Meta:
        database = db


class VCChannelInfo(BaseModel):
    """
    # VCChannelInfo
    Information pertaining to Private Voice Channels

    `ID`: AutoField()
    Database Entry Number.

    `ChannelID`: TextField()
    Channel ID.

    `name`: TextField()
    Current name of the channel. *This field can be modified after creation.*

    `authorID`: TextField()
    Owner of the voice channel.

    `datetimeObj` DateTimeField()
    DateTime Object that was created when the voice channel was formed.

    `used` BooleanField()
    **DEPRECATED**: Signifies if the voice channel is active.
    *When a voice session is archived, the database entry will also be deleted. Using this attribute will no longer work.*

    `lockStatus` = bool(TextField())
    Signifies if the voice channel is locked or not.

    `GuildID` = BigIntegerField()
    Guild ID of the Voice Channel.

    `TutorBotSessionID` = TextField(default=None)
    Signifies if the voice channel is linked to a TutorSession, if so this attribute contains its ID.
    """

    id = AutoField()
    ChannelID = TextField()
    name = TextField()
    authorID = TextField()
    datetimeObj = DateTimeField()
    used = BooleanField()
    lockStatus = TextField()
    GuildID = BigIntegerField()

    TutorBotSessionID = TextField(default=None)


class IgnoreThis(BaseModel):
    """
    # IgnoreThis
    Information pertaining to the Deletion of Voice Channels

    `ID`: AutoField()
    Database Entry Number.

    `ChannelID`: TextField()
    Channel ID.

    `authorID`: TextField()
    Owner of the voice channel being deleted.

    `GuildID` = BigIntegerField()
    Guild ID of the Voice Channel.
    """

    id = AutoField()
    channelID = TextField()
    authorID = TextField()
    GuildID = BigIntegerField()


class TutorSession_GracePeriod(BaseModel):
    """
    # IgnoreThis
    Information pertaining to the Deletion of Tutor Sessions

    `ID`: AutoField()
    Database Entry Number.

    `SessionID`: TextField()
    Session ID.

    `authorID`: TextField()
    Owner of the tutor session.

    `ext_ID` = BigIntegerField()
    ID of the correlating database entry.

    `GP_DATE` = DateTimeField()
    DateTime Object with built-in grace period of 10 minutes.
    """

    id = AutoField()
    SessionID = TextField()
    authorID = TextField()
    ext_ID = IntegerField()
    GP_DATE = DateTimeField()


class PunishmentTag(BaseModel):
    """
    #Tag
    Stores our tags accessed by the tag command.

    `id`: AutoField()
    Database Entry

    `tag_name`: TextField()
    Name of the tag

    `text`: TextField()
    Embed Description

    `imageURL`: TextField()
    URL of the image
    """

    id = AutoField()
    tag_name = TextField(unique=True)
    embed_title = TextField()
    text = TextField()
    imageURL = TextField(default=None)


class CTag(BaseModel):
    """
    #CTag
    Stores our tags accessed by the tag command.

    `id`: AutoField()
    Database Entry

    `tagname`: TextField()
    Name of the tag

    `text`: TextField()
    Embed Description

    `imageURL`: TextField()
    URL of the image
    """

    id = AutoField()
    tagname = TextField()
    embedtitle = TextField()
    text = TextField()
    imageURL = TextField(default=None)


class Administrators(BaseModel):
    """
    Administrators:
    List of users who are whitelisted on the bot.

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID

    `TierLevel`: IntegerField()
    TIER LEVEL

    1 - Bot Manager\n
    2 - Admin\n
    3 - Sudo Admin\n
    4 - Owner
    """

    id = AutoField()
    discordID = BigIntegerField(unique=True)

    TierLevel = IntegerField(default=1)


class AdminLogging(BaseModel):
    """
    # AdminLogging:
    List of users who are whitelisted on the bot.

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID

    `action`: TextField()
    Command Name

    `content`: TextField()
    `*args` passed in

    `datetime`: DateTimeField()
    DateTime Object when the command was executed.
    """

    id = AutoField()
    discordID = BigIntegerField()

    action = TextField()
    content = TextField(default="N/A")

    datetime = DateTimeField(default=datetime.now())


class CheckInformation(BaseModel):
    """
    # CheckInformation:
    List of users who are whitelisted on the bot.

    `id`: AutoField()
    Database Entry

    `MasterMaintenance`: BooleanField()
    Ultimate Check; If this is enabled no one except Permit 4+ users are allowed to use the bot.\n
    '>>> **NOTE:** This attribute must always have a bypass to prevent lockouts, otherwise this check will ALWAYS return False.

    `guildNone`: BooleanField()
    If commands executed outside of guilds (DMs) are allowed.

    `externalGuild`: BooleanField()
    If commands executed outside of the main guild (Staff Servers, etc) are allowed.

    `ModRoleBypass`: BooleanField()
    If commands executed inside of a public/general channel by a mod+ is allowed.

    `ruleBypass`: BooleanField()
    If the command *rule* is executed in public/general channels is allowed.

    `publicCategories`: BooleanField()
    If any command (except rule) inside of a public/general channel is allowed.

    `elseSituation`: BooleanField()
    Other situations will be defaulted to/as ...

    `PersistantChange`: BooleanField()
    If the discord bot has added its persistant buttons/views.
    """

    id = AutoField()

    MasterMaintenance = BooleanField()
    guildNone = BooleanField()
    externalGuild = BooleanField()
    ModRoleBypass = BooleanField()
    ruleBypass = BooleanField()
    publicCategories = BooleanField()
    elseSituation = BooleanField()
    PersistantChange = BooleanField()


class Blacklist(BaseModel):
    """
    # Blacklist:
    List of users who are blacklisted on the bot.

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID
    """

    id = AutoField()

    discordID = BigIntegerField(unique=True)


class ResponseSpamBlacklist(BaseModel):
    """
    # Blacklist:
    List of users who are blacklisted from suggesting to the SET team.

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID
    """

    id = AutoField()

    discordID = BigIntegerField(unique=True)


class ToDo(BaseModel):
    """
    # ToDo:
    ToDo Command (WIP)

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID/owner that the specific item is assigned/associated with.

    `item`: TextField()
    ToDo Item.

    """

    id = AutoField()

    discordID = BigIntegerField()
    item = TextField()


class StudyToDo(BaseModel):
    """
    # StudyToDo:
    The to-dos for the StudyBot.

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID/owner that the specific item is assigned/associated with.

    `item`: TextField()
    Study To-Do Item.
    """

    id = AutoField()
    discordID = BigIntegerField()
    item = TextField()


class WhitelistedPrefix(BaseModel):
    """
    # WhitelistedPrefix

    `id`: AutoField()
    Database Entry

    `prefix`: TextField()
    Prefix Entry

    `status`: BooleanField()
    Either shows if its disabled or enabled.
    """

    id = AutoField()
    prefix = TextField()
    status = BooleanField()


class TutorBot_Sessions(BaseModel):
    """
    #TutorBot Sessions

    `id`: AutoField()
    Database Entry

    `SessionID`: TextField()
    2-3 Character ID for the specific session.

    `Date`: DateTimeField()
    Timezone Field.

    `Time`: TextField()
    Time Field.

    `Subject`: TextField()
    Subject Field.

    `StudentID`: BigIntegerField()
    Discord ID of the Student.

    `TutorID`: BigIntegerField()
    Discord ID of the Tutor.

    `Repeat`: BooleanField()
    Boolean that states if this session is repeated.

    `ReminderSet`: BooleanField()
    Boolean that states if the user and student have been notified.

    `GracePeriod_Status`: BooleanField()
    Boolean that states if the session is about to expire.
    """

    id = AutoField()
    SessionID = TextField()
    Date = DateTimeField()
    Time = TextField()
    Subject = TextField()
    StudentID = BigIntegerField()
    TutorID = BigIntegerField()
    Repeat = BooleanField()
    ReminderSet = BooleanField()
    GracePeriod_Status = BooleanField(default=False)


class TicketInfo(BaseModel):
    """
    #TicketInfo

    `id`: AutoField()
    Database Entry

    `ChannelID`: BigIntegerField()
    Channel ID of the Ticket.

    `authorID`: BigIntegerField()
    Author ID of the Ticket Owner.

    `createdAt`: DateTimeField()
    A datetime object when the ticket opened.
    """

    id = AutoField()
    ChannelID = BigIntegerField()
    authorID = BigIntegerField()
    createdAt = DateTimeField()


class BaseTickerInfo(BaseModel):
    """
    #BaseTickerInfo

    `id`: AutoField()
    Database Entry

    `counter`: BigIntegerField()
    Counter for the total amount of channels.

    `guildID`: BigIntegerField()
    Guild ID.
    """

    id = AutoField()
    counter = BigIntegerField()
    guildID = BigIntegerField()


class VCDeletionQueue(BaseModel):
    """
    #VCDeletionQueue

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID of the user.

    `ChannelID`: BigIntegerField()
    Channel ID of the Voice Channel.

    `GuildID`: BigIntegerField()
    Guild ID of the Voice Channel.

    `DTF`: DateTimeField()
    DateTime Object of when the Voice Channel was scheduled to be deleted.
    """

    id = AutoField()
    discordID = BigIntegerField()
    ChannelID = BigIntegerField()
    GuildID = BigIntegerField()
    DTF = DateTimeField()


class TechCommissionArchiveLog(BaseModel):
    """
    #TechCommissionArchiveLog

    `id`: AutoField()
    Database Entry

    `ThreadID`: BigIntegerField()
    ID of the thread.
    """

    id = AutoField()
    ThreadID = BigIntegerField()


class SandboxConfig(BaseModel):
    """
    #SandboxConfig

    `id`: AutoField()
    Database Entry

    `mode`: TextField()
    Current Mode of the Sandbox.
    """

    id = AutoField()
    mode = TextField()

    cat_mathticket = BigIntegerField(default=0)
    cat_scienceticket = BigIntegerField(default=0)
    cat_socialstudiesticket = BigIntegerField(default=0)
    cat_essayticket = BigIntegerField(default=0)
    cat_englishticket = BigIntegerField(default=0)
    cat_otherticket = BigIntegerField(default=0)
    cat_fineartsticket = BigIntegerField(default=0)
    cat_languageticket = BigIntegerField(default=0)

    ch_tv_console = BigIntegerField(default=0)
    ch_tv_startvc = BigIntegerField(default=0)


class Voting(BaseModel):
    """
    #Voting

    `msgID`: BigIntegerField(primary_key)
    The ID of the message

    `components`: CharField()
    A dict as a string which includes a component of the message (`msgID`) as a key and the count of the component as a value.
    """

    msgID = BigIntegerField(primary_key=True)
    components = CharField()


class BaseQueue(BaseModel):
    """
    #BaseQueue

    `id`: AutoField()
    Database Entry

    `queueID`: BigIntegerField()
    Type of queue.
    """

    id = AutoField()
    queueID = BigIntegerField()


class StudyVCDB(BaseModel):
    """
    #StudyVCDB

    `id`: AutoField()
    Database Entry ID

    `discordID`: BigIntegerField()
    Discord ID of the user.

    `Goal`: TextField()
    Goal of the current study session.

    `StartTime`: DateTimeField()
    DateTime Object of when the session started.

    `RenewalTime`: DateTimeField()
    DateTime Object of when the session will renew.

    `Paused`: BooleanField()
    Boolean that states if the session is paused.
    """

    id = AutoField()
    discordID = BigIntegerField()
    Goal = TextField()
    StartTime = DateTimeField()
    RenewalTime = DateTimeField()
    Paused = BooleanField(default=False)


class StudyVCLeaderboard(BaseModel):
    """
    #StudyVCLeaderboard

    `id`: AutoField()
    Database Entry ID

    `discordID`: BigIntegerField()
    Discord ID of the user.

    `TTS`: BigIntegerField()
    Total time spent studying. (Measured in Minutes)

    `TTSWeek`: BigIntegerField()
    Total time spent in current week. This value gets reset every week (Monday Midnight) (Measured in Minutes)

    `totalSessions`: BigIntegerField()
    Total number of sessions.

    `level`: IntegerField()
    The level the user has.

    `xp`: IntegerField()
    The current xp, which get reset when new level reached.

    `totalXP`: IntegerField()
    The total XP, which the user has.
    """

    id = AutoField()
    discordID = BigIntegerField()
    TTS = BigIntegerField(default=0)
    TTSWeek = BigIntegerField(default=0)
    totalSessions = BigIntegerField(default=0)
    level = IntegerField(default=0)
    xp = BigIntegerField(default=0)
    totalXP = BigIntegerField(default=0)


class AuthorizedGuilds(BaseModel):
    """
    #AuthorizedGuilds

    `id`: AutoField()
    Database Entry ID

    `guildID`: BigIntegerField()
    Guild ID of the guild.

    `authorizedUserID`: BigIntegerField()
    User ID of the user who authorized the guild.
    """

    id = AutoField()
    guildID = BigIntegerField()
    authorizedUserID = BigIntegerField()


class SetPuzzleSchedule(BaseModel):
    id = AutoField()


class CommandAnalytics(BaseModel):
    """
    #CommandAnalytics

    `id`: AutoField()
    Database Entry ID

    `command`: TextField()
    The command that was used.

    `user`: IntegerField()
    The user that used the command.

    `date`: DateTimeField()
    The date when the command was used.

    `command_type`: TextField()
    The type of command that was used.

    `guild_id`: BigIntegerField()
    The guild ID of the guild that the command was used in.
    """

    id = AutoField()
    command = TextField()
    date = DateTimeField()
    command_type = TextField()
    guild_id = BigIntegerField()
    user = BigIntegerField()


class MGMTickets(BaseModel):
    """
    #MGMTickets

    `id`: AutoField()
    Database Entry

    `ChannelID`: BigIntegerField()
    Channel ID of the Ticket.

    `authorID`: BigIntegerField()
    Author ID of the Ticket Owner.

    `createdAt`: DateTimeField()
    A datetime object when the ticket opened.

    `configuration_id`: TextField()
    The related configuration ID of the ticket.
    """

    id = AutoField()
    ChannelID = BigIntegerField()
    authorID = BigIntegerField()
    createdAt = DateTimeField()
    configuration_id = TextField(default=None)


class TicketConfiguration(BaseModel):
    """
    #Tickets

    `id`: AutoField()
    Database Entry

    `guild_id` = BigIntegerField()
    Guild ID of the guild the ticket config is in.

    `channel_id`: BigIntegerField()
    Channel ID of where tickets originated.

    `category_id`: BigIntegerField()
    Category ID of where tickets go.

    `transcript_channel_id`: BigIntegerField()
    Channel ID of where transcripts go.

    `title`: TextField()
    Title of the form.

    `channel_identifier`: TextField()
    The channel identifier of the ticket.

    `button_label`: TextField()
    The label of the button.

    `role_id`: TextField()
    Role ID of the role that can view the ticket.

    `author_id`: BigIntegerField()
    Owner of ticket configuration

    `limit`: IntegerField()
    Limit of tickets per user.

    `questions`: TextField()
    Questions that are asked in the ticket. | Default to None if not set.

    `question_config` = TextField(default=None)
    Question configuration. | Default to None if not set.

    `q1_config` = TextField(default=None)
    `q2_config` = TextField(default=None)
    `q3_config` = TextField(default=None)
    `q4_config` = TextField(default=None)
    `q5_config` = TextField(default=None)
    Question configuration. | Default to None if not set.
    > Format: S/L , Char. Limit Min, Char. Limit Max


    `created_at`: DateTimeField()
    DateTime object when ticket configuration was created.
    """

    id = AutoField()
    guild_id = BigIntegerField()
    channel_id = BigIntegerField()
    category_id = BigIntegerField()
    transcript_channel_id = BigIntegerField()
    title = TextField()
    channel_identifier = TextField()
    button_label = TextField()
    role_id = TextField()
    author_id = BigIntegerField()
    limit = IntegerField()
    questions = TextField(default=None)
    q1_config = TextField(default=None)
    q2_config = TextField(default=None)
    q3_config = TextField(default=None)
    q4_config = TextField(default=None)
    q5_config = TextField(default=None)
    question_config = TextField(default=None)
    created_at = DateTimeField()


class RedirectLogs(BaseModel):
    """
    #RedirectLogs
    `id`: AutoField()
    Database Entry ID

    `redirect_id`: BigIntegerField()
    Redirect ID of the redirect. (Corresponds to the ID schema for Redirect.Pizza's API)

    `from_url`: TextField()
    The URL that was redirected from.

    `to_url`: TextField()
    The URL that was redirected to.

    `subdomain`: TextField()
    The subdomain the from_url uses.

    `author_id`: BigIntegerField()
    The author ID of the user that made the redirect.

    `created_at`: DateTimeField()
    The date when the redirect was made.
    """

    id = AutoField()
    redirect_id = BigIntegerField(unique=False)
    from_url = TextField(unique=False)
    to_url = TextField(unique=False)
    subdomain = TextField(default=None)
    author_id = BigIntegerField(unique=False)
    created_at = DateTimeField()


class ApprovedSubDomains(BaseModel):
    """
    #ApprovedSubDomains

    `id`: AutoField()
    Database Entry

    `sub_domain`: TextField()
    Domain that is approved.

    `author_id`: BigIntegerField()
    Author ID of the user that requested the domain.
    """

    id = AutoField()
    sub_domain = TextField()
    author_id = BigIntegerField()


class APIRouteTable(BaseModel):
    username = TextField()
    authorized_routes = TextField()
    hashed_password = TextField()
    disabled = BooleanField()
    created_at = DateTimeField(default=peewee.datetime.datetime.now)


app = Flask(__name__)


@app.before_request
def _db_connect():
    """
    This hook ensures that a connection is opened to handle any queries
    generated by the request.
    """
    db.connect()


@app.teardown_request
def _db_close(exc):
    """
    This hook ensures that the connection is closed when we've finished
    processing the request.
    """
    if not db.is_closed():
        db.close()


tables = {
    "VoiceChannelInfo": VCChannelInfo,
    "IgnoreThis": IgnoreThis,
    "Administrators": Administrators,
    "AdminLogging": AdminLogging,
    "CheckInformation": CheckInformation,
    "Blacklist": Blacklist,
    "ToDO": ToDo,
    "StudyToDo": StudyToDo,
    "WhitelistedPrefix": WhitelistedPrefix,
    "TutorBot_Sessions": TutorBot_Sessions,
    "TicketInfo": TicketInfo,
    "PunishmentTag": PunishmentTag,
    "CTag:": CTag,
    "BaseTickerInfo": BaseTickerInfo,
    "VCDeletionQueue": VCDeletionQueue,
    "TutorSession_GracePeriod": TutorSession_GracePeriod,
    "TechCommissionArchiveLog": TechCommissionArchiveLog,
    "SandboxConfig": SandboxConfig,
    "Voting": Voting,
    "BaseQueue": BaseQueue,
    "StudyVCDB": StudyVCDB,
    "StudyVCLeaderboard": StudyVCLeaderboard,
    "ResponseSpamBlacklist": ResponseSpamBlacklist,
    "AuthorizedGuilds": AuthorizedGuilds,
    # "SetPuzzleSchedule": SetPuzzleSchedule,
    "CommandAnalytics": CommandAnalytics,
    "MGMTickets": MGMTickets,
    "Ticket_Configuration": TicketConfiguration,
}

"""
This function automatically adds tables to the database if they do not exist,
however it does take a significant amount of time to run so the env variable 'PyTestMODE' should be 'False'
in development. 
"""
if os.getenv("PyTestMODE") == "True":
    print("iter_table")
    iter_table(tables)
