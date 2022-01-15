# KlikAanKlikUit TPC-300 REST service

Control individual KaKu lights through the TPC-300, exposed as a REST service. This is an alternative to building your own `433.92MHz` radio on eg. an Arduino.

## Build and run Synology package

1. Setup your environment: https://help.synology.com/developer-guide/getting_started/prepare_environment.html (note that some steps need root because of unpacking special files from the root/env tar archive...);
2. Clone this repo into the `source/` directory inside the `toolkit` folder created in the previous step;
3. In the toolkit folder, run `./pkgscripts-ng/PkgCreate.py -c -v 7.0 KakuTPCServer`;
4. The resulting package should now reside in `result_spk/KakuTPCServer-1.0.0-0001`.

Then, to install:

1. From a root shell, run the UDEV workaround from below: `chmod -R a+rwx /dev/bus/usb/`.
   Hopefully this permission issue can be fixed with a proper UDEV rule soon™;
2. Install `pip` packages as shown below (TODO: automate this in the package);
3. Install the resulting package from above through the Synology package manager;
4. Logs can be read with for example `tail -fn100 /var/log/packages/KakuTPCServer.log` (follow, and print the most recent `100` lines).

### TODO
- Configuration properties during installation don't do anything, since we can't write a "startup file" (see commented-out code in `postinst`);
- Fix the UDEV rules to not need a manual (and broad) `chmod` on `/dev/bus/usb`;
- Automagically package and/or install `requirements.txt` through `pip`?

## Run from shell on Synology NAS

### Install Python packages on the target (or pre-download on host)

Easiest is `pip install -r requirements.txt` on the target machine, but if there is "network trouble" here, download and copy files from the host:

`38` here stands for Python 3.8 - necessary for CPython packages like `pydantic`. This must match `python3 --version` on the host.

```console
$ pip download -r "../requirements.txt" --python-version 38 --only-binary=:all:
```

Now copy the files to the target (if you didn't download them into an `sshfs` on the host already)

Then, install them on the target:

```console
$ sudo python3 -m pip install packages/*
Processing ./packages/anyio-3.5.0-py3-none-any.whl
Processing ./packages/asgiref-3.4.1-py3-none-any.whl
Processing ./packages/click-8.0.3-py3-none-any.whl
Processing ./packages/fastapi-0.71.0-py3-none-any.whl
Processing ./packages/h11-0.12.0-py3-none-any.whl
Processing ./packages/idna-3.3-py3-none-any.whl
Processing ./packages/pydantic-1.9.0-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
Processing ./packages/pyusb-1.2.1-py3-none-any.whl
Processing ./packages/sniffio-1.2.0-py3-none-any.whl
Processing ./packages/starlette-0.17.1-py3-none-any.whl
Processing ./packages/typing_extensions-4.0.1-py3-none-any.whl
Processing ./packages/uvicorn-0.17.0-py3-none-any.whl
Installing collected packages: idna, sniffio, anyio, asgiref, click, typing-extensions, pydantic, starlette, fastapi, h11, pyusb, uvicorn
Successfully installed anyio-3.5.0 asgiref-3.4.1 click-8.0.3 fastapi-0.71.0 h11-0.12.0 idna-3.3 pydantic-1.9.0 pyusb-1.2.1 sniffio-1.2.0 starlette-0.17.1 typing-extensions-4.0.1 uvicorn-0.17.0
```

### UDEV rules be broken

Workaround:

```console
$ chmod -R a+rwx /dev/bus/usb/
```

### Finally, start the server

```console
$ PYUSB_DEBUG=debug uvicorn tpc-server:app --port 8080 --host <IP>
```

And in the background:

```console
$ PYUSB_DEBUG=debug nohup uvicorn tpc-server:app --port 8080 --host <IP> &
```

## Configure lights in Home Assistant

```yaml
# https://community.home-assistant.io/t/basic-restful-switch-help/103208/4
rest_command:
  kaku_switch:
    url: http://<IP>:<PORT>/switch/{{ id }}/{{ state }}
    method: get

switch:
  - platform: template
    switches:
      tafel:
        friendly_name: Tafel
        icon_template: mdi:lamp
        turn_on:
          service: rest_command.kaku_switch
          data: { id: 0, state: true }
        turn_off:
          service: rest_command.kaku_switch
          data: { id: 0, state: false }
      # More lights
```

## TODO

- Make HomeAssistant `switch.rest` work without a `state_resource`, to save on defining a REST command here followed by all the `switch.template` repetition;
