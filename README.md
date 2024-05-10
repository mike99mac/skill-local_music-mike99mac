# <img src='https://freemusicarchive.org/legacy/fma-smaller.jpg' card_color="#FF8600" width="50" style="vertical-align:center">Local Music
## Summary
[OCP](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin) skill to play media from
local storage.

## Description
Search and play music saved to the local file system. 

## Installation
This example was installed on a Raspberry Pi 5 running Raspberry Pi OS.

```
$ head -1 /etc/os-release
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
$ uname -v
#1 SMP PREEMPT Debian 1:6.6.28-1+rpt1 (2024-04-22)
```

To install this music skill, perform the following steps:
- Plug a USB drive with music files into one of the USB ports

- Make the directory ``/mnt/usb`` 
```
cd /mnt
sudo mkdir usb
sudo mount /dev/sda1 /mnt/usb
```

- Install ovos-tools:

```
git clone https://github.com/mike99mac/ovos-tools
cd ovos-tools
sudo ./setup
```

- Install OVOS with the OVOS installer. Follow the steps in this document:
https://community.openconversational.ai/t/howto-begin-your-open-voice-os-journey-with-the-ovos-installer/14900

```
sh -c "curl -s https://raw.githubusercontent.com/OpenVoiceOS/ovos-installer/main/installer.sh -o installer.sh && chmod +x installer.sh && sudo ./installer.sh && rm installer.sh"
```

- Clone this repo to your home directory: 

```
cd
git clone https://github.com/mike99mac/skill-local_music-mike99mac
```

- Change to the OVOS source code directory 
cd ~/.venvs/ovos/lib/python3.11/site-packages/skill-local_music-mike99mac
cp -a $HOME/skill-local_music-mike99mac/ .


Install the branch that restores support for Mycroft CommonPlay skills 

```
pip install git+https://github.com/OpenVoiceOS/ovos-core@feat/ocp_legacy
```

- Add this to the end your mycroft.conf file:

vi ~/.config/mycroft/mycroft.conf
{
  "intents": {
    "legacy_cps": true,
    "pipelines": ["...", "ocp_legacy"]
  }
}
```

- Check the syntax with the ``jq`` command:

```
cat ~/.config/mycroft/mycroft.conf | jq
{
  "log_level": "INFO",
  "play_wav_cmdline": "pw-play %1",
  "play_mp3_cmdline": "pw-play %1",
  "lang": "en-us",
  "listener": {
    "remove_silence": true,
    "VAD": {
      "module": "ovos-vad-plugin-silero"
    },
    "instant_listen": true
  },
  "skills": {
    "installer": {
      "allow_pip": true,
      "allow_alphas": true
    }
  },
  "websocket": {
    "max_msg_size": 25
  },
  "PHAL": {},
  "tts": {
    "ovos-tts-plugin-server": {
      "voice": "ryan-low"
    },
    "sentence_tokenize": true
  },
  "intents": {
    "legacy_cps": true,
    "pipelines": [
      "...",
      "ocp_legacy"
    ]
  }
}
```

- Start OVOS.
## Examples
- Play local music.
- Play music.

> You may also request a specific song, album, or artist from your local music
> collection.

## Contact Support
Use the [link](https://neongecko.com/ContactUs) or [submit an issue on GitHub](https://help.github.com/en/articles/creating-an-issue)

## Credits

[NeonGeckoCom](https://github.com/NeonGeckoCom)
[NeonDaniel](https://github.com/NeonDaniel)

## Category
**Music**
Daily

## Tags
#music
#NeonAI
#NeonGecko Original
#OCP
#Common Play
