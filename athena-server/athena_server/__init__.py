import json
import subprocess
import shlex
import os
import base64

from jpapi import API, APIHandler, Endpoint
from .gpt import GPT

GPT_OBJ = None
API_OBJ = None
FAILURE_TEMPLATE = {
    "error": {"code": 400, "message": "Invalid input"},
    "status": "fail",
}
RESPONSE_TEMPLATE = {"data": {"response": ""}, "status": "success"}
BUSY = False


class AIAPI(API):
    def __init__(self, config):
        super().__init__(config, "/v1", AIAPIHandler)


class AIAPIHandler(APIHandler):
    def init(self):
        GetLanguage(self)
        Translate(self)
        Prompt(self)
        SpokenPrompt(self)
        Speak(self)


class GetLanguage(Endpoint):
    def __init__(self, handler):
        super().__init__(handler)
        self.path = "/lang/get_language"
        self.required_fields["POST"] = ["input"]

    def POST(self, data):
        inp = data["input"]
        if len(inp.split(" ")) > 1000:
            response = FAILURE_TEMPLATE.copy()
            response["error"]["message"] = "Invalid input length"
            return json.dumps(response), 400
        try:
            answer = GPT_OBJ.get_language(inp)
            response = RESPONSE_TEMPLATE.copy()
            response["data"]["response"] = answer
            return json.dumps(response), 200
        except Exception as e:
            return str(e), 500


class Translate(Endpoint):
    def __init__(self, handler):
        super().__init__(handler)
        self.path = "/lang/translate"
        self.required_fields["POST"] = ["input", "target"]

    def POST(self, data):
        inp = data["input"]
        target = data["target"]
        if len(inp.split(" ")) > 1000:
            response = FAILURE_TEMPLATE.copy()
            response["error"]["message"] = "Invalid input length"
            return json.dumps(response), 400
        if len(target.split(" ")) > 1:
            response = FAILURE_TEMPLATE.copy()
            response["error"]["message"] = "Invalid target language"
            return json.dumps(response), 400
        try:
            answer = GPT_OBJ.translate(target, inp)
            response = RESPONSE_TEMPLATE.copy()
            response["data"]["response"] = answer
            return json.dumps(response), 200
        except Exception as e:
            return str(e), 500


class Prompt(Endpoint):
    def __init__(self, handler):
        super().__init__(handler)
        self.path = "/text/prompt"
        self.required_fields["POST"] = ["input"]

    def POST(self, data):
        inp = data["input"]
        if len(inp.split(" ")) > 1000:
            response = FAILURE_TEMPLATE.copy()
            response["error"]["message"] = "Invalid input length"
            return json.dumps(response), 400
        try:
            answer = GPT_OBJ.question_formatted(inp)
            response = RESPONSE_TEMPLATE.copy()
            response["data"]["response"] = answer
            return json.dumps(response), 200
        except Exception as e:
            return str(e), 500


class SpokenPrompt(Endpoint):
    def __init__(self, handler):
        super().__init__(handler)
        self.path = "/voice/prompt"
        self.required_fields["POST"] = ["input", "voice"]

    def POST(self, data):
        global BUSY
        if BUSY:
            response = FAILURE_TEMPLATE.copy()
            response["error"]["message"] = "Server is busy"
            return json.dumps(response), 800
        BUSY = True
        inp = data["input"]
        if len(inp.split(" ")) > 1000:
            response = FAILURE_TEMPLATE.copy()
            response["error"]["message"] = "Invalid input length"
            return json.dumps(response), 400
        try:
            answer = GPT_OBJ.question(inp)
            response = RESPONSE_TEMPLATE.copy()
            response["data"]["response"] = answer
            result = process_voice(answer, data["voice"])
            response["data"]["voice"] = result
            BUSY = False
            return json.dumps(response), 200
        except Exception as e:
            BUSY = False
            return str(e), 500


class Speak(Endpoint):
    def __init__(self, handler):
        super().__init__(handler)
        self.path = "/voice/speak"
        self.required_fields["POST"] = ["input", "voice", "quality"]

    def POST(self, data):
        global BUSY
        if BUSY:
            response = FAILURE_TEMPLATE.copy()
            response["error"]["message"] = "Server is busy"
            return json.dumps(response), 800
        BUSY = True
        inp = data["input"]
        if len(inp.split(" ")) > 1000:
            response = FAILURE_TEMPLATE.copy()
            response["error"]["message"] = "Invalid input length"
            return json.dumps(response), 400
        try:
            response = RESPONSE_TEMPLATE.copy()
            response["data"]["response"] = inp
            result = process_voice(inp, data["voice"], quality=data["quality"])
            response["data"]["voice"] = result
            BUSY = False
            return json.dumps(response), 200
        except Exception as e:
            BUSY = False
            return str(e), 500


def process_voice(prompt, voice, quality="ultra_fast"):
    # Check if /tmp/voice.wav exists then delete
    if os.path.exists("/tmp/voice.ogg"):
        os.remove("/tmp/voice.ogg")
    if os.path.exists("/home/athena/results"):
        os.system("rm -rf /home/athena/results")

    prompt = shlex.quote(prompt)

    try:
        os.chdir("/home/athena")
        subprocess.check_output(
            [
                "tortoisetts",
                prompt,
                "-v",
                voice,
                "-V",
                "/opt/athena/voices",
                "--low_vram",
                "--half",
                "--cond_free",
                "--sampler",
                "ddim",
                "--vocoder",
                "Univnet",
                "-p",
                quality,
            ]
        )
    except subprocess.CalledProcessError as e:
        if os.path.exists("/home/athena/results"):
            os.system("rm -rf /home/athena/results")
        raise e

    # Convert to ogg
    subprocess.check_output(
        [
            "ffmpeg",
            "-i",
            f"/home/athena/results/{voice}_combined.wav",
            "/tmp/voice.ogg",
            "-y",
            "-loglevel",
            "quiet",
        ]
    )
    if os.path.exists("/home/athena/results"):
        os.system("rm -rf /home/athena/results")

    # Read wav file, convert to base64, and return
    with open("/tmp/voice.ogg", "rb") as f:
        data = f.read()
        os.remove("/tmp/voice.ogg")

        # convert to base64
        data = base64.b64encode(data)

        # return as string
        return data.decode("utf-8")


def main():
    global GPT_OBJ, API_OBJ
    with open("/etc/athena/config.json") as f:
        config = json.load(f)
    GPT_OBJ = GPT(config)
    API_OBJ = AIAPI(config)
    API_OBJ.start()


if __name__ == "__main__":
    main()
