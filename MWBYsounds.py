# /home/pi/season_box/season_box.py
import time, os
import RPi.GPIO as GPIO
import pygame

# ---- CONFIG ----
PULSE_MS = 500           # on/off button pulse width
SEASON_ON_MS = 10000     # how long the device should stay ON at start of its season
TOTAL_PLAY_MS = 180000   # 3 minutes in milliseconds
AUDIO_DIR = os.path.dirname(__file__)
TRACKS = [
    ("spring.wav",  "none"),
    ("summer.wav",  "fan"),    # fan: ON briefly at start, then OFF
    ("fall.wav",    "none"),
    ("winter.wav",  "snow"),   # snow: ON briefly at start, then OFF
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

def season_action(kind, duration_ms):
    if kind == "fan":
        pulse(FAN_ON, PULSE_MS)  # turn ON
        time.sleep(duration_ms / 1000.0)
        pulse(FAN_OFF, PULSE_MS) # turn OFF
    elif kind == "snow":
        pulse(SNOW_ON, PULSE_MS)
        time.sleep(duration_ms / 1000.0)
        pulse(SNOW_OFF, PULSE_MS)
    # "none" -> do nothing

def play_sound(path, duration_ms):
    snd = pygame.mixer.Sound(path)
    start_time = time.time()
    while (time.time() - start_time) * 1000 < duration_ms:
        channel = snd.play()
        time.sleep(snd.get_length())
        channel.stop()

def main_loop():
    pygame.mixer.init(2048)  # uses default ALSA/PipeWire backend
    while True:
        for filename, action in TRACKS:
            full = os.path.join(AUDIO_DIR, filename)
            # turn on device, play sound for 3 minutes, then turn off device
            season_action(action, TOTAL_PLAY_MS) if action != "none" else None
            play_sound(full, TOTAL_PLAY_MS)

if __name__ == "__main__":
    try:
        main_loop()
    finally:
        GPIO.cleanup()
