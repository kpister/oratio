# aws stt
import time
import boto3
import requests
import json

from constants.constants import AWS_UPLOAD_BUCKET_URL
import api.stt.util as util


def get_client():
    print("Using AWS for STT client")
    return boto3.client("transcribe")


def transcribe_storage_uri(client, uploaded_file, locale):
    # must be unique (required by aws api)
    job_name = time.ctime().replace(" ", "-").replace(":", "-")

    storage_uri = os.path.join(AWS_UPLOAD_BUCKET_URL, uploaded_file)
    # start transcription
    client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": storage_uri},
        MediaFormat="flac",
        LanguageCode=locale,
    )

    # wait for it to complete
    while True:
        status = client.get_transcription_job(TranscriptionJobName=job_name)
        if status["TranscriptionJob"]["TranscriptionJobStatus"] in [
            "COMPLETED",
            "FAILED",
        ]:
            break
        time.sleep(5)

    response = requests.get(
        status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    )

    if response.ok:
        with open("resp.json", "w") as f:
            json.dump(response.json(), f, indent=2)
        return response.json()["results"]
    else:
        print("trancription failed")
        return []


def get_word_list(response):
    results = []

    start = 0
    end = 0
    for item in response["items"]:
        word_text = item["alternatives"][0]["content"]
        if item["type"] != "punctuation":
            start = float(item["start_time"])
            end = float(item["end_time"])

        results.append(
            util.Word(word_text, start, end, is_punc=(item["type"] == "punctuation"))
        )
    return results
