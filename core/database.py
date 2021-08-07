import os
from datetime import datetime
from pickletools import pyfrozenset
from typing import Text

from discord.enums import ExpireBehavior
from dotenv import load_dotenv
from flask import Flask
from peewee import *
from playhouse.shortcuts import (  # these can be used to convert an item to or from json http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#model_to_dict
    ReconnectMixin, dict_to_model, model_to_dict)
from playhouse.sqlite_ext import RowIDField

load_dotenv()

'''
Change to a SqliteDatabase if you don't have any MySQL Credentials.
If you do switch, comment/remove the MySQLDatabase variable and uncomment/remove the # from the SqliteDatabase instance. 
'''

db = MySQLDatabase(os.getenv("DatabaseName"), user=os.getenv("Username"), password=os.getenv("Password"),host= os.getenv("IP"), port = int(os.getenv("PORT")))
#db = SqliteDatabase("data.db")

def iter_table(model_dict):
    """Iterates through a dictionary of tables, confirming they exist and creating them if necessary."""
    for key in model_dict:
        if not db.table_exists(key):
            db.connect(reuse_if_open=True)
            db.create_tables([model_dict[key]])
            db.close()



'''
DATABASE FILES

This file represents every database table and the model they follow. When fetching information from the tables, consult the typehints for possible methods!

'''


class BaseModel(Model):
    """Base Model class used for creating new tables."""
    class Meta:
        database = db


class VCChannelInfo(BaseModel):
    '''
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

    `TutorBotSessionID` = TextField(default=None)
    Signifies if the voice channel is linked to a TutorSession, if so this attribute contains its ID. 
    '''

    id = AutoField()
    ChannelID = TextField()
    name = TextField()
    authorID = TextField()
    datetimeObj = DateTimeField()
    used = BooleanField()
    lockStatus = TextField()

    TutorBotSessionID = TextField(default=None)

class IgnoreThis(BaseModel):
    '''
    # IgnoreThis
    Information pertaining to the Deletion of Voice Channels

    `ID`: AutoField()
    Database Entry Number.

    `ChannelID`: TextField()
    Channel ID.

    `authorID`: TextField()
    Owner of the voice channel being deleted.
    '''

    id = AutoField()
    channelID = TextField()
    authorID = TextField()

class HelperTally(BaseModel):
    '''
    DEPRECATED
    '''
    id = AutoField()
    userID = TextField()
    CS = IntegerField(default = 0)
    English = IntegerField(default = 0)
    Language = IntegerField(default = 0)
    Math = IntegerField(default = 0)
    Science = IntegerField(default = 0)
    SocialStudies = IntegerField(default = 0)
    Algebra = IntegerField(default = 0)
    Geometry = IntegerField(default = 0)
    Precalc = IntegerField(default = 0)
    Calc = IntegerField(default = 0)
    Statistics = IntegerField(default = 0)
    EnglishLang = IntegerField(default = 0)
    EnglishLit = IntegerField(default = 0)
    Research = IntegerField(default = 0)
    Seminar = IntegerField(default = 0)
    Bio = IntegerField(default = 0)
    Chem = IntegerField(default = 0)
    Physics = IntegerField(default = 0)
    ASL = IntegerField(default = 0)
    Chinese = IntegerField(default = 0)
    French = IntegerField(default = 0)
    German = IntegerField(default = 0)
    Italian = IntegerField(default = 0)
    Latin = IntegerField(default = 0)
    Korean = IntegerField(default = 0)
    Russian = IntegerField(default = 0)
    Spanish = IntegerField(default = 0)
    Econ = IntegerField(default = 0)
    Euro = IntegerField(default = 0)
    Psych = IntegerField(default = 0)
    USGov = IntegerField(default = 0)
    USHistory = IntegerField(default = 0)
    WorldHistory = IntegerField(default = 0)


class QuestionTimestamp(BaseModel):
    '''
    DEPRECATED
    '''
    id = PrimaryKeyField()
    userID = TextField()
    date = TextField()
    subject = TextField()
    question = TextField()


class Response(BaseModel):
    '''
    DEPRECATED
    '''

    id = AutoField()
    CommunityService = TextField(default="NONE")
    Recommendation = TextField(default="NONE")
    AcademicHour = TextField(default="NONE")
    Design = TextField(default="NONE")
    PR = TextField(default="NONE")
    Marketing = TextField(default="NONE")
    Analytics = TextField(default="NONE")
    Tech = TextField(default="NONE")
    BreakApproval = TextField(default="NONE")

class ExtraResponse(BaseModel):
    '''
    ExtraResponse Records for StaffInformation Tickets
    DEPRECATED
    '''
    id = AutoField()
    topic = TextField()
    field1 = TextField()
    field2 = TextField(default="NONE")
    field3 = TextField(default="NONE")
    field4= TextField(default="NONE")
    field4= TextField(default="NONE")

class EmailsVersion2(BaseModel):
    '''
    DEPRECATED
    '''

    id = AutoField()
    supervisorID = TextField()
    supervisorEmail = TextField()

class ChannelInfo(BaseModel):
    '''
    DEPRECATED
    '''

    id = AutoField()
    ChannelID = TextField()
    topic = TextField()
    authorID = TextField()
    status = TextField()

class Tag(BaseModel):
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
    

class Administrators(BaseModel):
    '''
    Administrators: 
    List of users who are whitelisted on the bot.

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID

    `TierLevel`: IntegerField()
    TIER LEVEL

    >>> 1 - Bot Manager\n
    >>> 2 - Admin\n
    >>> 3 - Sudo Admin\n
    >>> 4 - Owner
    '''

    id = AutoField()
    discordID = BigIntegerField(unique = True)

    TierLevel = IntegerField(default=1)

class AdminLogging(BaseModel):
    '''
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
    '''

    id = AutoField()
    discordID = BigIntegerField()

    action = TextField()
    content = TextField(default = "N/A")

    datetime = DateTimeField(default = datetime.now())

class CheckInformation(BaseModel):
    '''
    # CheckInformation: 
    List of users who are whitelisted on the bot.

    `id`: AutoField()
    Database Entry

    `MasterMaintenance`: BooleanField()
    Ultimate Check; If this is enabled no one except Permit 4+ users are allowed to use the bot.\n
    >>> **NOTE:** This attribute must always have a bypass to prevent lockouts, otherwise this check will ALWAYS return False.

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
    '''

    id = AutoField()

    MasterMaintenance = BooleanField()
    guildNone = BooleanField()
    externalGuild = BooleanField()
    ModRoleBypass = BooleanField()
    ruleBypass = BooleanField()
    publicCategories = BooleanField()
    elseSituation = BooleanField()

class Blacklist(BaseModel):
    '''
    # Blacklist: 
    List of users who are blacklisted on the bot.

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID
    '''

    id = AutoField()

    discordID = BigIntegerField(unique = True)

class ToDo(BaseModel):
    '''
    # ToDo: 
    ToDo Command (WIP)

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID/owner that the specific item is assigned/associated with.

    `item`: TextField()
    ToDo Item.

    '''

    id = AutoField()

    discordID = BigIntegerField()
    item = TextField()

class MotivationalQuotes(BaseModel):
    '''
    # MotivationalQuotes

    `id`: AutoField()
    Database Entry

    `discordID`: BigIntegerField()
    Discord ID/owner that the specific item is assigned/associated with.

    `item`: TextField()
    Either a quote or message

    `typeObj`: TextField()
    Signifies what the *item* is. (Returns either Quote or Inspirational Message)

    '''

    id = AutoField()
    discordID = BigIntegerField()
    item = TextField(unique = True)
    typeObj = TextField()


class WhitelistedPrefix(BaseModel):
    '''
    # WhitelistedPrefix

    `id`: AutoField()
    Database Entry

    `prefix`: TextField()
    Prefix Entry

    `status`: BooleanField()
    Either shows if its disabled or enabled.
    '''

    id = AutoField()
    prefix = TextField()
    status = BooleanField()


class TutorBot_Sessions(BaseModel):
    '''
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
    '''

    id = AutoField()
    SessionID = TextField()
    Date = DateTimeField()
    Time = TextField()
    Subject = TextField()
    StudentID = BigIntegerField()
    TutorID = BigIntegerField()
    Repeat = BooleanField()
    
class Uptime(BaseModel):
    '''
    #Uptime

    `id`: AutoField()
    Database Entry

    `UpStart`: FloatField()
    Time Object of Bot being started.
    '''
    id = AutoField()
    UpStart = FloatField()

app = Flask(__name__)

@app.before_request
def _db_connect():
    '''
    This hook ensures that a connection is opened to handle any queries
    generated by the request.
    '''
    db.connect()


@app.teardown_request
def _db_close(exc):
    '''
    This hook ensures that the connection is closed when we've finished
    processing the request.
    '''
    if not db.is_closed():
        db.close()

tables = {
    "VoiceChannelInfo" : VCChannelInfo, 
    "IgnoreThis": IgnoreThis, 
    "helpertally": HelperTally, 
    "questiontimestamp": QuestionTimestamp, 
    "tag": Tag, 
    "ChannelInfo" : ChannelInfo, 
    "Response": Response, 
    "ExtraResponse": ExtraResponse, 
    "EmailsVersion2": EmailsVersion2,
    "Administrators": Administrators, 
    "AdminLogging": AdminLogging, 
    "CheckInformation": CheckInformation, 
    "Blacklist": Blacklist,
    "ToDO": ToDo,
    "WhitelistedPrefix": WhitelistedPrefix
}

iter_table(tables)
