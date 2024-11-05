import RPi.GPIO as GPIO
import time
from LoRa import LoRa

GPIO.setmode(GPIO.BCM)
msgCount = 0


# define LoRa module pins and configs.
resetPin = 22
DIO0Pin = 4
Frequency = 868
SF = 7
BW = 125
crc = 5
power = 17
RFO = False
crcCheck = True
syncWord = 56 #In decimal format eq to 0x38
lora = LoRa(resetPin, Frequency, SF, BW, crc, power, RFO, crcCheck, syncWord)

def loraMsgReceived(channel):
    global msgCount
    try:
        mens=bytes(lora.read()).decode("ascii",'ignore')
        print ("\n== LORA MESSAGE RECEIVED:", mens, msgCount)
        msgCount += 1 
    except Exception as e:
        print(e)

GPIO.setup(DIO0Pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.add_event_detect(DIO0Pin, GPIO.RISING,callback = loraMsgReceived)

if lora.powerUP():
    print("LoRa started successfully")
else:
    print("Failed to start LoRa. Exiting ...")

while True:
    pass