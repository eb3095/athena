import pvporcupine
import speech_recognition as sr
import json
import os
import pyaudio
import subprocess
import shlex
import numpy as np

CONFIG = {
    "server_key": "snip",
    "server_address": "https://athena.com",
    "server_port": 443,
    "voice": "freeman",
}
VOICE_DIR = f"/opt/athena/voice/{CONFIG['voice']}/"
RESPONSES = {
    "notification": f"{VOICE_DIR}notification.ogg",
    "helpme": f"{VOICE_DIR}helpme.ogg",
    "yes": f"{VOICE_DIR}yes.ogg",
    "no": f"{VOICE_DIR}no.ogg",
    "okay": f"{VOICE_DIR}okay.ogg",
    "error": f"{VOICE_DIR}error.ogg",
    "ack": f"{VOICE_DIR}ack.ogg",
    "task": f"{VOICE_DIR}task.ogg",
    "bad_command": f"{VOICE_DIR}bad_command.ogg",
    "identify": f"{VOICE_DIR}identify.ogg",
    "askme": f"{VOICE_DIR}askme.ogg",
    "sorry": f"{VOICE_DIR}sorry.ogg",
}
LOOP = None
PORCUPINE = None
RECOGNIZER = None


def init():
    global PORCUPINE, RECOGNIZER, CONFIG

    with open("/etc/athena/config.json") as f:
        CONFIG = json.load(f)

    PORCUPINE = pvporcupine.create(
        keyword_paths=[
            "/opt/athena/wake/athena_listen.ppn",
            "/opt/athena/wake/athena_request.ppn",
            "/opt/athena/wake/athena_quiet.ppn",
        ],
        access_key=CONFIG["porcupine_key"],
        sensitivities=[0.3, 0.3, 0.3],
    )

    # Initialize SpeechRecognition
    RECOGNIZER = sr.Recognizer()

    # Start listening loop
    listen()


def play_sound(response):
    os.system(f"paplay {RESPONSES[response]} &")


def play_sound_wait(response):
    os.system(f"paplay {RESPONSES[response]}")


def listen():
    # Initialize PyAudio object
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=PORCUPINE.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=PORCUPINE.frame_length,
    )

    # Start listening loop
    while True:
        pcm = audio_stream.read(PORCUPINE.frame_length)
        pcm_int16 = np.frombuffer(pcm, dtype=np.int16)

        # Check if the wake word was detected
        keyword_index = PORCUPINE.process(pcm_int16)
        if keyword_index == 3 and is_prompting():
            kill_prompt()
            play_sound_wait(response="sorry")
            continue
        if keyword_index >= 0 and keyword_index < 3 and not is_prompting():
            if keyword_index == 0:
                play_sound_wait(response="helpme")
            if keyword_index == 1:
                play_sound_wait(response="askme")

            # Wait for a command
            with sr.Microphone() as source:
                retries = 3
                if keyword_index == 1:
                    retries = 1
                while retries > 0:
                    audio = RECOGNIZER.listen(source, phrase_time_limit=5)
                    try:
                        # Try to recognize the command
                        result = RECOGNIZER.recognize_google(
                            audio, language="en-US", show_all=True
                        )

                        # Execute the command
                        if keyword_index == 0:
                            cmd_run = False
                            if result:
                                for command in result["alternative"]:
                                    cmd_run = execute_command(command["transcript"])
                                    if cmd_run:
                                        retries = 0
                                        break
                            if not cmd_run:
                                play_sound_wait(response="bad_command")
                            retries -= 1
                        if keyword_index == 1:
                            if result:
                                prompt = result["alternative"][0]["transcript"]
                                print(f"Received prompt: {prompt}")
                                play_sound(response="ack")
                                voice_prompt(prompt)
                                retries = 0
                                break
                            retries -= 1
                    except Exception as e:
                        print(str(e))
                        play_sound(response="error")
                        retries = 0


def execute_command(text):
    cmd = text.lower()
    print(f"Received command: {cmd}")
    if cmd == "what are you":
        play_sound(response="identify")
        return True
    for command in CONFIG["commands"]:
        if command["name"] == cmd:
            play_sound(response="ack")
            execute(command["command"])
            return True
    if "never mind" in cmd:
        play_sound(response="okay")
        return True
    return False


def execute(command, ignore_errors=False):
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output, error = proc.communicate()
    if proc.returncode > 0 and not ignore_errors:
        raise RuntimeError(
            "Failed to run command: '%s' Code: %s Error: %s"
            % (command, output.decode("utf-8"), error.decode("utf-8"))
        )
    if ignore_errors:
        return {"out": output.decode("utf-8"), "exit": proc.returncode}
    return output.decode("utf-8").strip()


def get_prompt_id():
    cmd = "ps aux | grep athena_gpt.py | grep -v grep | awk '{print $2}'"
    return execute(cmd)


def is_prompting():
    return len(get_prompt_id()) > 0


def kill_prompt():
    pid = get_prompt_id()
    if pid:
        execute(f"kill -9 {pid}")


def voice_prompt(prompt):
    cmd = shlex.quote(prompt)
    os.system(f"python3 /opt/athena/athena_gpt.py prompt {cmd} &")


def voice_speak(prompt):
    cmd = shlex.quote(prompt)
    os.system(f"python3 /opt/athena/athena_gpt.py speak {cmd} &")


init()
