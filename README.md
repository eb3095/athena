# Athena AI Personal Assistant

## Install

### Server
Deploy a Vultr Tortoise TTS instance. Then install the Tortoise TTS fast fork over top.
https://github.com/152334H/tortoise-tts-fast

```
sudo make install_server
```

Edit `/etc/athena/config.json` with your key and server info.

Start the service with,
```
systemctl enable --now /opt/athena/athena-server.service
```

Its recommended to put this behind nginx.

### Client

This requires a few extra steps,

To start,
```
sudo make install_client
```

Go to,
https://picovoice.ai/platform/porcupine/

Sign up for a free account. Now you need 3 wake words,

* "Athena Listen"
* "Athena Request"
* "Athena Quiet"

Train and download these wake words. Unzip the ppn files to these locations,

* `/opt/athena/wake/athena-listen.ppn`
* `/opt/athena/wake/athena-request.ppn`
* `/opt/athena/wake/athena-quiet.ppn`

Now add your porcupine and server details to the config file,
`/etc/athena/config.json`

You are going to want to pick a voice, or leave it as freeman. Then you want
to generate the pre-rendered voice responses.
```
sudo python3 /opt/athena/athena_generate.py
```

If you set up the server right, this should be working. If not, check the server!

Now start the assistant!
```
systemctl enable --now /opt/athena/athena.service
```

This should be working and you should be ready to go!

### Usage

* "Athena Listen" is used to trigger commands preset in the config.
* "Athena Request" hits the server, uses OpenAI to get a response, and then TortoiseTTS to render the response
* "Athena Quiet" is to tell Athena to bail on a request or to stop talking during a long one
* "Never mind" tells Athena to stop waiting for a command
* "What are you" tells Athena to identify itself
