from gpiozero import PWMOutputDevice
import time

#PINS
Motor_PIN = 26

motor = PWMOutputDevice(Motor_PIN, frequency=50)

def set_motor_speed(duty):
    motor.value = duty / 100
    print(f"Set motor speed to {duty}%.")
    
try:
    print("Initializing ESC")
    set_motor_speed(10)
    time.sleep(2)
    
    set_motor_speed(5)
    time.sleep(2)
    
    set_motor_speed(7.5)
    time.sleep(2)
except:
    print("Run into an error while running.")
    pass
finally:
    set_motor_speed(0)
    print("Done")