from __future__ import annotations

import asyncio
import io
import json
import os
import random
import re
import string
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import Any, Awaitable, Callable, List, Literal, Tuple, Union, Optional, TYPE_CHECKING

import boto3
import chat_exporter
import configcatclient
import discord
import pytz
import requests
from botocore.exceptions import ClientError
from discord import (
    ButtonStyle,
    SelectOption,
    ui
)
from discord.ext import commands
from dotenv import load_dotenv
from github import Github
from google.cloud import secretmanager
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

from core import database

if TYPE_CHECKING:
    from main import Timmy

from googleapiclient.discovery import build

load_dotenv()

# Module Variables
CoroutineType = Callable[[Any, Any], Awaitable[Any]]
g = Github(os.getenv("GH_TOKEN"))


class ConfigCatClient:
    PS_ID_CC = configcatclient.create_client(os.getenv("PS_ID_CC"))
    SET_ID_CC = configcatclient.create_client(os.getenv("SET_ID_CC"))
    MAIN_ID_CC = configcatclient.create_client(os.getenv("MAINID_CC"))
    STAFF_ID_CC = configcatclient.create_client(os.getenv("STAFFID_CC"))
    DIGITAL_ID_CC = configcatclient.create_client(os.getenv("DIGITALID_CC"))
    TECH_ID_CC = configcatclient.create_client(os.getenv("TECHID_CC"))
    MKT_ID_CC = configcatclient.create_client(os.getenv("MKTID_CC"))
    TUT_ID_CC = configcatclient.create_client(os.getenv("TUTID_CC"))
    CH_ID_CC = configcatclient.create_client(os.getenv("CHID_CC"))
    HR_ID_CC = configcatclient.create_client(os.getenv("HRID_CC"))
    LEADER_ID_CC = configcatclient.create_client(os.getenv("LEADERID_CC"))
    CHECK_DB_CC = configcatclient.create_client(os.getenv("CHECKDB_CC"))
    SANDBOX_CONFIG_CC = configcatclient.create_client_with_auto_poll(
        os.getenv("SANDBOX_CONFIG_CC"),
        poll_interval_seconds=10
    )

class ConsoleColors:
   HEADER = '\033[95m'
   OKBLUE = '\033[94m'
   OKCYAN = '\033[96m'
   OKGREEN = '\033[92m'
   WARNING = '\033[93m'
   FAIL = '\033[91m'
   ENDC = '\033[0m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'

async def raw_export(channel, response, user: discord.User):
    transcript = await chat_exporter.export(channel, None)

    if transcript is None:
        return

    embed = discord.Embed(
        title="Channel Transcript",
        description=f"**Channel:** {channel.name}"
                    f"\n**User Invoked:** {user.name}*"
                    f"\nTranscript Attached Below*",
        color=discord.Colour.green()
    )
    transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{channel.name}.html")

    msg: discord.Message = await response.send(embed=embed, file=transcript_file)
    return msg


async def paginate_embed(
        bot: discord.Client,
        ctx: commands.Context,
        embed: discord.Embed,
        population_func,
        end: int,
        begin: int = 1,
        page=1
):
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


class CompletedButton(discord.ui.Button):
    def __init__(
            self,
            bot: 'Timmy',
            task: Literal[
                "Motivation",
                "Weekly Puzzle",
                "Opportunities",
                "Daily Question",
                "Media Recommendations",
                "Art Appreciation",
                "Daily Laugh",
            ]
    ):
        super().__init__(
            style=discord.ButtonStyle.green,
            label="Completed",
            custom_id="task::completed"
        )
        self.bot = bot
        self.value: Optional[Literal["complete", "incomplete", "busy"]] = "incomplete"
        self._task = task

    async def callback(self, interaction: discord.Interaction) -> None:
        self.value = "complete"
        await interaction.response.send_message("Great!")
        channel = self.bot.get_channel(SETID.ch_reminders)
        await channel.send(f"✅ {self._task} has been completed for today!")
        await interaction.edit_original_message(view=None)
        self.view.stop()


class CannotComplete(discord.ui.Button):
    def __init__(
            self,
            bot: 'Timmy',
            task: Literal[
                "Motivation",
                "Weekly Puzzle",
                "Opportunities",
                "Daily Question",
                "Media Recommendations",
                "Art Appreciation",
                "Daily Laugh",
            ]
    ):
        super().__init__(
            style=discord.ButtonStyle.red,
            label="Can't Complete",
            custom_id="task::cannotcomplete"
        )
        self.bot = bot
        self.value: Optional[Literal["complete", "incomplete", "busy"]] = "incomplete"
        self._task = task

    async def callback(self, interaction: discord.Interaction) -> Any:
        self.value = "busy"
        await interaction.response.send_message("Notified the team!")
        channel = self.bot.get_channel(SETID.ch_reminders)
        embed = discord.Embed(
            title=f"{self._task} needs to be filled!",
            description=f"{self._task} for today cannot be completed.",
            colour=Colors.red,
            timestamp=discord.utils.utcnow()
        )
        await channel.send(embed=embed)
        await interaction.edit_original_message(view=None)
        self.view.stop()


class ScheduleView(discord.ui.View):
    def __init__(
            self,
            bot: 'Timmy',
            task: Literal[
                "Motivation",
                "Weekly Puzzle",
                "Opportunities",
                "Daily Question",
                "Media Recommendations",
                "Art Appreciation",
                "Daily Laugh",
            ]
    ):
        super().__init__(timeout=None)
        self.bot = bot
        self.__task = task
        self.add_item(CompletedButton(bot, task))
        self.add_item(CannotComplete(bot, task))


def get_extensions():
    extensions = ["jishaku"]
    if sys.platform == "win32" or sys.platform == "cygwin":
        dirpath = "\\"
    else:
        dirpath = "/"

    for file in Path("utils").glob("**/*.py"):
        if "!" in file.name or "DEV" in file.name:
            continue
        extensions.append(str(file).replace(dirpath, ".").replace(".py", ""))
    return extensions


def load_config(name) -> Tuple[dict, Path]:
    config_file = Path(f"utils/bots/RoleSync/{name}.json")
    config_file.touch(exist_ok=True)

    if config_file.read_text() == "":
        config_file.write_text("{}")

    with config_file.open("r") as f:
        config = json.load(f)

    return config, config_file

class CommissionConfirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()

def access_secret(
        secret_id,
        google_auth_load_mode=False,
        type_auth=None,
        scopes=None,
        redirect_uri=None
):
    """
    Access credentials and secrets from Google.

    Args:
        secret_id (str): The secret ID to access. (Options: doc_t, doc_c, tts_c, tsa_c, svc_c, adm_t)

        google_auth_load_mode (bool, optional): If marked as True, the function will return a specific credential class for you to authenticate with an API. Defaults to False.

        type_auth (int, optional): Type of credential class to return.
        (0: oauth2.credentials.Credentials, 1: oauthlib.flow.Flow, 2: oauth2.service_account.Credentials, 3: service_account.ServiceAccountCredentials) Defaults to None.

        scopes (list[str], optional): Scopes to access, this is required when using google_auth_load_mode. Defaults to None.

        redirect_uri (str, optional): Redirect URL to configure, required when using authentication mode 1. Defaults to None.

    Returns:
        Credential Object: Returns a credential object that allows you to authenticate with APIs.
    """

    if os.path.exists("gsheetsadmin/sstimmy.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gsheetsadmin/sstimmy.json"
        client = secretmanager.SecretManagerServiceClient()
    else:
        rawcreds = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(rawcreds)
        client = secretmanager.SecretManagerServiceClient(credentials=creds)

    name = f"projects/ss-timmy/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    if not google_auth_load_mode:
        return payload
    else:
        with open("cred_file.json", "w") as payload_file:
            payload_file.write(payload.replace("'", '"'))

        if type_auth == 0:
            creds = Credentials.from_authorized_user_file("cred_file.json", scopes)
            os.remove("cred_file.json")
        elif type_auth == 1:
            creds = Flow.from_client_secrets_file("cred_file.json", scopes=scopes, redirect_uri=redirect_uri)
            os.remove("cred_file.json")
        elif type_auth == 2:
            creds = service_account.Credentials.from_service_account_file("cred_file.json")
            os.remove("cred_file.json")
        elif type_auth == 3:
            payload: dict = json.loads(payload)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(payload, scopes)
        try:
            os.remove("cred_file.json")
        except:
            pass

        return creds


def S3_upload_file(
        file_name,
        bucket,
        object_name=None
):
    """
    Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)
    # Upload the file
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-2",
    )
    try:
        response = s3_client.upload_file(
            file_name,
            bucket,
            object_name,
            ExtraArgs={"ContentType": "text/html", "ACL": "public-read"},
        )

        # s3_object = s3_client.Object('ch-transcriptlogs', file_name)
        # s3_object.metadata.update({'x-amz-meta-content-type':'text/html'})
        # s3_object.copy_from(CopySource={'Bucket':'ch-transcriptlogs', 'x-amz-meta-content-type':'binary/octet-stream'}, Metadata=s3_object.metadata, MetadataDirective='REPLACE')

    except ClientError as e:
        print(e)


class MainID:
    """
    IDs of the SS Main server.
    NOTE: If you want to add IDs, please use the format as below.

    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    # *** Guilds ***
    g_main = int(ConfigCatClient.MAIN_ID_CC.get_value("g_main", 763119924385939498))

    ch_commands = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_commands", 763409002913595412)
    )
    ch_senior_mods = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_seniormods", 878792926266810418)
    )
    ch_moderators = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_moderators", 786068971048140820)
    )
    ch_muted_chat = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_mutedchat", 808919081469739008)
    )
    ch_mod_logs = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_modlogs", 863177000372666398)
    )
    ch_tutoring = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_tutoring", 865716647083507733)
    )
    ch_transcript_logs = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_transcriptlogs", 767434763337728030)
    )
    ch_action_logs = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_actionlogs", 767206398060396574)
    )
    ch_mod_commands = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_modcommands", 786057630383865858)
    )
    ch_control_panel = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_controlpanel", 843637802293788692)
    )
    ch_start_private_vc = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_startprivatevc", 784556875487248394)
    )
    ch_announcements = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_announcements", 763121175764926464)
    )
    ch_mod_announcements = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_modannouncements", 887780215789617202)
    )
    ch_event_announcements = int(
        ConfigCatClient.MAIN_ID_CC.get_value("ch_eventannouncements", 951302954965692436)
    )

    # *** Categories ***
    cat_casual = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_casual", 763121170324783146))
    cat_community = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_community", 800163651805773824))
    cat_lounge = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_lounge", 774847738239385650))
    cat_events = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_events", 805299289604620328))
    cat_voice = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_voice", 763857608964046899))
    cat_science_ticket = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_scienceticket", 800479815471333406))
    cat_fine_arts_ticket = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_fineartsticket", 833210452758364210))
    cat_math_ticket = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_mathticket", 800472371973980181))
    cat_social_studies_ticket = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_socialstudiesticket", 800481237608824882))
    cat_english_ticket = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_englishticket", 800475854353596469))
    cat_essay_ticket = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_essayticket", 854945037875806220))
    cat_language_ticket = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_languageticket", 800477414361792562))
    cat_other_ticket = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_otherticket", 825917349558747166))
    cat_private_vc = int(ConfigCatClient.MAIN_ID_CC.get_value("cat_privatevc", 776988961087422515))

    # *** Roles ***
    r_coding_club = int(ConfigCatClient.MAIN_ID_CC.get_value("r_codingclub", 883169286665936996))
    r_debate_club = int(ConfigCatClient.MAIN_ID_CC.get_value("r_debateclub", 883170141771272294))
    r_music_club = int(ConfigCatClient.MAIN_ID_CC.get_value("r_musicclub", 883170072355561483))
    r_cooking_club = int(ConfigCatClient.MAIN_ID_CC.get_value("r_cookingclub", 883162279904960562))
    r_chess_club = int(ConfigCatClient.MAIN_ID_CC.get_value("r_chessclub", 883564455219306526))
    r_book_club = int(ConfigCatClient.MAIN_ID_CC.get_value("r_bookclub", 883162511560560720))
    r_advocacy_club = int(ConfigCatClient.MAIN_ID_CC.get_value("r_advocacyclub", 883169000866070539))
    r_speech_club = int(ConfigCatClient.MAIN_ID_CC.get_value("r_speechclub", 883170166161149983))
    r_club_president = int(ConfigCatClient.MAIN_ID_CC.get_value("r_clubpresident", 883160826180173895))
    r_chat_helper = int(ConfigCatClient.MAIN_ID_CC.get_value("r_chathelper", 811416051144458250))
    r_lead_helper = int(ConfigCatClient.MAIN_ID_CC.get_value("r_leadhelper", 810684359765393419))
    r_essay_reviser = int(ConfigCatClient.MAIN_ID_CC.get_value("r_essayreviser", 854135371507171369))
    r_moderator = int(ConfigCatClient.MAIN_ID_CC.get_value("r_moderator", 951302697263452240))
    r_debate_ban = int(ConfigCatClient.MAIN_ID_CC.get_value("r_debateban", 951302659657334784))
    r_ticket_ban = int(ConfigCatClient.MAIN_ID_CC.get_value("r_ticketban", 951302690011492452))
    r_count_ban = int(ConfigCatClient.MAIN_ID_CC.get_value("r_countban", 951302821079318539))

    # *** Messages ***
    msg_math = int(ConfigCatClient.MAIN_ID_CC.get_value("msg_math", 866904767568543744))
    msg_science = int(ConfigCatClient.MAIN_ID_CC.get_value("msg_science", 866904901174427678))
    msg_english = int(ConfigCatClient.MAIN_ID_CC.get_value("msg_english", 866905061182930944))
    msg_language = int(ConfigCatClient.MAIN_ID_CC.get_value("msg_language", 866905971519389787))
    msg_art = int(ConfigCatClient.MAIN_ID_CC.get_value("msg_art", 866906016602652743))
    msg_social_studies = int(ConfigCatClient.MAIN_ID_CC.get_value("msg_socialstudies", 866905205094481951))
    msg_computer_science = int(ConfigCatClient.MAIN_ID_CC.get_value("msg_computerscience", 867550791635566623))


class StaffID:
    """
    IDs of the SS Staff Community server.
    NOTE: If you want to add IDs, please use the format as below.

    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    # *** Guilds ***
    g_staff = int(ConfigCatClient.STAFF_ID_CC.get_value("g_staff", 891521033700540457))
    g_staff_resources = int(ConfigCatClient.STAFF_ID_CC.get_value("g_staff_resources", 955911166520082452))
    g_staff_mgm = int(ConfigCatClient.STAFF_ID_CC.get_value("g_staff_mgm", 824421093015945216))

    # *** Channels ***
    ch_verification_logs = int(ConfigCatClient.STAFF_ID_CC.get_value("ch_verificationlogs", 894241199433580614))
    ch_verification = int(ConfigCatClient.STAFF_ID_CC.get_value("ch_verification", 894240578651443232))
    ch_console = int(ConfigCatClient.STAFF_ID_CC.get_value("ch_console", 895041227123228703))
    ch_start_private_vc = int(ConfigCatClient.STAFF_ID_CC.get_value("ch_startprivatevc", 895041070956675082))
    ch_announcements = int(ConfigCatClient.STAFF_ID_CC.get_value("ch_announcements", 891920066550059028))
    ch_leadership_announcements = int(ConfigCatClient.STAFF_ID_CC.get_value("ch_leadershipannouncements",
                                                                            910357129972551710))

    # *** Categories ***
    cat_private_vc = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_privatevc", 895041016057446411))
    cat_staffapps_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_staffapps_tickets", 979485444364468345))
    cat_announcements_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_announcements", 979485569337946192))

    cat_promote_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_promote_tickets", 956297567346495568))
    cat_demote_tickers = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_demote_tickets", 956297567346495568))
    cat_fire_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_fire_tickets", 956297567346495568))

    cat_censure_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_censure_tickets", 956297567346495568))
    cat_break_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_break_tickets", 992191587281027144))
    cat_resignation_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_resignation_tickets", 992191685415145542))
    cat_suggestions_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_suggestions_tickets", 992191996947083275))
    cat_complaint_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_complaint_tickets", 992191762611327029))
    cat_cs_hours_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_cs_hours_tickets", 992191874309828658))
    cat_suggestion_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_suggestion_tickets", 992191996947083275))

    cat_recruiting_tickets = int(ConfigCatClient.STAFF_ID_CC.get_value("cat_recruiting_tickets", 997646929553018920))


    # *** Roles ***
    r_director = int(ConfigCatClient.STAFF_ID_CC.get_value("r_director", 891521034333880416))
    r_SS_digital_committee = int(ConfigCatClient.STAFF_ID_CC.get_value("r_ssdigitalcommittee", 898772246808637541))
    r_chairperson_SSD_committee = int(ConfigCatClient.STAFF_ID_CC.get_value("r_chairpersonssdcommittee",
                                                                            934971902781431869))
    r_executive_assistant = int(ConfigCatClient.STAFF_ID_CC.get_value("r_executiveassistant", 892535575574372372))
    r_chapter_president = int(ConfigCatClient.STAFF_ID_CC.get_value("r_chapterpresident", 892532950019735602))
    r_organization_president = int(ConfigCatClient.STAFF_ID_CC.get_value("r_organizationpresident",
                                                                         892532907078475816))
    r_vice_president = int(ConfigCatClient.STAFF_ID_CC.get_value("r_vicepresident", 891521034371608671))
    r_president = int(ConfigCatClient.STAFF_ID_CC.get_value("r_president", 932861531224428555))
    r_editor_in_chief = int(ConfigCatClient.STAFF_ID_CC.get_value("r_editorinchief", 910269854592950352))
    r_corporate_officer = int(ConfigCatClient.STAFF_ID_CC.get_value("r_corporateofficer", 932861485917540402))
    r_CHRO = int(ConfigCatClient.STAFF_ID_CC.get_value("r_chro", 892530791005978624))
    r_CIO = int(ConfigCatClient.STAFF_ID_CC.get_value("r_cio", 892530239996059728))
    r_CFO = int(ConfigCatClient.STAFF_ID_CC.get_value("r_cfo", 892530080029503608))
    r_CMO = int(ConfigCatClient.STAFF_ID_CC.get_value("r_cmo", 892529974303686726))
    r_CAO = int(ConfigCatClient.STAFF_ID_CC.get_value("r_cao", 892530033430790165))
    r_COO = int(ConfigCatClient.STAFF_ID_CC.get_value("r_coo", 892530902528307271))
    r_CEO_and_president = int(ConfigCatClient.STAFF_ID_CC.get_value("r_ceoandpresident", 892529865247580160))
    r_board_member = int(ConfigCatClient.STAFF_ID_CC.get_value("r_boardmember", 891521034371608675))
    r_administrative_executive = int(ConfigCatClient.STAFF_ID_CC.get_value("r_administrativeexecutive",
                                                                           946873101956841473))
    r_information_technology = int(ConfigCatClient.STAFF_ID_CC.get_value("r_informationtechnology", 891521034333880410))


class TechID:
    """
    IDs of the 'The Department of Information & Technology' server.
    NOTE: If you want to add IDs, please use the format as below.
    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    # *** Guilds ***
    g_tech = int(ConfigCatClient.TECH_ID_CC.get_value("g_tech", 805593783684562965))

    # *** Channels ***
    ch_tracebacks = int(ConfigCatClient.TECH_ID_CC.get_value("ch_tracebacks", 851949397533392936))
    ch_commission_logs = int(ConfigCatClient.TECH_ID_CC.get_value("ch_commissionlogs", 849722616880300061))
    ch_ticket_log = int(ConfigCatClient.TECH_ID_CC.get_value("ch_ticketlog", 872915565600182282))
    ch_bot_requests = int(ConfigCatClient.TECH_ID_CC.get_value("ch_botreq", 933181562885914724))
    ch_announcements = int(ConfigCatClient.TECH_ID_CC.get_value("ch_announcements", 934109939373314068))
    ch_IT_announcements = int(ConfigCatClient.TECH_ID_CC.get_value("ch_itannouncements", 932066545587327000))
    ch_web_announcements = int(ConfigCatClient.TECH_ID_CC.get_value("ch_webannouncements", 932487991958577152))
    ch_bot_announcements = int(ConfigCatClient.TECH_ID_CC.get_value("ch_botannouncements", 932725755115368478))
    ch_snake_pit = int(ConfigCatClient.TECH_ID_CC.get_value("ch_snakepit", 942076483290161203))

    # *** Roles ***
    r_developer_manager = int(ConfigCatClient.TECH_ID_CC.get_value("r_developermanager", 805596419066822686))
    r_assistant_bot_dev_manager = int(ConfigCatClient.TECH_ID_CC.get_value("r_assistantbotdevmanager",
                                                                           816498160880844802))
    r_bot_developer = int(ConfigCatClient.TECH_ID_CC.get_value("r_botdeveloper", 997238819055222894))


class SandboxConfig:
    """
    IDs for the Sandbox Configuration.
    NOTE: If you want to add IDs, please use the format as below.

    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    mode = str(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("mode", "404"))

    # *** Channels ***
    ch_TV_console = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("ch_tv_console", 404))
    ch_TV_start_vc = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("ch_tv_startvc", 404))

    # *** Categories ***
    cat_sandbox = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("cat_sandbox", 945459539967348787))
    cat_science_ticket = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("cat_scienceticket", 800479815471333406))
    cat_fine_arts_ticket = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("cat_fineartsticket", 833210452758364210))
    cat_math_ticket = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("cat_mathticket", 800472371973980181))
    cat_social_studies_ticket = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("cat_socialstudiesticket",
                                                                                800481237608824882))
    cat_english_ticket = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("cat_englishticket", 800475854353596469))
    cat_essay_ticket = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("cat_essayticket", 854945037875806220))
    cat_language_ticket = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("cat_languageticket", 800477414361792562))
    cat_other_ticket = int(ConfigCatClient.SANDBOX_CONFIG_CC.get_value("cat_otherticket", 825917349558747166))


class ChID:
    """
    IDs of the Chat Helper server.
    NOTE: If you want to add IDs, please use the format as below.

    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    # *** Guilds ***
    g_ch = int(ConfigCatClient.CH_ID_CC.get_value("g_ch", 801974357395636254))
    cat_essay = int(ConfigCatClient.CH_ID_CC.get_value("cat_essay", 854945037875806220))
    cat_english = int(ConfigCatClient.CH_ID_CC.get_value("cat_english", 800475854353596469))


class MktID:
    """
    IDs of the SS Marketing Department server.
    NOTE: If you want to add IDs, please use the format as below.

    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    # *** Guilds ***
    g_mkt = int(ConfigCatClient.MKT_ID_CC.get_value("g_mkt", 799855854182596618))

    # *** Channels ***
    ch_commands = int(ConfigCatClient.MKT_ID_CC.get_value("ch_commands", 799855856295608345))
    ch_commission_transcripts = int(ConfigCatClient.MKT_ID_CC.get_value("ch_commissiontranscripts", 820843692385632287))
    ch_announcements = int(ConfigCatClient.MKT_ID_CC.get_value("ch_announcements", 799855854244855847))
    ch_design_announcements = int(ConfigCatClient.MKT_ID_CC.get_value("ch_designannouncements", 891926914258829323))
    ch_media_announcements = int(ConfigCatClient.MKT_ID_CC.get_value("ch_mediaannouncements", 864050588023259196))
    ch_bp_announcements = int(ConfigCatClient.MKT_ID_CC.get_value("ch_bpannouncements", 852371717744885760))
    ch_events_announcements = int(ConfigCatClient.MKT_ID_CC.get_value("ch_eventsannouncements", 820508373791277067))
    ch_mod_announcements = int(ConfigCatClient.MKT_ID_CC.get_value("ch_modannouncements", 820532007620575282))

    # *** Categories ***
    cat_design = int(ConfigCatClient.MKT_ID_CC.get_value("cat_design", 820873176208375838))
    cat_media = int(ConfigCatClient.MKT_ID_CC.get_value("cat_media", 882031123541143632))
    cat_discord = int(ConfigCatClient.MKT_ID_CC.get_value("cat_discord", 888668259220615198))

    # *** Roles ***
    r_discord_manager = int(ConfigCatClient.MKT_ID_CC.get_value("r_discordmanager", 890778255655841833))
    r_discord_team = int(ConfigCatClient.MKT_ID_CC.get_value("r_discordteam", 805276710404489227))
    r_design_manager = int(ConfigCatClient.MKT_ID_CC.get_value("r_designmanager", 882755765910261760))
    r_design_team = int(ConfigCatClient.MKT_ID_CC.get_value("r_designteam", 864161064526020628))
    r_content_creator_manager = int(ConfigCatClient.MKT_ID_CC.get_value("r_contentcreatormanager", 864165192148189224))


class TutID:
    """
    IDs of the SS Tutoring Division server.
    NOTE: If you want to add IDs, please use the format as below.

    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    # *** Guilds ***
    g_tut = int(ConfigCatClient.TUT_ID_CC.get_value("g_tut", 860897711334621194))

    # *** Channels ***
    ch_bot_commands = int(ConfigCatClient.TUT_ID_CC.get_value("ch_botcommands", 862480236965003275))
    ch_hour_logs = int(ConfigCatClient.TUT_ID_CC.get_value("ch_hourlogs", 953454389652226068))
    ch_announcements = int(ConfigCatClient.TUT_ID_CC.get_value("ch_announcements", 861711851330994247))
    ch_leadership_announcements = int(ConfigCatClient.TUT_ID_CC.get_value("ch_leadershipannouncements",
                                                                          861712109757530112))
    ch_math_announcements = int(ConfigCatClient.TUT_ID_CC.get_value("ch_mathannouncements", 860929479961739274))
    ch_science_announcements = int(ConfigCatClient.TUT_ID_CC.get_value("ch_scienceannouncements", 860929498782629948))
    ch_english_announcements = int(ConfigCatClient.TUT_ID_CC.get_value("ch_englishannouncements", 860929517102039050))
    ch_SS_announcements = int(ConfigCatClient.TUT_ID_CC.get_value("ch_ssannouncements", 860929548639797258))
    ch_cs_announcements = int(ConfigCatClient.TUT_ID_CC.get_value("ch_csannouncements", 860929585355948042))
    ch_misc_announcements = int(ConfigCatClient.TUT_ID_CC.get_value("ch_miscannouncements", 860929567132221481))


class HRID:
    """
    IDs of the SS HR Department server.
    NOTE: If you want to add IDs, please use the format as below.

    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    # *** Guilds ***
    g_hr = int(ConfigCatClient.HR_ID_CC.get_value("g_hr", 815753072742891532))

    # *** Channels ***
    ch_announcements = int(ConfigCatClient.HR_ID_CC.get_value("ch_announcements", 816507730557796362))
    ch_mkt_announcements = int(ConfigCatClient.HR_ID_CC.get_value("ch_mktannouncements", 816733579660754944))
    ch_acad_announcements = int(ConfigCatClient.HR_ID_CC.get_value("ch_acadannouncements", 816733725244522557))
    ch_tech_announcements = int(ConfigCatClient.HR_ID_CC.get_value("ch_techannouncements", 816733303629414421))
    ch_leadership_announcements = int(ConfigCatClient.HR_ID_CC.get_value("ch_leadershipannouncements",
                                                                         819009569979629569))
    ch_email_requests = int(ConfigCatClient.HR_ID_CC.get_value("ch_emailrequests", 968345000100384788))

    # *** Roles ***
    r_hr_staff = int(ConfigCatClient.HR_ID_CC.get_value("r_hrstaff", 861856418117845033))


class PSID:
    """
    IDs of the Programming Simplified server.
    NOTE: If you want to add IDs, please use the format as below.

    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    # *** Guilds ***
    g_ps = int(ConfigCatClient.PS_ID_CC.get_value("g_ps", 952287046750310440))

    # *** Roles ***
    r_ps_tut = int(ConfigCatClient.PS_ID_CC.get_value("r_pstut", 952287047056511076))


class LeaderID:
    """
    IDs of the Leadership Lounge server.
    NOTE: If you want to add IDs, please use the format as below.

    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    # *** Guilds ***
    g_leader = int(ConfigCatClient.LEADER_ID_CC.get_value("g_leader", 888929996033368154))
    g_staff_resources = int(ConfigCatClient.LEADER_ID_CC.get_value("g_staffresources", 955911166520082452))

    # *** Channels ***
    ch_staff_announcements = int(ConfigCatClient.LEADER_ID_CC.get_value("ch_staffannouncements", 936134263777148949))
    ch_env_announcements = int(ConfigCatClient.LEADER_ID_CC.get_value("ch_envannouncements", 942572395640782909))
    ch_rebrand_announcements = int(ConfigCatClient.LEADER_ID_CC.get_value("ch_rebrandannouncements",
                                                                          946180039630782474))
    ch_workonly_announcements = int(ConfigCatClient.LEADER_ID_CC.get_value("ch_workonlyannouncements",
                                                                           890993285940789299))
    ch_finance_announcements = int(ConfigCatClient.LEADER_ID_CC.get_value("ch_financeannouncements",
                                                                          919341240280023060))
    ch_mkt_announcements = int(ConfigCatClient.LEADER_ID_CC.get_value("ch_mktannouncements", 942792208841588837))
    ch_ssd_announcements = int(ConfigCatClient.LEADER_ID_CC.get_value("ch_ssdannouncements", 947656507162525698))
    ch_main_announcements = int(ConfigCatClient.LEADER_ID_CC.get_value("ch_mainannouncements", 936464173687259226))
    ch_announcements = int(ConfigCatClient.HR_ID_CC.get_value("ch_announcements", 816507730557796362))
    ch_acad_announcements = int(ConfigCatClient.HR_ID_CC.get_value("ch_acadannouncements", 816733725244522557))
    ch_tech_announcements = int(ConfigCatClient.HR_ID_CC.get_value("ch_techannouncements", 816733303629414421))
    ch_leadership_announcements = int(ConfigCatClient.HR_ID_CC.get_value("ch_leadershipannouncements",
                                                                         819009569979629569))
    ch_com_log = int(ConfigCatClient.LEADER_ID_CC.get_value("ch_com_log", 955991586364334082))

    # *** Roles ***
    r_corporate_officer = int(ConfigCatClient.LEADER_ID_CC.get_value("r_corporateofficer", 900940957783056444))
    r_president = int(ConfigCatClient.LEADER_ID_CC.get_value("r_president", 900940957783056444))
    r_vice_president = int(ConfigCatClient.LEADER_ID_CC.get_value("r_vicepresident", 888929996175978508))
    r_board_member = int(ConfigCatClient.LEADER_ID_CC.get_value("r_boardmember", 888929996188549189))
    r_director = int(ConfigCatClient.LEADER_ID_CC.get_value("r_director", 892531463482900480))
    r_SS_digital_committee = int(ConfigCatClient.LEADER_ID_CC.get_value("r_ssdigitalcommittee", 912472488594771968))
    r_information_technology_manager = int(ConfigCatClient.LEADER_ID_CC.get_value("r_informationtechnologymanager",
                                                                                  943942441357172758))

    # *** Roles **
    r_hr_staff = int(ConfigCatClient.HR_ID_CC.get_value("r_hrstaff", 861856418117845033))


class SETID:
    """
    IDs of the SSD SET SERVER

    NOTE: If you want to add IDs, please use the format as below.
    Format:
        g: discord.Guild
        ch: discord.TextChannel, discord.VoiceChannel, discord.StageChannel
        cat: discord.CategoryChannel
        r: discord.Role
        msg: discord.Message
    """

    # *** Guilds ***
    g_set = int(ConfigCatClient.SET_ID_CC.get_value("g_set", 950799439625355294))

    # *** Channels ***
    ch_suggestions = int(
        ConfigCatClient.SET_ID_CC.get_value("ch_suggestions", 954190487026274344)
    )
    ch_puzzle = int(
        ConfigCatClient.SET_ID_CC.get_value("ch_puzzle", 952402735167320084)
    )
    ch_college_acceptance = int(
        ConfigCatClient.SET_ID_CC.get_value("ch_college_acceptance", 955960683785236540)
    )
    ch_may_day_guess = int(
        ConfigCatClient.SET_ID_CC.get_value("ch_puzzle_guessv2", 966857151417028608)
    )
    ch_general = int(
        950799440766177297  #  will replace later
    )
    ch_reminders = int(
        971215505828511744
    )

    # *** Roles ***
    r_hrStaff = int(ConfigCatClient.HR_ID_CC.get_value("r_hrstaff", 861856418117845033))




class CheckDB_CC:
    """
    Checks and Safeguards for the Bot.
    """

    MasterMaintenance = int(ConfigCatClient.CHECK_DB_CC.get_value("mastermaintenance", False))
    guild_None = int(ConfigCatClient.CHECK_DB_CC.get_value("guildnone", False))
    external_guild = int(ConfigCatClient.CHECK_DB_CC.get_value("externalguild", True))
    mod_role_bypass = int(ConfigCatClient.CHECK_DB_CC.get_value("modrolebypass", True))
    rule_bypass = int(ConfigCatClient.CHECK_DB_CC.get_value("rulebypass", True))
    public_categories = int(ConfigCatClient.CHECK_DB_CC.get_value("publiccategories", False))
    else_situation = int(ConfigCatClient.CHECK_DB_CC.get_value("elsesituation", True))
    persistent_change = int(ConfigCatClient.CHECK_DB_CC.get_value("persistantchange", True))


def config_patch(key, value):
    """
    Makes a PATCH request to ConfigCat to change a Sandbox Configuration.
    **NOTE:** This only supports changing the Sandbox category, anything else will not work.

    Args:
        key (str): Key to modify.
        value (str): Value to apply.

    Returns:
        requests.Response: requests.Response object representing the HTTP request.
    """
    url = f"https://api.configcat.com/v1/settings/{key}/value?settingKeyOrId={key}"
    user = os.getenv("CONFIG_CC_USER")
    password = os.getenv("CONFIG_CC_PASSWORD")
    json_payload = [{"op": "replace", "path": "/value", "value": str(value)}]

    r = requests.patch(
        url,
        auth=(user, password),
        headers={"X-CONFIGCAT-SDKKEY": os.getenv("SANDBOX_CONFIG_CC")},
        json=json_payload,
    )
    print(r.status_code)
    return r


class Emoji:
    """
    Emojis to use for the bot.
    """

    space = "<:space:834967357632806932>"
    confirm = "<:confirm:860926261966667806>"
    deny = "<:deny:860926229335375892>"
    question = "<:question:861794223027519518>"
    warn = "<:warn:860926255443345409>"
    lock = "<:lock:860926195087835137>"
    unlock = "<:unlock:860926246937427989>"
    time = "<:time:860926238737825793>"
    red_issue = "<:issue:860587949263290368>"
    archive = "<:file:861794167578689547>"
    cycle = "<:cycle:861794132585611324>"
    calender = "<:calendar:861794038739238943>"
    add_gear = "<:add5x:862875088311025675>"
    minus_gear = "<:minusgear:862875088217702421>"
    invalid_channel = "<:invalidchannel:862875088361619477>"
    barrow = "<:SS:865715703545069568>"
    person = "<:person:883771751127990333>"
    activity = "<:note:883771751190908989>"
    check = "<:success:834967474101420032>"
    cancel = "<:cancel:834967460075012106>"
    arrow = "<:rightDoubleArrow:834967375735422996>"
    mute = "<:mute:834967579264155658>"
    ban = "<:ban:834967435642929162>"
    reason = "<:activity:834968852558249999>"
    profile = "<:profile:835213199070593035>"
    creation = "<:creation:835213216299745291>"
    date = "<:thewickthing:835213229294223400>"
    discordLogo = "<:discord:812757175465934899>"
    discordLoad = "<a:Discord:866408537503694869>"
    pythonLogo = "<:python:945410067887435846>"
    javascriptLogo = "<:javascript:945410211752054816>"
    blob_amused = "<:blobamused:895125015719194655>"
    mod_shield = "<:modshield:957316876168474644>"
    loadingGIF = "<a:Loading:904192577094426626>"
    loadingGIF2 = "<a:Loading:905563298089541673>"
    gsuite_logo = "<:gsuitelogo:932034284724834384>"
    turtle_smirk = "<:TurtleSmirk:879119619737124914>"

    # SS Emojis
    schoolsimplified = "<:SchoolSimplified:830689765329993807>"
    ss_arrow = "<:SS:865715703545069568>"
    human_resources = "<:SS_HumanResources:907766589972181043>"
    timmyBook = "<:timmy_book:933043045493010453>"
    timmyTutoring = "<:tutoring:933043045950164992>"


class Colors:
    """
    Colors for the bot. Can be custom hex colors or built-in colors.
    """

    # *** Standard Colors ***
    blurple = discord.Color.blurple()
    green = discord.Color.brand_green()
    yellow = discord.Color.yellow()
    fuchsia = discord.Color.fuchsia()
    red = discord.Color.brand_red()

    # *** Hex Colors ***
    orange = 0xFCBA03
    dark_gray = 0x2F3136
    light_purple = 0xD6B4E8
    mod_blurple = 0x4DBEFF
    ss_blurple = 0x7080FA


class Others:
    """
    Other things to use for the bot. (Images, characters, etc.)
    """

    ss_logo_png = "https://media.discordapp.net/attachments/864060582294585354/878682781352362054/ss_current.png"
    error_png = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png"
    nitro_png = "https://i.imgur.com/w9aiD6F.png"

    # *** Timmy Images ***
    timmy_dog_png = "https://cdn.discordapp.com/attachments/875233489727922177/876610305852051456/unknown.png"
    timmy_laptop_png = "https://i.gyazo.com/5cffb6cd45e5e1ee9b1d015bccbdf9e6.png"
    timmy_happy_png = "https://i.gyazo.com/a0b221679db0f980504e64535885a5fd.png"
    timmy_book_png = "https://media.discordapp.net/attachments/875233489727922177/876603875329732618/timmy_book.png?width=411&height=533"
    timmy_teacher_png = "https://media.discordapp.net/attachments/875233489727922177/877378910214586368/tutoring.png?width=411&height=532"
    timmy_donation_png = "timmydonation.png"
    timmy_donation_path = "./utils/bots/CoreBot/LogFiles/timmydonation.png"

    space_character = "　"
    ticket_inactive_time = 1440
    CHID_default = 905217698865225728


# Game IDs (constants)
GameDict = {
    "Awkword": 879863881349087252,
    "Betrayal": 773336526917861400,
    "CG4": 832025144389533716,
    "Chess in the Park": 832012774040141894,
    "Doodle Crew": 878067389634314250,
    "Letter Tile": 879863686565621790,
    "Fishington": 814288819477020702,
    "Poker Night": 755827207812677713,
    "Putts": 832012854282158180,
    "Sketchy Artist": 879864070101172255,
    "Spell Cast": 852509694341283871,
    "Youtube Together": 755600276941176913,
    "Word Snacks": 879863976006127627,
}

CHHelperRoles = {
    "Essay": 951302786337890334,
    "Essay Reviser": 951302786337890334,
    "English": 951302796026724408,
    "English Language": 951302795456294992,
    "English Literature": 951302800342679623,
    "Math": 951302805233205328,
    "Algebra": 951302805698805780,
    "Geometry": 951302804599885884,
    "Precalculus": 951302803224166470,
    "Calculus": 951302802544685117,
    "Statistics": 951302800896307281,
    "Science": 951302798321004585,
    "Biology": 951302801907130379,
    "Chemistry": 951302796756537355,
    "Physics": 951302803538714715,
    "Psych": 951302799612842046,
    "Social Studies": 951302792100864020,
    "World History": 951302791605911572,
    "US History": 951302790548955216,
    "US Gov": 951302800225235004,
    "Euro": 951302791027118110,
    "Human Geo": 951302806428590111,
    "Economy": 951302788762198067,
    "Languages": 951302794881675294,
    "French": 951302794420293702,
    "Chinese": 951302788510531584,
    "Korean": 951302787998826537,
    "Spanish": 951302786765705266,
    "Computer Science": 951302797813489714,
    "Fine Arts": 951302798857895936,
    "Research": 951302790066602034,
    "SAT/ACT": 951302789613625345,
}

rulesDict = {
    1: f"All Terms of Service and Community Guidelines apply. && {Emoji.barrow} https://discord.com/terms\n{Emoji.barrow} https://discord.com/guidelines",
    2: f"Keep chats and conversations mainly in English. && {Emoji.barrow} Full-blown conversations in a different language that disrupt the environment are not allowed.\n{Emoji.barrow} Disrupting an existing conversation in English in voice chat is not allowed.",
    3: f"Keep chats and conversations relevant. && {Emoji.barrow} Keep discussions about politics or anything else in <#773366189648642069>.\n{Emoji.barrow} Ask homework questions in the homework channels or tickets.",
    4: f"No content that does not belong in a school server. && {Emoji.barrow} No inappropriate user profiles, avatars, banners, statuses, about me, usernames, or nicknames.\n{Emoji.barrow} No sharing of content that glorifies or promotes suicide or self-harm.\n{Emoji.barrow} No trolling, raiding, epileptic, disturbing, suggestive, or offensive behavior.\n{Emoji.barrow} No sexist, racist, homophobic, transphobic, xenophobic, islamophobic, pedophilic, creepy behavior, etc.",
    5: f"No advertising or self-promotion (unless given explicit permission). && {Emoji.barrow} Self-advertising a website, group, or anything else through DMs, VC or in the server is not allowed.\n{Emoji.barrow} Explicitly asking users to look at advertisements in status/About Me is not allowed.",
    6: f"No toxic behavior or harassment. && {Emoji.barrow} No discriminatory jokes or language towards an individual or group due to race, ethnicity, nationality, sex, gender, sexual orientation, religious affiliation, or disabilities.\n{Emoji.barrow} Disrespect of members is not allowed, especially if it is continuous, repetitive, or severe.\n{Emoji.barrow} Encouraging toxicity, harassment, bullying, and anything of the sort is prohibited.",
    7: f"No illegal or explicit material. && {Emoji.barrow} Discussing or sharing illegal content is prohibited. This includes, but is not limited to: copyrighted content, pirated content, illegal activities, crimes, IPGrabbers, phishing links.\n{Emoji.barrow} Any form of NSFW, NSFL, or explicit content (pornographic, overtly sexual, overly gory) is prohibited.",
    8: f"No DDoS, dox, death or any other sort of threats. && {Emoji.barrow} Indirect or direct threats to harm someone else are strictly prohibited and causes for immediate ban.\n{Emoji.barrow} DDoS (Distributed Denial of Service): sending a large amount of requests in a short amount of time.\n{Emoji.barrow} Dox: revealing any private information of another member, such as real name or address, without consent.",
    9: f"No slurs and excessive or harmful profanity usage. && {Emoji.barrow} Using or attempting to use slurs and racist terms is prohibited.\n{Emoji.barrow} Excessive profanity, verbal abuse and insults are prohibited.",
    10: f"No cheating in any form. && {Emoji.barrow} It is strictly prohibited to cheat or engage in academic dishonesty anywhere in the server.",
    11: f"No spamming in any form. && {Emoji.barrow} Spamming links, images, messages, roles, emojis, emotes, emote reactions, or anything else is not allowed.",
    12: f"No impersonation in any form. && {Emoji.barrow} Changing your username or avatar to something similar as any staff or members with the intent to mimic them and create confusion is prohibited. ",
    13: f"No disruptive behavior in voice chat. && {Emoji.barrow} No continuous hopping between voice chats.\n{Emoji.barrow} No starting and closing streams in short intervals.\n{Emoji.barrow} No loud, annoying, or high-pitched noises.\n{Emoji.barrow} No voice changers if asked to stop.",
    14: f"No evading user blocks, punishments, or bans by using alternate accounts. && {Emoji.barrow} Sending unwanted, repeated friend requests or messages to contact someone who has blocked you is prohibited.\n{Emoji.barrow} Creating alternate accounts to evade a punishment or ban, harass or impersonate someone, or participate in a raid are all strictly prohibited.\n{Emoji.barrow} Suspicions of being an alternate account are cause for a ban with no prior warning.\n{Emoji.barrow} To discuss punishments or warnings, create a support ticket or talk to a moderator in DMs.",
}

deprecatedFiles = [
    "TTScreds.json",
    "tokenA.json",
    "staff_verifyClient.json",
    "gmailAPI_credentials.json",
    "gmail_token.json",
    "docs_token.json",
    "docs_credentials.json",
    "credentialsA.json",
    "admincred.json",
]

class EmbeddedActivity:
    awkword = 879863881349087252
    betrayal = 773336526917861400
    cg2_qa = 832012815819604009
    cg2_staging = 832012730599735326
    cg3_dev = 832012682520428625
    cg3_prod = 832013003968348200
    cg3_qa = 832012894068801636
    cg3_staging = 832012938398400562
    cg4_dev = 832013108234289153
    cg4_prod = 832025144389533716
    cg4_qa = 832025114077298718
    cg4_staging = 832025061657280566
    chess_in_the_park_dev = 832012586023256104
    chess_in_the_park = 832012774040141894
    decoders_dev = 891001866073296967
    doodle_crew = 878067389634314250
    doodle_crew_dev = 878067427668275241
    fishington = 814288819477020702
    letter_tile = 879863686565621790
    pn_staging = 763116274876022855
    poker_night = 755827207812677713
    poker_qa = 801133024841957428
    putts = 832012854282158180
    sketchy_artist = 879864070101172255
    sketchy_artist_dev = 879864104980979792
    spell_cast = 852509694341283871
    watch_together = 880218394199220334
    watch_together_dev = 880218832743055411
    word_snacks = 879863976006127627
    word_snacks_dev = 879864010126786570
    youtube_together = 755600276941176913


SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.orgunit",
    "https://www.googleapis.com/auth/admin.directory.userschema",
]
orgUnit = {
    "Personal Account": "/School Simplified Personal Acc.",
    "Team Account": "/School Simplified Team Acc.",
}

creds = access_secret("adm_t", True, 0, SCOPES)
service = build("admin", "directory_v1", credentials=creds)


def get_random_string(length=13):
    # choose from all lowercase letter
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"

    rnd = random.SystemRandom()
    return "".join(rnd.choice(chars) for i in range(length))

EmailSelectOptions = [
    discord.SelectOption(
        label="Individual Email",
        description="Request an individual email address.",
        emoji="👤",
    ),
    discord.SelectOption(
        label="Team Email",
        description="Request a team email address.",
        emoji="👥",
    )
]


def create_ui_modal_class(conf_id):
    query = database.TicketConfiguration.select().where(database.TicketConfiguration.id == conf_id)
    if query.exists():
        query: database.TicketConfiguration = query.get()
    else:
        return None

    class UIModal(ui.Modal, title=query.title):
        def __init__(self, bot: commands.Bot, title: str, questions_l: str, conf_id: int):
            super().__init__(timeout=None)
            self.bot = bot
            self.title = title
            self.questions = str(questions_l).strip('][').split(', ')
            self.conf_id = conf_id

            self.question_obj: List[ui.TextInput] = []
            self.answers = []
            self.index_to_config_dict = {
                1: query.q1_config,
                2: query.q2_config,
                3: query.q3_config,
                4: query.q4_config,
                5: query.q5_config,
            }
            self.config_to_TextStyle_dict = {
                "S": discord.TextStyle.short,
                "L": discord.TextStyle.long,
            }
            self.create_ui_elements()

        def create_ui_elements(self):
            cache_list = []
            for elem in self.questions:
                cache_list.append(elem.strip("'"))
            self.questions = cache_list
            index = 1

            for question_e in self.questions:
                # get q1.config and update config to match ui.TextInput arguments
                config = self.index_to_config_dict[index]
                print("yo")
                if config is None or config == "":
                    style = discord.TextStyle.long
                    min_length = None
                    max_length = None
                    print("am not here")
                else:
                    print("am here")
                    style, min_length, max_length = config.split(",")
                    style = self.config_to_TextStyle_dict[style]
                    print(style, min_length, max_length)

                text_input = ui.TextInput(
                    label=question_e,
                    required=True,
                    style=style,
                    min_length=min_length,
                    max_length=max_length,
                )
                self.add_item(
                    text_input
                )
                self.question_obj.append(text_input)
                index += 1

        async def on_submit(self, interaction: discord.Interaction):
            for question in self.question_obj:
                self.answers.append(question.value)

            query = database.TicketConfiguration.select().where(database.TicketConfiguration.id == self.conf_id)

            if not query.exists():
                return await interaction.response.send_message("Ticket configuration no longer exists!")
            else:
                query: database.TicketConfiguration = query.get()

            if query.limit != 0:
                lim_query = database.MGMTickets.select().where(
                    (database.MGMTickets.configuration_id == self.conf_id)
                    & (database.MGMTickets.authorID == interaction.user.id)
                )

                if lim_query.count() >= query.limit:
                    return await interaction.response.send_message("You have hit the ticket limit for this "
                                                                   "category, please close already open "
                                                                   "tickets before opening a new one!")

            ticket_server = self.bot.get_guild(query.guild_id)
            ticket_category = discord.utils.get(ticket_server.categories, id=query.category_id)
            member = interaction.guild.get_member(interaction.user.id)

            ticket_channel = await ticket_category.create_text_channel(
                f"{interaction.user.name}-{query.channel_identifier}",
                topic=f"{interaction.user.name} | {interaction.user.id}\n{query.title}",
                reason=f"Requested by {interaction.user.name} break",
            )
            cache_query = database.MGMTickets.create(
                ChannelID=ticket_channel.id,
                authorID=interaction.user.id,
                createdAt=datetime.now(),
                configuration_id=self.conf_id,
            )
            cache_query.save()

            # make query.role_id into a list (comma seperated string) and add each role to the ticket channel
            role_list = [int(e) if e.strip().isdigit() else e for e in query.role_id.split(',')]
            for role in role_list:
                role = discord.utils.get(ticket_server.roles, id=int(role))
                try:
                    await ticket_channel.set_permissions(role, read_messages=True, send_messages=True)
                except discord.NotFound:
                    pass

            await ticket_channel.set_permissions(
                member,
                read_messages=True,
                send_messages=True,
            )
            control_embed = discord.Embed(
                title="Control Panel",
                description="To end this ticket, click the lock button!",
                color=discord.Colour.gold(),
            )
            LCB = discord.ui.View()
            LCB.add_item(
                ButtonHandler(
                    style=discord.ButtonStyle.green,
                    url=None,
                    disabled=False,
                    label="Lock",
                    emoji="🔒",
                    custom_id=f"mgm_ch_lock_menu:{query.id}",
                )
            )
            LCM = await ticket_channel.send(
                interaction.user.mention, embed=control_embed, view=LCB
            )
            await LCM.pin()
            # make an embed that has the questions and answers
            embed = discord.Embed(
                title="Ticket Created",
                description=f"{interaction.user.mention} has created a ticket in {ticket_channel.mention}",
                color=discord.Colour.gold(),
            )
            for question_final_embed, answer in zip(self.questions, self.answers):
                embed.add_field(name=question_final_embed, value=answer, inline=False)
            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.avatar.url,
            )
            embed.set_footer(
                text=f"ID: {interaction.user.id}"
            )
            await ticket_channel.send(embed=embed)

            await interaction.response.send_message(
                content=f"{interaction.user.mention}, I've created a ticket for you!\n> {ticket_channel.mention}",
                ephemeral=True,
            )
    return UIModal


def create_ticket_button(conf_id):
    query = database.TicketConfiguration.select().where(database.TicketConfiguration.id == conf_id)
    if query.exists():
        query: database.TicketConfiguration = query.get()
    else:
        return None

    class GlobalSubmitButton(discord.ui.View):
        def __init__(self, modal_view) -> None:
            super().__init__(timeout=None)
            self.modal_view = modal_view
            self.value = None

        @discord.ui.button(label=query.button_label, style=discord.ButtonStyle.blurple, disabled=False, custom_id=f"cts_pers:{query.id}")
        async def starts_commission(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.modal_view is not None:
                await interaction.response.send_modal(self.modal_view)
            else:
                await interaction.response.send_message("No modal found!")

    return GlobalSubmitButton


class HREmailDisabled(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green, disabled=True)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red, disabled=True)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass


class HREmailConfirm(discord.ui.View):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(label='Confirm', emoji="✅", style=discord.ButtonStyle.green, custom_id="temp_mgm_confirm")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        embed.title = f"[CREATED] {embed.title}"
        embed.colour = discord.Colour.green()
        temppass = get_random_string()
        if embed.fields[0].value == "G":
            return await interaction.response.send_message("Error, not supported yet.\nYou'll need to contact a Super/User "
                                                   "Administrator to create this manually.", ephemeral=True)
        elif embed.fields[0].value == "T":
            firstname = embed.fields[4].value
            lastname = "Team"
            user = {
                "name": {
                    "givenName": firstname,
                    "fullName": firstname + " Team",
                    "familyName": "Team",
                },
                "password": temppass,
                "primaryEmail": embed.fields[2].value,
                "changePasswordAtNextLogin": True,
                "orgUnitPath": "/School Simplified Team Acc.",
                "organizations": [
                    {
                        "title": "Team Email",
                        "primary": True,
                        "department": embed.fields[4].value,
                        "description": "Team",
                    }
                ]
            }
        elif embed.fields[0].value == "Personal":
            firstname = embed.fields[1].value
            lastname = embed.fields[2].value
            user = {
                "name": {
                    "givenName": embed.fields[1].value,
                    "fullName": embed.fields[1].value + " " + embed.fields[2].value,
                    "familyName": embed.fields[2].value,
                },
                "password": temppass,
                "primaryEmail": f"{embed.fields[1].value}.{embed.fields[2].value}@schoolsimplified.org",
                "changePasswordAtNextLogin": True,
                "orgUnitPath": "/School Simplified Personal Acc.",
                "relations": [
                    {
                        "value": embed.fields[3].value,
                        "type": "manager"
                    }
                ],
                "organizations": [
                    {
                        "title": embed.fields[5].value,
                        "primary": True,
                        "type": "work",
                        "department": embed.fields[4].value,
                    }
                ]

            }
        else:
            return
        try:
            service.users().insert(body=user).execute()
        except HttpError as e:
            """If the error code is 409, send a message to the user saying that the email is already taken."""
            if e.status_code == 409:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} The email {user['primaryEmail']} is already taken."
                )
            else:
                return await interaction.response.send_message(
                    f"{interaction.user.mention} An error occurred. Please try again later; forward this to a Bot "
                    f"Developer if you continue to have problems!.\nError: {e} "
                )
        else:
            if embed.fields[0].value == "Personal":
                await interaction.response.send_message(
                    f"{interaction.user.mention} Successfully created **{firstname} {lastname}'s** account.\n"
                    f"**Username:** {firstname}.{lastname}@schoolsimplified.org\n"
                    f"**Organization Unit:** {user['orgUnitPath']}",
                    ephemeral=False,
                )
            else:
                await interaction.response.send_message(
                    f"{interaction.user.mention} Successfully created **{user['name']['givenName']}'s** account.\n"
                    f"**Username:** {user['primaryEmail']}\n"
                    f"**Organization Unit:** {user['orgUnitPath']}\n",
                    "**Note:** This email has been flagged as a `TEAM` email.",
                    ephemeral=False,
                )
            await interaction.followup.send(
                f"**Temporary Password:**\n||{temppass}||\n\n**Instructions:**\nGive the Username and the Temporary "
                f"Password to the user and let them know they have **1 week** to setup 2FA before they get locked out. ",
                ephemeral=True,
            )
        self.value = True
        await interaction.message.edit(embed=embed, view=HREmailDisabled())
        self.stop()

    @discord.ui.button(label='Cancel', emoji="❌", style=discord.ButtonStyle.red, custom_id="temp_mgm_cancel")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        embed = interaction.message.embeds[0]
        embed.title = f'[RESOLVED] {embed.title}'
        embed.colour = discord.Color.brand_red()

        await interaction.message.edit(embed=embed, view=HREmailDisabled())
        self.value = False
        self.stop()


class IEmailForm(ui.Modal, title="Auto Email Form"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    first_name = ui.TextInput(
        label="First Name",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    last_name = ui.TextInput(
        label="Last Name",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    team_name = ui.TextInput(
        label="Team/Dept. Name",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    team_role = ui.TextInput(
        label="What is your position in that team?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    managers_email = ui.TextInput(
        label="Managers Email",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Thank you for your submission, forwarding your request to HR!", ephemeral=True)
        hr_email: discord.TextChannel = self.bot.get_channel(HRID.ch_email_requests)
        embed = discord.Embed(
            title=f"Email Request from {interaction.user.name}#{interaction.user.discriminator}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="Account Type", value="Personal", inline=False)
        embed.add_field(name="First Name", value=self.first_name.value)
        embed.add_field(name="Last Name", value=self.last_name.value)
        embed.add_field(name="Managers Email", value=self.managers_email.value, inline=False)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        embed.add_field(name="Team Role", value=self.team_role.value)
        await hr_email.send(embed=embed, view=HREmailConfirm(self.bot))


class TEmailForm(ui.Modal, title="Email Address Requests"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(
            discord.ui.Select(
                placeholder="Email Type",
                options=[
                    discord.SelectOption(label="Group Email", value="G"),
                    discord.SelectOption(label="Team Email", value="T"),
                ],
            )
        )

    email_purpose = ui.TextInput(
        label="Purpose of Email",
        style=discord.TextStyle.short,
        placeholder="What is this email going to be used for?",
        max_length=1024,
    )

    requested_address = ui.TextInput(
        label="Desired Email",
        style=discord.TextStyle.short,
        placeholder="Include @schoolsimplified.org",
        max_length=1024,
    )

    team_name = ui.TextInput(
        label="Team Name",
        style=discord.TextStyle.short,
        placeholder="What Team is this email for?",
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        email_type = self.children[3].values[0]
        await interaction.response.send_message("Thank you for your submission, forwarding your request to HR!", ephemeral=True)
        hr_email: discord.TextChannel = self.bot.get_channel(HRID.ch_email_requests)
        embed = discord.Embed(
            title=f"Email Request from {interaction.user.name}#{interaction.user.discriminator}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        account_type = {"G": "Group", "T": "Team"}
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="Account Type", value=account_type[email_type], inline=False)
        embed.add_field(name="Email Purpose", value=self.email_purpose.value)
        embed.add_field(name="Desired Email", value=self.requested_address.value)
        embed.add_field(name="Email Type", value=email_type)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        await hr_email.send(embed=embed, view=HREmailConfirm(self.bot))


class StaffApps(ui.Modal, title="Staff Applications"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    team_name = ui.TextInput(
        label="Team Name",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    target_app = ui.TextInput(
        label="Application that needs updating",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    approval = ui.TextInput(
        label="Who approved this?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Thank you for your submission, creating your ticket now!", ephemeral=True)
        counter_num = (
            database.BaseTickerInfo.select()
                .where(database.BaseTickerInfo.guildID == interaction.guild.id)
                .get()
        )
        num = counter_num.counter
        counter_num.counter = counter_num.counter + 1
        counter_num.save()

        category = discord.utils.get(interaction.guild.categories, id=StaffID.cat_staffapps_tickets)
        channel = await interaction.guild.create_text_channel(f"staff-apps-{num}", category=category)

        await channel.set_permissions(
            interaction.user,
            read_messages=True,
            send_messages=True,
            reason="Ticket Perms (User)",
        )
        await channel.set_permissions(
            interaction.guild.default_role,
            read_messages=False,
            send_messages=False,
            reason="Ticket Perms (Default Role)",
        )

        controlTicket = discord.Embed(
            title="Control Panel",
            description="To end this ticket, click the lock button!",
            color=discord.Colour.gold(),
        )
        LockControlButton = discord.ui.View()
        LockControlButton.add_item(
            ButtonHandler(
                style=discord.ButtonStyle.green,
                url=None,
                disabled=False,
                label="Lock",
                emoji="🔒",
                custom_id="mgm_ch_lock_menu",
            )
        )

        LCM = await channel.send(
            interaction.user.mention, embed=controlTicket, view=LockControlButton
        )
        await LCM.pin()

        tz = pytz.timezone("EST")
        opened_at = datetime.now(tz)
        query = database.MGMTickets.create(
            ChannelID=channel.id, authorID=interaction.message.author.id, createdAt=opened_at
        )
        query.save()


        embed = discord.Embed(
            title=f"Staff Application from {interaction.user.name}#{interaction.user.discriminator}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        embed.add_field(name="Application", value=self.target_app.value, inline=False)
        embed.add_field(name="Approved By", value=self.approval.value, inline=False)
        await channel.send(embed=embed)


class StaffAnnouncements(ui.Modal, title="Staff Announcements"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(
            discord.ui.Select(
                placeholder="Where will this be published?",
                options=[
                    discord.SelectOption(label="For Staff", value="Staff"),
                    discord.SelectOption(label="For the Public", value="Public"),
                ]
            )
        )

    app_title = ui.TextInput(
        label="Subject:",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    team_name = ui.TextInput(
        label="What team/dept. is this for?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    """target_publication = ui.TextInput(
        label="Where will this be published?",
        style=discord.TextStyle.long,
        max_length=1024,
    )"""

    approval = ui.TextInput(
        label="Who approved this?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Thank you for your submission, creating your ticket now!",
                                                ephemeral=True)
        counter_num = (
            database.BaseTickerInfo.select()
                .where(database.BaseTickerInfo.guildID == interaction.guild.id)
                .get()
        )
        num = counter_num.counter
        counter_num.counter = counter_num.counter + 1
        counter_num.save()

        category = discord.utils.get(interaction.guild.categories, id=StaffID.cat_announcements_tickets)
        channel = await interaction.guild.create_text_channel(f"staff-announce-{num}", category=category)

        await channel.set_permissions(
            interaction.user,
            read_messages=True,
            send_messages=True,
            reason="Ticket Perms (User)",
        )
        await channel.set_permissions(
            interaction.guild.default_role,
            read_messages=False,
            send_messages=False,
            reason="Ticket Perms (Default Role)",
        )

        controlTicket = discord.Embed(
            title="Control Panel",
            description="To end this ticket, click the lock button!",
            color=discord.Colour.gold(),
        )
        LockControlButton = discord.ui.View()
        LockControlButton.add_item(
            ButtonHandler(
                style=discord.ButtonStyle.green,
                url=None,
                disabled=False,
                label="Lock",
                emoji="🔒",
                custom_id="mgm_ch_lock_menu",
            )
        )

        LCM = await channel.send(
            interaction.user.mention, embed=controlTicket, view=LockControlButton
        )
        await LCM.pin()

        tz = pytz.timezone("EST")
        opened_at = datetime.now(tz)
        query = database.MGMTickets.create(
            ChannelID=channel.id, authorID=interaction.message.author.id, createdAt=opened_at
        )
        query.save()

        embed = discord.Embed(
            title=f"Staff Announcements from {interaction.user.name}#{interaction.user.discriminator}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.add_field(name="Subject", value=self.app_title.value, inline=False)
        embed.add_field(name="Team Name", value=self.team_name.value, inline=False)
        embed.add_field(name="Target Publication", value=self.children[3].values[0], inline=False)
        embed.add_field(name="Approved By", value=self.approval.value, inline=False)
        await channel.send(embed=embed)


class MGMCommissionButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Start Commission",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:start_commission_mgm",
        emoji="📝",
    )
    async def start_commission(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button,
    ):
        # TODO: Comply with Code Guidelines and use ConfigCat for IDs
        channel_to_modal_map = {
            956619079853179031: StaffApps(self.bot),
            956619132525244516: StaffAnnouncements(self.bot),
        }
        modal = channel_to_modal_map[interaction.channel.id]
        await interaction.response.send_modal(modal)


class EmailDropdown(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Individual Email",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:i_email_mgm",
        emoji="👤",
    )
    async def i_email(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button,
    ):
        modal = IEmailForm(self.bot)
        return await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="Team Email",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:t_email_mgm",
        emoji="👥",
    )
    async def t_email(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button,
    ):
        modal = TEmailForm(self.bot)
        return await interaction.response.send_modal(modal)


class SelectMenuHandler(ui.Select):
    """Adds a SelectMenu to a specific message and returns it's value when option selected.

    Usage:
        To do something after the callback function is invoked (the button is pressed), you have to pass a
        coroutine to the class. IMPORTANT: The coroutine has to take two arguments (discord.Interaction, discord.View)
        to work.
    """

    def __init__(
        self,
        options: List[SelectOption],
        custom_id: Union[str, None] = None,
        place_holder: Union[str, None] = None,
        max_values: int = 1,
        min_values: int = 1,
        disabled: bool = False,
        select_user: Union[discord.Member, discord.User, None] = None,
        roles: List[discord.Role] = None,
        interaction_message: Union[str, None] = None,
        ephemeral: bool = True,
        coroutine: CoroutineType = None,
        view_response=None,
        modal_response=None,
    ):
        """
        Parameters:
            options: List of discord.SelectOption
            custom_id: Custom ID of the view. Default to None.
            place_holder: Placeholder string for the view. Default to None.
            max_values Maximum values that are selectable. Default to 1.
            min_values: Minimum values that are selectable. Default to 1.
            disabled: Whenever the button is disabled or not. Default to False.
            select_user: The user that can perform this action, leave blank for everyone. Defaults to None.
            interaction_message: The response message when pressing on a selection. Default to None.
            ephemeral: Whenever the response message should only be visible for the select_user or not. Default to True.
            coroutine: A coroutine that gets invoked after the button is pressed. If None is passed, the view is stopped after the button is pressed. Default to None.
            view_response: The response of the view. Default to None.
            modal_response: The response of the modal. Default to None.
        """

        self.options_ = options
        self.custom_id_ = custom_id
        self.select_user = select_user
        self.roles = roles
        self.disabled_ = disabled
        self.placeholder_ = place_holder
        self.max_values_ = max_values
        self.min_values_ = min_values
        self.interaction_message_ = interaction_message
        self.ephemeral_ = ephemeral
        self.coroutine = coroutine
        self.view_response = view_response
        self.modal_response = modal_response

        if self.custom_id_:
            super().__init__(
                options=self.options_,
                placeholder=self.placeholder_,
                custom_id=self.custom_id_,
                disabled=self.disabled_,
                max_values=self.max_values_,
                min_values=self.min_values_,
            )
        else:
            super().__init__(
                options=self.options_,
                placeholder=self.placeholder_,
                disabled=self.disabled_,
                max_values=self.max_values_,
                min_values=self.min_values_,
            )

    async def callback(self, interaction: discord.Interaction):
        if self.select_user in [None, interaction.user] or \
                any(role in interaction.user.roles for role in self.roles):

            self.view.value = self.values[0]
            self.view_response = self.values[0]

            if self.modal_response:
                await interaction.response.send_modal(self.modal_response)

            elif self.interaction_message_:
                await interaction.response.send_message(
                    content=self.interaction_message_, ephemeral=self.ephemeral_
                )

            if self.coroutine is not None:
                await self.coroutine(interaction, self.view)
            else:
                self.view.stop()
        else:
            await interaction.response.send_message(
                content="You're not allowed to interact with that!", ephemeral=True
            )


class ButtonHandler(ui.Button):
    """
    Adds a Button to a specific message and returns it's value when pressed.

    Usage:
        To do something after the callback function is invoked (the button is pressed), you have to pass a
        coroutine to the class. IMPORTANT: The coroutine has to take two arguments (discord.Interaction, discord.View)
        to work.
    """

    def __init__(
        self,
        style: ButtonStyle,
        label: str,
        custom_id: Union[str, None] = None,
        emoji: Union[str, None] = None,
        url: Union[str, None] = None,
        disabled: bool = False,
        button_user: Union[discord.Member, discord.User, None] = None,
        roles: List[discord.Role] = None,
        interaction_message: Union[str, None] = None,
        ephemeral: bool = True,
        coroutine: CoroutineType = None,
        view_response=None
    ):
        """
        Parameters:
            style: Label for the button
            label: Custom ID that represents this button. Default to None.
            custom_id: Style for this button. Default to None.
            emoji: An emoji for this button. Default to None.
            url: A URL for this button. Default to None.
            disabled: Whenever the button should be disabled or not. Default to False.
            button_user: The user that can perform this action, leave blank for everyone. Defaults to None.
            roles: The roles which the user needs to be able to click the button.
            interaction_message: The response message when pressing on a selection. Default to None.
            ephemeral: Whenever the response message should only be visible for the select_user or not. Default to True.
            coroutine: A coroutine that gets invoked after the button is pressed. If None is passed, the view is stopped after the button is pressed. Default to None.
        """
        self.style_ = style
        self.label_ = label
        self.custom_id_ = custom_id
        self.emoji_ = emoji
        self.url_ = url
        self.disabled_ = disabled
        self.button_user = button_user
        self.roles = roles
        self.interaction_message_ = interaction_message
        self.ephemeral_ = ephemeral
        self.coroutine = coroutine
        self.view_response = view_response

        if self.custom_id_:
            super().__init__(
                style=self.style_,
                label=self.label_,
                custom_id=self.custom_id_,
                emoji=self.emoji_,
                url=self.url_,
                disabled=self.disabled_,
            )
        else:
            super().__init__(
                style=self.style_,
                label=self.label_,
                emoji=self.emoji_,
                url=self.url_,
                disabled=self.disabled_,
            )

    async def callback(self, interaction: discord.Interaction):
        if self.button_user in [None, interaction.user] or any(
            role in interaction.user.roles for role in self.roles
        ):
            if self.custom_id_ is None:
                self.view.value = self.label_
                self.view_response = self.label_
            else:
                self.view.value = self.custom_id_
                self.view_response = self.custom_id_

            if self.interaction_message_:
                await interaction.response.send_message(
                    content=self.interaction_message_, ephemeral=self.ephemeral_
                )

            if self.coroutine is not None:
                await self.coroutine(interaction, self.view)
            else:
                self.view.stop()
        else:
            await interaction.response.send_message(
                content="You're not allowed to interact with that!", ephemeral=True
            )


def get_guild_list(bot: commands.Bot, exempt_server: List[int] = None) -> list:
    guild_list = []
    for guild in bot.guilds:
        if guild.id in exempt_server:
            continue
        guild_list.append(guild.id)

    return guild_list


class TechnicalCommissionConfirm(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="persistent_view:tempconfirm",
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        transcript_log = self.bot.get_channel(TechID.ch_ticket_log)
        ch = self.bot.get_channel(interaction.channel_id)

        await raw_export(ch, transcript_log, interaction.user)
        await ch.delete()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message( "ok, not removing this channel.", ephemeral=True)
        self.value = False
        self.stop()


class LockButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.green, custom_id="persistent_view:lock", emoji="🔒")
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        ch = self.bot.get_channel(interaction.channel_id)
        temp_confirm_instance = TechnicalCommissionConfirm(self.bot)

        await ch.send("Are you sure you want to close this ticket?", view=temp_confirm_instance)


class GSuiteVerify(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(
        label="Verify with GSuite",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:gsuiteverify",
        emoji=Emoji.gsuite_logo
    )
    async def lock(self,interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True


class TempConfirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="persistent_view:tempconfirm",
    )
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button,):
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()


class NitroConfirmFake(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(
        label="Claim",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:nitrofake",
    )
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message(
                "https://images-ext-2.discordapp.net/external/YTk-6Mfxbbr8KwIc-3Pyy5Z_06tfpcO65MflxYgbjA8/"
                "%3Fcid%3D73b8f7b119cc9225923f70c7e25a1f8e8932c7ae8ef48fe7%26rid%3Dgiphy.mp4%26ct%3Dg/"
                "https/media2.giphy.com/media/Ju7l5y9osyymQ/giphy.mp4",
                ephemeral=True,
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                "https://images-ext-2.discordapp.net/external/YTk-6Mfxbbr8KwIc-3Pyy5Z_06tfpcO65MflxYgbjA8/%3Fcid%3D73"
                "b8f7b119cc9225923f70c7e25a1f8e8932c7ae8ef48fe7%26rid%3Dgiphy.mp4%26ct%3Dg"
                "/https/media2.giphy.com/media/Ju7l5y9osyymQ/giphy.mp4",
                ephemeral=True,
            )
        self.value = True


class TicketLockButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Lock",
        style=discord.ButtonStyle.green,
        custom_id="persistent_view:lock",
        emoji="🔒",
    )
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        ch = self.bot.get_channel(interaction.channel_id)
        TempConfirmInstance = TicketTempConfirm()

        await ch.send("Are you sure you want to close this ticket?", view=TempConfirmInstance)


class TicketTempConfirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="persistent_view:tempconfirm",
    )
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button,):
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()


# class LeaderboardPages(menus.ListPageSource):
#     def __init__(self, leaderboard):
#         super().__init__(entries=leaderboard, per_page=25)
#
#     async def format_page(self, menu, item):
#
#         with open('levels.json', 'r') as fcheckrew:
#             checkrew = json.load(fcheckrew)
#         if f'{menu.ctx.guild.id}' in checkrew.keys():
#             if not checkrew[f'{menu.ctx.guild.id}'] == {}:
#
#                 listkeys = []
#                 authorrank = ''
#                 for key, value in sorted(checkrew[f'{menu.ctx.guild.id}'].items(), key=lambda pair: pair[1]['total'], reverse=True):
#                     if menu.ctx.guild.get_member(int(key)):
#                         listkeys.append(key)
#
#                         if int(key) == menu.ctx.author.id:
#                             authorrank_len = int(listkeys.index(str(menu.ctx.author.id))) + 1
#
#
#                 if f'{menu.ctx.author.id}' in listkeys:
#                     authorrank = f"Your rank: #{authorrank_len}"
#
#                 else:
#                     authorrank = f"You aren't ranked yet."
#
#                 joined = '\n'.join(item)
#                 embed = discord.Embed(color=farbegeneral, title=f'Leaderboard of {menu.ctx.guild.name}', description=
#                 f'_ _'
#                 f'\n{joined}')
#                 embed.set_footer(text=f'{authorrank} | page {menu.current_page + 1}/{self.get_max_pages()}')
#                 embed.set_thumbnail(url=f'{menu.ctx.guild.icon_url}')
#
#                 return embed


async def id_generator(size=3, chars=string.ascii_uppercase):
    while True:
        ID = "".join(random.choice(chars) for _ in range(size))
        query = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.SessionID == ID)

        if query.exists():
            continue
        else:
            return ID


async def force_restart(ctx, main_or_beta):
    p = subprocess.run("git status -uno", shell=True, text=True, capture_output=True, check=True)

    embed = discord.Embed(
        title="Restarting...",
        description="Doing GIT Operation (1/3)",
        color=discord.Color.green(),
    )
    embed.add_field(name="Checking GIT (1/3)", value=f"**Git Output:**\n```shell\n{p.stdout}\n```")

    msg = await ctx.send(embed=embed)
    try:
        result = subprocess.run(
            f"cd && cd {main_or_beta}",
            shell=True,
            text=True,
            capture_output=True,
            check=True,
        )
        process = subprocess.Popen([sys.executable, "main.py"])

        run_thread = Thread(target=process.communicate)
        run_thread.start()

        embed.add_field(
            name="Started Environment and Additional Process (2/3)",
            value="Executed `source` and `nohup`.",
            inline=False,
        )
        await msg.edit(embed=embed)

    except Exception as e:
        embed = discord.Embed(title="Operation Failed", description=e, color=Colors.red)
        embed.set_footer(text="Main bot process will be terminated.")

        await ctx.send(embed=embed)

    else:
        embed.add_field(
            name="Killing Old Bot Process (3/3)",
            value="Executing `sys.exit(0)` now...",
            inline=False,
        )
        await msg.edit(embed=embed)
        sys.exit(0)


def get_host_dir():
    """
    Get the directory of the current host.

    Format: /home/<HOST>/
    -> which 'HOST' is either 'timmya` or 'timmy-beta'

    NOTE: THIS ONLY WORKS ON THE VPS.
    """

    run_path = os.path.realpath(__file__)
    run_dir = re.search("/home/[^/]*", run_path)
    if run_dir is not None:
        run_dir = run_dir.group(0)
    else:
        run_dir = None

    return run_dir


def string_time_convert(string: str):
    """
    Filters out the different time units from a string (e.g. from '2d 4h 6m 7s') and returns a ``dict``.
    NOTE: The sequence of the time units doesn't matter. Could also be '6m 2d 7s 4h'.

    Params:
        string: The string which should get converted to the time units. (e.g. '2d 4h 6m 7s')

    Returns: A ``dict`` which the keys are 'days', 'hours', 'minutes', 'seconds' and the value is either a ``int`` or ``None``.
    """

    time_dict: dict = {}

    days = re.search("\d+d", string)
    hours = re.search("\d+h", string)
    minutes = re.search("\d+m", string)
    seconds = re.search("\d+s", string)

    if days is not None:
        time_dict["days"] = int(days.group(0).strip("d"))
    else:
        time_dict["days"] = None

    if hours is not None:
        time_dict["hours"] = int(hours.group(0).strip("h"))
    else:
        time_dict["hours"] = None

    if minutes is not None:
        time_dict["minutes"] = int(minutes.group(0).strip("m"))
    else:
        time_dict["minutes"] = None

    if seconds is not None:
        time_dict["seconds"] = int(seconds.group(0).strip("s"))
    else:
        time_dict["seconds"] = None

    return time_dict


def search_custom_emoji(string: str):
    """
    Searches for a custom emoji in a specific ``str`` and returns it or None if nothing found.
    The custom emoji can either be animated or not.

    Params:
        string: The string which should get searched for a custom emoji.

    Returns: The custom emoji (``str``) or None if nothing found.
    """

    custom_emoji = re.search("<[^:]*:[^:]*:(\d)+>", string)

    if custom_emoji is not None:
        custom_emoji = custom_emoji.group(0)
    else:
        custom_emoji = None

    return custom_emoji


async def get_active_or_archived_thread(
        guild: discord.Guild,
        thread_id: int
) -> Optional[discord.Thread]:

    active_thread = guild.get_thread(thread_id)

    if active_thread is None:

        thread = None
        for text_channel in guild.text_channels:
            if thread is None:
                async for archived_thread in text_channel.archived_threads():
                    if archived_thread.id == thread_id:
                        thread = archived_thread
                        break
            else:
                break
    else:
        thread = active_thread

    return thread
