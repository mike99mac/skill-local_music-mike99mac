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

### Set up automount of USB drives
OVOS does not appear to have automount of USB drives set up.  When you plug a USB drive in, a device file, usually ``/dev/sda1`` is created, but it is not mounted.  It is recommended that you **do not** use the directory ``/media``.  Rather, create a new directory under ``/mnt``.

To set up automount, perform the following steps:

- Create the udev rules file ``/etc/udev/rules.d/99-mount-usb.rules`` as follows:

```
cd /etc/udev/rules.d
vi 99-mount-usb.rules
KERNEL=="sd[a-z][0-9]", SUBSYSTEMS=="usb", ACTION=="add", RUN+="/bin/systemctl start usb-mount@%k.service"
KERNEL=="sd[a-z][0-9]", SUBSYSTEMS=="usb", ACTION=="remove", RUN+="/bin/systemctl stop usb-mount@%k.service"
```

- Create the systemd file ``/etc/systemd/system/usb-mount@.service`` with the following content

```
[Unit]
Description=Mount USB Drive on %i

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/root/usb-mount.sh add %i
ExecStop=/root/usb-mount.sh remove %i
```

- Create the script ``/root/usb-mount.sh``:

```
#!/bin/bash
ACTION=$1
DEVBASE=$2
DEVICE="/dev/${DEVBASE}"
MOUNT_POINT=$(/bin/mount | /bin/grep ${DEVICE} | /usr/bin/awk '{ print $3 }')  # See if this drive is already mounted
case "${ACTION}" in
    add)
        if [[ -n ${MOUNT_POINT} ]]; then exit 1; fi          # Already mounted, exit
        eval $(/sbin/blkid -o udev ${DEVICE})                # Get info for this drive: $ID_FS_LABEL, $ID_FS_UUID, and $ID_FS_TYPE
        OPTS="rw,relatime"                                   # Global mount options
        if [[ ${ID_FS_TYPE} == "vfat" ]]; then OPTS+=",users,gid=100,umask=000,shortname=mixed,utf8=1,flush"; fi     # File system type specific mount options
        if ! /bin/mount -o ${OPTS} ${DEVICE} /mnt/usb/; then exit 1; fi          # Error during mount process: cleanup mountpoint
        ;;
    remove)
        if [[ -n ${MOUNT_POINT} ]]; then /bin/umount -l ${DEVICE}; fi
        ;;
esac
```

- Make it executable:

```
sudo chmod 755 /root/usb-mount.sh
```

- Restart udev rules:

```
sudo udevadm control --reload-rules
```

- Plug a USB drive in. It should get mounted over ``/mnt/usb``.


```
cd /mnt
sudo mkdir usb
sudo mount /dev/sda1 /mnt/usb
```

### Add some tools
The ovos-tools repo has some useful tools.
 
- Install ovos-tools:

```
git clone https://github.com/mike99mac/ovos-tools
cd ovos-tools
sudo ./setup
```

### Install OVOS
The OVOS installer makes it easy to install OVOS, which is not a small task.
 
- Install OVOS with the OVOS installer. Follow the steps in this document:
https://community.openconversational.ai/t/howto-begin-your-open-voice-os-journey-with-the-ovos-installer/14900

- For reference, this is the command that starts the process:

```
sh -c "curl -s https://raw.githubusercontent.com/OpenVoiceOS/ovos-installer/main/installer.sh -o installer.sh && chmod +x installer.sh && sudo ./installer.sh && rm installer.sh"
```

- Clone this repo to your home directory: 

```
cd
git clone https://github.com/mike99mac/skill-local_music-mike99mac
```

- Change to the OVOS source code directory 

```
cd ~/.venvs/ovos/lib/python3.11/site-packages/skill-local_music-mike99mac
cp -a $HOME/skill-local_music-mike99mac/ .
```

- Install the branch that restores support for Mycroft CommonPlay skills:

```
pip install git+https://github.com/OpenVoiceOS/ovos-core@feat/ocp_legacy
```

- Add this to the end your mycroft.conf file:

```
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
