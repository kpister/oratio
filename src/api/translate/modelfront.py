"""
Example curl
curl \
  --header "Content-Type: application/json" --request POST \
  --data '{ "rows": [ {"original": "This is not a test.", "translation": "Esto no es una prueba."} ] }' \
  "https://api.modelfront.com/v1/predict?sl=en&tl=es&token=$MODELFRONT_TOKEN"
"""

from src.constants.constants import MODELFRONT_TOKEN
import requests


def evaluate(
    original_text: str, original_language: str, target_text: str, target_language: str
) -> float:

    if MODELFRONT_TOKEN is None:
        print("ModelFront token is not set in this environ; please export it to the shell")
        return None

    endpoint = f"https://api.modelfront.com/v1/predict?sl={original_language}&tl={target_language}&token={MODELFRONT_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {"rows": [{"original": original_text, "translation": target_text}]}

    response = requests.post(endpoint, headers=headers, json=data).json()
    if response["status"] != "ok":
        raise Exception(f"ModelFront failed with this response: {response}")

    # TODO: This can take many texts, add a batching option
    return response["rows"][0]["risk"]
