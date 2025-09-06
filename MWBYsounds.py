# /home/pi/season_box/season_box.py
import time, os
import RPi.GPIO as GPIO
import pygame

# ---- CONFIG ----
PULSE_MS = 500           # on/off button pulse width
SEASON_ON_MS = 300       # how long the device should stay ON at start of its season
AUDIO_DIR = os.path.dirname(__file__)
TRACKS = [
    ("spring.mp3",  "none"),
    ("summer.mp3",  "fan"),    # fan: ON briefly at start, then OFF
    ("fall.mp3",    "none"),
    ("winter.mp3",  "snow"),   # snow: ON briefly at start, then OFF
]
# GPIO (BCM)
FAN_ON, FAN_OFF   = 17, 27
SNOW_ON, SNOW_OFF = 22, 23
# ---------------

GPIO.setmode(GPIO.BCM)
for pin in (FAN_ON, FAN_OFF, SNOW_ON, SNOW_OFF):
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

def pulse(pin, ms):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(ms/1000.0)
    GPIO.output(pin, GPIO.LOW)

def season_action(kind):
    if kind == "fan":
        pulse(FAN_ON,  PULSE_MS)               # press ON
        time.sleep(SEASON_ON_MS/1000.0)        # keep it on briefly
        pulse(FAN_OFF, PULSE_MS)               # press OFF
    elif kind == "snow":
        pulse(SNOW_ON,  PULSE_MS)
        time.sleep(SEASON_ON_MS/1000.0)
        pulse(SNOW_OFF, PULSE_MS)
    # "none" -> do nothing

def play_sound(path):
    snd = pygame.mixer.Sound(path)
    snd.play()
    time.sleep(snd.get_length())

def main_loop():
    pygame.mixer.init()  # uses default ALSA/PipeWire backend
    while True:
        for filename, action in TRACKS:
            full = os.path.join(AUDIO_DIR, filename)
            # trigger devices at start of the track
            season_action(action)
            # play the track
            play_sound(full)

if __name__ == "__main__":
    try:
        main_loop()
    finally:
        GPIO.cleanup()
