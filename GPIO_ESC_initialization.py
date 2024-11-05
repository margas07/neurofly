from gpiozero import PWMOutputDevice
import time
import pygame

#PINS
Motor_PIN = 26

motor = PWMOutputDevice(Motor_PIN, frequency=50)

def set_motor_speed(duty):
    motor.value = duty / 100
    print(f"Set motor speed to {duty}%.")

current_speed = 0

pygame.init()
pygame.display.set_mode((640, 480))

try:
    running = True
    while running:
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            current_speed -= 0.1
            if current_speed < 0:
                current_speed = 0
            set_motor_speed(current_speed)
        elif keys[pygame.K_UP]:
            current_speed += 0.1
            set_motor_speed(current_speed)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        pygame.time.Clock().tick(60)
except:
    print("Run into an error while running.")
    pass
finally:
    pygame.quit()
    set_motor_speed(0)
    print("Done")
