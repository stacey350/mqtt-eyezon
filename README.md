# A Python3 daemon for proxying decoding Eyezon alarm system messages and publishing home-assistant.io compatible MQTT messages.

## Installation
I owe a setup.py, but for now do the following to get this running: 
- virtualenv virtualenv
- source virtualenv/bin/activate
- pip3 install paho-mqtt
- pip3 install Queue
- pip3 install ConfigParser

you should then be able to run `python3 main.py` to connect to your alarm panel
