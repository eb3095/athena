import os
import requests
import base64
import json

CONFIG = {
    "server_key": "snip",
    "server_address": "https://athena.com",
    "server_port": 443,
    "voice": "freeman"
}
DIALOG = {}
VOICE_DIR = f"/opt/athena/voice/{CONFIG['voice']}/"
RESPONSES = {"error": f"{VOICE_DIR}error.ogg", "busy": f"{VOICE_DIR}busy.ogg"}


def prompt(dialog):
    if os.path.exists("/tmp/athena.ogg"):
        os.remove("/tmp/athena.ogg")

    # Include key in header
    response = requests.post(
        f"{CONFIG['server_address']}/v1/voice/speak",
        json={"input": DIALOG[dialog], "voice": CONFIG["voice"], "quality": "standard"},
        headers={"Authorization": f"Bearer {CONFIG['server_key']}"},
    )

    # Check status code
    if response.status_code != 200:
        print(f"{response.text} Status code: {response.status_code}")
        return

    response = json.loads(response.json()["message"])
    string_base64_ogg = response["data"]["voice"]
    with open(f"{VOICE_DIR}{dialog}.ogg", "wb") as f:
        f.write(base64.b64decode(string_base64_ogg))

    print("Done")


def generate():
    for diag in DIALOG.keys():
        prompt(diag)


with open("/etc/athena/config.json") as f:
    CONFIG = json.load(f)
with open("/etc/athena/dialog.json") as f:
    DIALOG = json.load(f)

generate()
