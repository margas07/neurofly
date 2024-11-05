#Importem les llibreries rellevants
import RPi.GPIO as GPIO  # Llibreria essencial per a que funcionin certs mòduls
from LoRa import LoRa  # Llibreria per al mòdul de comunicació
import time  # Amb aquesta llibreria podem saber el temps que ha passat i podem esperar
from adafruit_servokit import ServoKit  # Aquesta llibreria controla els servos

# El nombre de espais per posar servo que té el nostre mòdul
nbPCAServo=16 

# L'àngle mínim i màxim de cada servo, a partir del cinquè es pot ignorar.
MIN_IMP  =[500 , 500 , 500 , 500 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MAX_IMP  =[2500, 2500, 2500, 2500, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MIN_ANG  =[95  , 30  , 130 , 90  , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MAX_ANG  =[0   , 180 , 0   , 160 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
NTR_ANG  =[60  , 110 , 90  , 120 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Creem el nostre objecte per controlar els servos
pca = ServoKit(channels=16)

# Creem el nostre objecte per al mòdul de comunicacions (LoRa)
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


# Fem tot allò que es necessita per a inicialitzar el que escau. 
def init():
    for i in range(nbPCAServo):
        pca.servo[i].set_pulse_width_range(MIN_IMP[i] , MAX_IMP[i])
        
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIO0Pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.add_event_detect(DIO0Pin, GPIO.RISING,callback = loraMsgReceived)
    
    if lora.powerUP():
        print("LoRa started successfully")
    else:
        print("Failed to start LoRa. Exiting ...")
        raise Exception("Lora initialization failed.")


# El cos principal del programa es fa a dins d'una funció "main".
def main():
    pcaScenario();
    
    print("Listening for LoRa")
    while True:
        pass


# Funció per a provar els servos individualment.
def pcaScenario():
    for i in range(0, 4):
        
        if MIN_ANG[i] < MAX_ANG[i]:
            print(f"Servo {i}, min: {MIN_ANG[i]}, max: {MAX_ANG[i]}")
            for j in range(MIN_ANG[i],MAX_ANG[i],1):
                pca.servo[i].angle = j
                time.sleep(0.01)
            for j in range(MAX_ANG[i],MIN_ANG[i],-1):
                pca.servo[i].angle = j
                time.sleep(0.01)
                
        else:
            print(f"Reverse servo {i}, max: {MAX_ANG[i]}, min: {MIN_ANG[i]}")
            for j in range(MIN_ANG[i],MAX_ANG[i],-1):
                pca.servo[i].angle = j
                time.sleep(0.01)
            for j in range(MAX_ANG[i],MIN_ANG[i],1):
                pca.servo[i].angle = j
                time.sleep(0.01)
                
        pca.servo[i].angle = NTR_ANG[i] #disable channel
        time.sleep(0.5)
        
# Diem que ha de passar al rebre quelcom del LoRa
def loraMsgReceived(channel):
    try:
        mens=bytes(lora.read()).decode("ascii",'ignore')
        print ("\n== LORA MESSAGE RECEIVED:", mens)
    except Exception as e:
        print(e)
        
    if "D" in mens:
        pca.servo[3].angle = MIN_ANG[3]
        pca.servo[2].angle = MIN_ANG[2]
    elif "U" in mens:
        pca.servo[3].angle = MAX_ANG[3]
        pca.servo[2].angle = MAX_ANG[2]
    else:
        pca.servo[3].angle = NTR_ANG[3]
        pca.servo[2].angle = NTR_ANG[2]
        
    if "R" in mens:
        pca.servo[1].angle = MIN_ANG[1]
        pca.servo[0].angle = MAX_ANG[0]
        pca.servo[1].angle = MIN_ANG[3]
        pca.servo[0].angle = MAX_ANG[2]
    elif "L" in mens:
        pca.servo[1].angle = MAX_ANG[1]
        pca.servo[0].angle = MIN_ANG[0]
        pca.servo[1].angle = MAX_ANG[3]
        pca.servo[0].angle = MIN_ANG[2]
    else:
        pca.servo[1].angle = NTR_ANG[1]
        pca.servo[0].angle = NTR_ANG[0]
        
    if "T" in mens:
        pca.servo[0].angle = MIN_ANG[0]
        pca.servo[1].angle = MIN_ANG[1]
        pca.servo[2].angle = MIN_ANG[2]
        pca.servo[3].angle = MIN_ANG[3]
        

# Inicialitzem el programa i un cop acabat, correm el codi principal (main).
if __name__ == '__main__':
    init()
    main()
