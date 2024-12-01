>**NOTE**  
>Hem afegit un programa addicional per a mostrar a la presentació. Aquest està fet més enllà del període d'entrega de la memòria, només l'hem usat per a fer la presentació i, per tant, no extraiem cap conclusió d'aquest programa en específic.

# Importem les llibreries rellevants
import RPi.GPIO as GPIO  # Llibreria essencial perquè funcionin certs mòduls
from LoRa import LoRa  # Llibreria per al mòdul de comunicació
import time  # Amb aquesta llibreria podem saber el temps que ha passat i podem esperar
from adafruit_servokit import ServoKit  # Aquesta llibreria controla els servos
import cv2  # No existeix el paquet "cv2", s'ha d'instal·lar "opencv-python", que conté la llibreria "cv2".
import cvlib as cv
from cvlib.object_detection import draw_bbox

# El nombre de espais per posar servo que té el nostre mòdul
nbPCAServo = 16

# L'àngle mínim i màxim de cada servo, a partir del cinquè es pot ignorar.
MIN_IMP = [500, 500, 500, 500, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MAX_IMP = [2500, 2500, 2500, 2500, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MIN_ANG = [95, 30, 130, 90, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MAX_ANG = [0, 180, 0, 160, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
NTR_ANG = [60, 110, 90, 120, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Creem el nostre objecte per controlar els servos
pca = ServoKit(channels=16)

# Definim la càmera de l'avió amb la qual podrem esquivar perills.
video = cv2.VideoCapture(0)


# Aquesta funció detecta si hi ha perills en el camp de visió de la camera.
def detectant_perill() -> bool:
    # Llegim la informació de la càmera i la guardem en una variable amb la qual podem treballar
    _, frame = video.read()

    # Aquesta línia és la que fa tota la feina de la IA. Més informació a la memòria.
    bbox, labels, conf = cv.detect_common_objects(frame, model="yolov3-tiny", confidence=0)
    # Si la càmera ha trobat una persona, un ocell o un avió, considerarem que estem detectant un perill.
    if "person" in labels:
        return True
    else:
        return False


# Fem tot allò que es necessita per a inicialitzar el que escau.
def init():
    for i in range(nbPCAServo):
        pca.servo[i].set_pulse_width_range(MIN_IMP[i], MAX_IMP[i])


init()

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
syncWord = 56  # In decimal format eq to 0x38
lora = LoRa(resetPin, Frequency, SF, BW, crc, power, RFO, crcCheck, syncWord)


# Fem tot allò que es necessita per a inicialitzar el que escau.
def init():
    for i in range(nbPCAServo):
        pca.servo[i].set_pulse_width_range(MIN_IMP[i], MAX_IMP[i])

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIO0Pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(DIO0Pin, GPIO.RISING, callback=loraMsgReceived)

    if lora.powerUP():
        print("LoRa started successfully")
    else:
        print("Failed to start LoRa. Exiting ...")
        raise Exception("Lora initialization failed.")


Camera_active = False


# El cos principal del programa es fa a dins d'una funció "main".
def main():
    print("Listening for LoRa")
    global Camera_active

    while True:
        pass

        if Camera_active:
            if detectant_perill():
                print("Perill!!!")
                pca.servo[0].angle = MIN_ANG[0]
                pca.servo[1].angle = MIN_ANG[1]
                pca.servo[2].angle = MIN_ANG[2]
                pca.servo[3].angle = MIN_ANG[3]
            else:
                print("Lliure")
                pca.servo[0].angle = MAX_ANG[0]
                pca.servo[1].angle = MAX_ANG[1]
                pca.servo[2].angle = MAX_ANG[2]
                pca.servo[3].angle = MAX_ANG[3]

        time.sleep(0.1)


# Diem que ha de passar en rebre quelcom del LoRa
def loraMsgReceived(channel):
    global Camera_active

    try:
        mens = bytes(lora.read()).decode("ascii", 'ignore')
        print("\n== LORA MESSAGE RECEIVED:", mens)
    except Exception as e:
        print(e)
        return

    if "M" in mens:
        Camera_active = not Camera_active

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
