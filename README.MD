## Setup


sudo apt update
sudo apt-get install -y python3-dev libasound2-dev portaudio19-dev python3-rpi.gpio
sudo apt install python3-venv

python3 -m venv .venv
source .venv/bin/activate

# rimuovi eventuale pacchetto pip sbagliato
python -m pip uninstall -y neopixel

python -m pip install --upgrade pip setuptools wheel
python -m pip install adafruit-blinka adafruit-circuitpython-neopixel rpi_ws281x
python -m pip install RPi.GPIO

python -m pip install -r requirements.txt

pip install -r requirements.txt