from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage

from core.common import access_secret

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

# The ID of a template document.
DOCUMENT_ID = "1u_Ab5ZkKxHLlkOWAAXW8Ht_vgv9T-3PBA_Lj-KWc-G0"

# Default Bucket Name
bucket_name = "ss-transcript-archive"
storage_client = storage.Client(credentials=access_secret("tsa_c", True, 2))
speech_client = speech.SpeechClient(credentials=access_secret("tsa_c", True, 2))

# GOOG1EJ5H3XJY3JWVZDXT7S2GEIZ2E73EGDD2PNEVXKSOWOPTB7QZB6YYBCWA
# 8LVFSONX2aLQCg1CkVjWvf3k37yeiHe5bMEcIlBS


def callback(request_id, response, exception):
    if exception:
        print(exception)
    else:
        print("Permission Id: %s" % response.get("id"))


def auth():
    creds = None
    creds = Credentials.from_authorized_user_file(
        access_secret("docs_t", True, 0, SCOPES)
    )

    try:
        service = build("drive", "v3", credentials=creds)
        dc_service = build("docs", "v1", credentials=creds)
        return service, dc_service

    except Exception as e:
        print(e)


def upload_blob(source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


def delete_blob(blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print("Blob {} deleted.".format(blob_name))


def transcribe(
    drive_service,
    docs_service,
    name: str,
    audio_f,
    total_users: int,
    primary_email: str,
):
    with open(audio_f, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=total_users,
    )

    # encoding = speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=8000,
        language_code="en-US",
        diarization_config=diarization_config,
    )

    response = speech_client.recognize(config=config, audio=audio)
    result = response.results[-1]
    words_info = result.alternatives[0].words

    list_cleanup = []
    for word_info in words_info:
        list_cleanup.append(
            u"Speaker {}: {}".format(word_info.speaker_tag, word_info.word)
        )
    transcript_list = "\n".join(list_cleanup)

    tag = 1
    speaker = ""
    transcript = ""

    for word_info in words_info:  # Changed
        if word_info.speaker_tag == tag:  # Changed
            speaker = speaker + " " + word_info.word  # Changed
        else:  # Changed
            transcript += "speaker {}: {}".format(tag, speaker) + "\n"  # Changed
            tag = word_info.speaker_tag  # Changed
            speaker = "" + word_info.word  # Changed

    transcript += "speaker {}: {}".format(tag, speaker)
    print(transcript)

    """
    # END TRANSCRIBE MODULE
    # BEGIN UPDATE DOCUMENT MODULE

    body = {
        'name': name
    }
    drive_response = drive_service.files().copy(
        fileId=DOCUMENT_ID, body=body).execute()
    document_copy_id = drive_response.get('id')

    requests = [
        {
            'insertText': {
                'location': {
                    'index': 132,
                },
                'text': transcript_list,
            }
        }
    ]

    result = docs_service.documents().batchUpdate(
        documentId=document_copy_id, body={'requests': requests}).execute()

    batch = docs_service.new_batch_http_request(callback=callback)
    user_permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': primary_email
    }
    batch.add(docs_service.permissions().create(
            fileId=document_copy_id,
            body=user_permission,
            fields='id',
    ))
    batch.execute()
    """


service, dc_service = auth()
transcribe(
    service,
    dc_service,
    "Transcript Test",
    "tts-test.mp3",
    2,
    "rohit.penta@schoolsimplified.org",
)
