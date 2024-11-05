from LoRa import LoRa
import time

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

try:
    if lora.powerUP():
        print("LoRa started successfully\n")
    else:
        print("Failed to start LoRa. Exiting ...")
        raise exception

    msg_number = 0
    
    while True:
        print(f"Sending message {msg_number} on LoRa")
        
        message = f"Hello, i'm from transmitter side, message {msg_number}."
        messageBytes = bytes(message, 'utf-8')
        msg_number += 1
        
        if lora.transmit(list(messageBytes), 2000):
            print("Message sent successfully.\n")
        else:
            print("Failed to send message.\n")
        time.sleep(7)
        
except:
    pass

finally:
    print("Finished.")
