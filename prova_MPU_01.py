import smbus					#import SMBus module of I2C
import time
import math

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
    try:
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value
    except OSError as er:
        print("ERROR:",er)
        value = 0

bus = smbus.SMBus(1)
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

print (" Reading Data of Gyroscope and Accelerometer")

Rx = 0
Ry = 0
Rz = 0

#Llegim les dades per a calibrar el sensor
for i in range(10):
    a = read_raw_data(ACCEL_XOUT_H)
    a = read_raw_data(ACCEL_YOUT_H)
    a = read_raw_data(ACCEL_ZOUT_H)
        
    a = read_raw_data(GYRO_XOUT_H)
    a = read_raw_data(GYRO_YOUT_H)
    a = read_raw_data(GYRO_ZOUT_H)

prev_time = time.time()

while True:
    current_time = time.time()
    dtime = current_time - prev_time
    prev_time = current_time
    
    print ("Rx=%.2f" %Rx + "º\tRy=%.2f" %Ry + "º\tRz=%.2f" %Rz + "º" + "\tDt=%.4f" %dtime)
    
    #Read Gyroscope raw value
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    
    Gx = gyro_x/131.0
    Gy = gyro_y/131.0
    
    Rx += (Gx + 0.2) * dtime * 18 + 180
    Ry += (Gy - 0.296) * dtime * 18 + 180
    
    Rx %= 360
    Ry %= 360
    
    Rx -= 180
    Ry -= 180
    
    time.sleep(0.01)