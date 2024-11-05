import time  # Ens permet mantenir el temps que ha passat i esperar, si escau.
import math  # Ens permet fer certes fòrmules matemàtiques que no té per defecte python, com ara funcions trigonomètriques.
import cvlib as cv  # Aquesta llibreria i la següent s'usen per al reconeixement d'imatges
import cv2  # Per si algú vol usar aquest codi, no existeix el paquet "cv2", s'ha d'instal·lar "opencv-python", que conté la llibreria "cv2".
import smbus  # Serveix per a certes funcionalitats dels pins de la raspberry pi, es necessita per a altres llibreries.
import RPi.GPIO as GPIO  # Similar a l'anterior, tot i que té alguna funcionalitat més que sí que usarem
from LoRa import LoRa  # Llibreria per al mòdul de comunicació per ràdio LoRa, s'ha d'instal·lar el paquet "lorathon".
from adafruit_servokit import ServoKit  # Aquesta llibreria controla els servos
from gpiozero import PWMOutputDevice  # Amb aquesta llibreria funciona el motor
import urllib.request  # Necessitem aquesta llibreria per a agafar informació de l'internet, ho farem pel GPS.
import json  # JSON és un format de fitxers de text amb informació, amb aquesta llibreria es pot llegir còmodament.

# Creem el objecte pel motor, 26 és el seu pin GPIO de la raspberry.
motor = PWMOutputDevice(26, frequency=50)

# El nombre de espais per posar servo que té el nostre mòdul, només n'usem 4, però.
nbPCAServo = 16

# L'àngle mínim, neutral i màxim de cada servo, a partir del cinquè es pot ignorar.
MIN_IMP = [500, 500, 500, 500, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MAX_IMP = [2500, 2500, 2500, 2500, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MIN_ANG = [95, 30, 130, 90, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MAX_ANG = [0, 180, 0, 160, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
NTR_ANG = [60, 110, 90, 120, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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
syncWord = 56  # In decimal format eq to 0x38
lora = LoRa(resetPin, Frequency, SF, BW, crc, power, RFO, crcCheck, syncWord)


# Fem tot allò que es necessita per a inicialitzar el que escau dels servos i el LoRa.
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


mens = ""


# Diem que hammmmmmm de passar al rebre quelcom del LoRa
def loraMsgReceived(channel):
    global mens
    try:
        mens = bytes(lora.read()).decode("ascii", 'ignore')
        print("Recibed LoRa message:", mens)
    except Exception as e:
        print(e)


init()

# Adreces per al giroscopi.
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47


# Codi d'inicialització del giroscopi
def MPU_Init():
    # write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

    # Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

    # Write to Configuration register
    bus.write_byte_data(Device_Address, CONFIG, 0)

    # Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

    # Write to interrupt enable register
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)


# Llegir dades del giroscopi
def read_raw_data(addr):
    # Accelero and Gyro value are 16-bit
    try:
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr + 1)

        # concatenate higher and lower value
        value = ((high << 8) | low)

        # to get signed value from mpu6050
        if (value > 32768):
            value = value - 65536
        return value
    except OSError as er:
        print("ERROR:", er)
        value = 0


# Inicialitzacio del giroscopi
bus = smbus.SMBus(1)
Device_Address = 0x68  # MPU6050 device address
MPU_Init()

Rx = 0
Ry = 0
Rz = 0

# Llegim les dades per a treure dades residuals del giroscopi
for i in range(10):
    _ = read_raw_data(ACCEL_XOUT_H)
    _ = read_raw_data(ACCEL_YOUT_H)
    _ = read_raw_data(ACCEL_ZOUT_H)

    _ = read_raw_data(GYRO_XOUT_H)
    _ = read_raw_data(GYRO_YOUT_H)
    _ = read_raw_data(GYRO_ZOUT_H)

prev_time = time.time()


def troba_rotacio(dtime):
    global Rx
    global Ry
    global Rz

    # Llegim les dades del giroscopi i les emmagatzem.
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)

    Gx = gyro_x / 131.0
    Gy = gyro_y / 131.0

    Rx += (Gx + 0.2) * dtime * 18 + 180
    Ry += (Gy - 0.296) * dtime * 18 + 180

    Rx %= 360
    Ry %= 360

    Rx -= 180
    Ry -= 180

    return 0, Gy, Gx


# Definim la càmera de l'avió amb la qual podrem esquivar perills.
video = cv2.VideoCapture(0)


# Aquesta funció detecta si hi ha perills en el camp de visió de la camera.
def detectant_perill() -> bool:
    # Llegim la informació de la càmera i la guardem en una variable amb la qual podem treballar
    _, frame = video.read()

    # Aquesta línia crida una IA generativa anomenada "yolov3-tiny" que és capaç de detectar coses i objectes comuns
    # com ara cotxes, persones, arbres o ocells. Ens guardarem tot allò que detecti la IA en la variable "labels".
    _, labels, _ = cv.detect_common_objects(frame, model="yolov3-tiny", confidence=0)

    # Si la càmera ha trobat una persona, un ocell o un avió, considerarem que estem detectant un perill.
    if "bird" in labels or "person" in labels or "airplane" in labels:
        return True
    else:
        return False


# Retorna la posició del GPS com a 3 variables, representant latitud, longitud i altura.
def troba_posicio() -> (float, float, float):
    with urllib.request.urlopen(
            "http://192.168.43.1:8080/get?status&lat&lon&z&zwgs84&v&dir&dist&diststart&accuracy&zAccuracy&satellites") as url:
        data = json.load(url)

        lat = data["buffer"]["lat"]["buffer"][0]
        lon = data["buffer"]["lon"]["buffer"][0]
        alt = data["buffer"]["z"]["buffer"][0]

    return lat, alt, lon


# Retorna la velocitat a la qual va l'avió com a vector amb mòdul bidimensional.
def troba_velocitat(temps_transcorregut: float) -> (float, float):
    with urllib.request.urlopen(
            "http://192.168.43.1:8080/get?status&lat&lon&z&zwgs84&v&dir&dist&diststart&accuracy&zAccuracy&satellites") as url:
        data = json.load(url)

        vel = data["buffer"]["v"]["buffer"][0]
        direct = data["buffer"]["dir"]["buffer"][0]
        pendent = 0
    return vel, direct


class Avio:
    def __init__(self):
        self.guinyada: float = 0
        self.capcineig: float = 0
        self.balanceig: float = 0

        self.latitud: float = 0
        self.longitud: float = 0
        self.altura: float = 0

        self.velocitat: float = 0

    # Funcions que l'avió ha de fer constantment
    def rutina(self, temps_transcorregut: float):
        # Actualitzem la seva posició i rotació.
        self.latitud, self.longitud, self.altura = troba_posicio()

        # Les lectures del GPS acostumen a ser més precises que les del MPU, així que només necessitem el balanceig.
        _, self.capcineig, self.balanceig = troba_rotacio(temps_transcorregut)

        # El GPS ens pot aportar els altres dos angles i la velocitat.
        self.velocitat, self.guinyada, _ = troba_velocitat(temps_transcorregut)

    # Retorna "True" només si el missatge reconegut per ràdio és el mateix que l'esperat.
    def pregunta(self, missatge: str) -> bool:
        received_message = "None"
        if missatge == received_message:
            return True
        else:
            return False

    # Estabilitza l'avió per a posar-lo en una direcció en balanceig i el capcineig, però no mou la guinyada.
    # Un escalar més gran el mourà més de pressa, però serà menys precís.
    def estabilitza(self, nou_balanceig: float | None = 0, nou_capcineig: float | None = 0, escalar: float = 1):

        if nou_balanceig is not None:
            self.canvia_balanceig(escalar * (nou_balanceig - self.balanceig))
        if nou_capcineig is not None:
            self.canvia_capcineig(escalar * (nou_capcineig - self.capcineig))

    # 0 és sense canvi, valors positius roten l'avió cap a dalt i negatius cap a baix.
    def canvia_capcineig(self, velocitat: float | None):
        if velocitat is None:
            return

        elif velocitat > 0:
            pca.servo[3].angle = MIN_ANG[3]
            pca.servo[2].angle = MIN_ANG[2]

        elif velocitat < 0:
            pca.servo[3].angle = MAX_ANG[3]
            pca.servo[2].angle = MAX_ANG[2]

    # 0 és sense canvi, valors positius roten l'avió cap a la dreta i negatius cap a l'esquerra.
    def canvia_balanceig(self, velocitat: float | None):
        if velocitat is None:
            return

        elif velocitat > 0:
            pca.servo[1].angle = MIN_ANG[1]
            pca.servo[0].angle = MAX_ANG[0]
            pca.servo[1].angle = MIN_ANG[3]
            pca.servo[0].angle = MAX_ANG[2]

        elif velocitat < 0:
            pca.servo[1].angle = MAX_ANG[1]
            pca.servo[0].angle = MIN_ANG[0]
            pca.servo[1].angle = MAX_ANG[3]
            pca.servo[0].angle = MIN_ANG[2]

    # Usa un percentatge. Normalment, 5% és el mínim i 10% el màxim.
    def assigna_velocitat_a(self, amount: float):
        motor.value = amount / 100


def main():
    print("main")
    global mens
    fase: str = "Esperant per enlairar-se"
    temps_inicial: float = time.time()
    temps_anterior: float = temps_inicial
    temps_actual: float = temps_inicial
    temps_transcorregut: float = 0
    espai_per_aterrar: float = 0
    avio: Avio = Avio()

    print("Buscant gps...")
    latitud_inicial, altura_inicial, longitud_inicial = troba_posicio()
    print("Començant loop")
    while True:
        # Calculem el temps que ha transcorregut des de l'última execució del bucle
        temps_anterior = temps_actual
        temps_actual = time.time() - temps_inicial
        temps_transcorregut = temps_actual - temps_anterior

        # Executem les funcions fonamentals que s'han d'executar constantment
        avio.rutina(temps_transcorregut)

        if "M" in mens:
            print('Manual Activat')
            fase = "Control manual"

        # Aquí programem el que farem a cada fase del vol.
        match fase:
            case "Control manual":
                if "V" in mens:
                    index = mens.index("V")
                    nova_velocitat = mens[index + 1: index + 3]
                    print(nova_velocitat)
                    avio.assigna_velocitat_a(int(nova_velocitat))
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

            case "Esperant per enlairar-se":
                # Al principi ens esperem fins a rebre confirmació de la torre de control
                if "T" in mens:
                    # Un cop tenim la confirmació passem a la següent fase i encenem motors.
                    fase = "Enlairant-se"
                    avio.assigna_velocitat_a(10)

            case "Enlairant-se":
                # Apunti el morro cap a dalt.
                avio.estabilitza(0, 45)

                # Quan hàgim pujat a una bona altura, girem per anar on volem.
                if avio.altura >= 10:
                    fase = "Estabilitzar abans de rotar"

                    # Amb Pitàgores, ens guardem també la distància des de la pista fins on arriba ara com a referència.
                    # Durant l'aterratge ens posarem a la mateixa distància per a tenir espai suficient.
                    espai_per_aterrar = math.sqrt(
                        (avio.latitud - latitud_inicial) ** 2 + (avio.longitud - longitud_inicial) ** 2)

                    # Guardem també l'àngle en el que estem anant, és a dir, la guinyada.
                    guinyada_inicial = avio.guinyada

            case "Estabilitzar abans de rotar":
                # Només volem que s'estabilitzi, res més.
                avio.estabilitza()

                # Un cop estigui estabilitzat, passem de fase
                if -2 < avio.capcineig < 2:
                    fase = "Rotació d'enlairament"

            case "Rotació d'enlairament":
                # Volem que giri 180° per a tornar cap enrere.
                avio.canvia_balanceig(100)
                avio.canvia_capcineig(100)

                # Rotarà cap a la dreta, per tant, seran valors positius. Però en arribar a 180° passa a -180°.
                # Aleshores, realment volem fer la comparació amb valors negatius per a quan "dona la volta".
                if avio.guinyada <= -150:
                    fase = "Vol creuer"

            case "Vol creuer":
                # L'estabilitzem, però pujant o baixant segons calgui per a compensar canvis d'altura
                avio.estabilitza(0, (10 - avio.altura) * 3)

                # Aquí és on entra la detecció d'ocells, no ho fem a les altres fases perquè fer maniobres
                # evasives és molt perillós i podria resultar en un accident amb més probabilitat que si seguim.
                if detectant_perill():
                    avio.estabilitza(0, 45, 5)

                distancia_al_aeroport = math.sqrt(
                    (avio.latitud - latitud_inicial) ** 2 + (avio.longitud - longitud_inicial) ** 2)
                direccio_al_aeroport = math.tan(avio.longitud)
                if distancia_al_aeroport >= espai_per_aterrar and abs(
                        int(avio.guinyada - direccio_al_aeroport + 360)) & 180 >= 90:
                    fase = "Rotació d'aterratge"

            case "Rotació d'aterratge":
                avio.canvia_balanceig(100)
                avio.canvia_capcineig(100)

                if avio.guinyada >= 360 or avio.guinyada <= 30:
                    fase = "Vol creuer"

            case "Aterrant":
                avio.assigna_velocitat_a(5)
                avio.estabilitza()

                if avio.altura <= 1:
                    avio.assigna_velocitat_a(-10)

                if avio.velocitat <= 0:
                    avio.assigna_velocitat_a(0)


main()
