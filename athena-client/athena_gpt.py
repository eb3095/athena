import os
import requests
import base64
import sys
import json

CONFIG = {
    "server_key": "snip",
    "server_address": "https://athena.com",
    "server_port": 443,
    "voice": "freeman",
}
VOICE_DIR = f"/opt/athena/voice/{CONFIG['voice']}/"
RESPONSES = {"error": f"{VOICE_DIR}error.ogg", "busy": f"{VOICE_DIR}busy.ogg"}


def play_sound(response):
    os.system(f"paplay {RESPONSES[response]}")


def play_response():
    os.system("paplay /tmp/athena.ogg")


def prompt(prompt):
    if os.path.exists("/tmp/athena.ogg"):
        os.remove("/tmp/athena.ogg")

    endpoint = "speak"
    if sys.argv[1] == "prompt":
        endpoint = "prompt"

    # Include key in header
    response = requests.post(
        f"{CONFIG['server_address']}/v1/voice/{endpoint}",
        json={"input": prompt},
        headers={"Authorization": f"Bearer {CONFIG['server_key']}"},
    )

    # Check status code
    if response.status_code != 200:
        if response.status_code == 800:
            play_sound(response="sorry")
            return
        play_sound(response="error")
        print(f"{response.text} Status code: {response.status_code}")
        return

    response = json.loads(response.json()["message"])
    string_base64_ogg = response["data"]["voice"]
    str_response = response["data"]["response"]
    print(f"Response: {str_response}")
    with open("/tmp/athena.ogg", "wb") as f:
        f.write(base64.b64decode(string_base64_ogg))

    print("TMP Wrote, playing")
    play_response()
    os.remove("/tmp/athena.ogg")
    print("Done")


if len(sys.argv) != 3:
    print("Usage: athena_gpt.py <type> <prompt>")
    play_sound(response="error")
    exit(1)


with open("/etc/athena/config.json") as f:
    CONFIG.update(json.load(f))
prompt(sys.argv[1])
