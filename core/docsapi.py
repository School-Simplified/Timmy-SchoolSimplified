from __future__ import print_function

import json
import os
import os.path

import regex
from google.auth.transport.requests import Request
from google.cloud import secretmanager
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from core.common import access_secret

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents.modify"]

# The ID of a template document.
DOCUMENT_ID = "1u_Ab5ZkKxHLlkOWAAXW8Ht_vgv9T-3PBA_Lj-KWc-G0"

# Default Bucket Name
bucket_name = "ss-transcript-archive"


def callback(request_id, response, exception):
    if exception:
        print(exception)
    else:
        print("Permission Id: %s" % response.get("id"))


def auth():
    creds = access_secret("docs_t", True, 0)
    # creds = Credentials.from_authorized_user_file(jsonFile, SCOPES)
    try:
        service = build("docs", "v1", credentials=creds)
        return service

    except Exception as e:
        print("An error occurred: %s" % e)


def upload_blob(source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


def delete_blob(blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print("Blob {} deleted.".format(blob_name))


def transcribe(drive_service, name: str, audio_f, total_users: int, primary_email: str):
    client = speech.SpeechClient()

    with open(audio_f, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=total_users,
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,
        language_code="en-US",
        diarization_config=diarization_config,
    )

    response = client.recognize(config=config, audio=audio)
    result = response.results[-1]
    words_info = result.alternatives[0].words

    list_cleanup = []
    for word_info in words_info:
        list_cleanup.append(
            u"Speaker {}: {}".format(word_info.speaker_tag, word_info.word)
        )
    transcript_list = "\n".join(list_cleanup)

    # END TRANSCRIBE MODULE
    # BEGIN UPDATE DOCUMENT MODULE

    body = {"name": name}
    drive_response = drive_service.files().copy(fileId=DOCUMENT_ID, body=body).execute()
    document_copy_id = drive_response.get("id")

    requests = [
        {
            "insertText": {
                "location": {
                    "index": 25,
                },
                "text": transcript_list,
            }
        }
    ]

    result = (
        drive_service.documents()
        .batchUpdate(documentId=document_copy_id, body={"requests": requests})
        .execute()
    )

    batch = drive_service.new_batch_http_request(callback=callback)
    user_permission = {"type": "user", "role": "writer", "emailAddress": primary_email}
    batch.add(
        drive_service.permissions().create(
            fileId=document_copy_id,
            body=user_permission,
            fields="id",
        )
    )
    batch.execute()
