#Importem les llibreries rellevants
import RPi.GPIO as GPIO  # Llibreria essencial per a que funcionin certs mòduls
from LoRa import LoRa  # Llibreria per al mòdul de comunicació
import time  # Amb aquesta llibreria podem saber el temps que ha passat i podem esperar
from adafruit_servokit import ServoKit  # Aquesta llibreria controla els servos
import cv2  # No existeix el paquet "cv2", s'ha d'instal·lar "opencv-python", que conté la llibreria "cv2".
import cvlib as cv
from cvlib.object_detection import draw_bbox

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
        pca.servo[i].set_pulse_width_range(MIN_IMP[i] , MAX_IMP[i])


# El cos principal del programa es fa a dins d'una funció "main".
def main():
    pcaScenario();
    
    print("Listening for LoRa")
    while True:
        pass
        

# Inicialitzem el programa i un cop acabat, correm el codi principal (main).
if __name__ == '__main__':
    init()
    while True:
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

