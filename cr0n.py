import pygame
from pygame import midi
from pygame import joystick

import time

# Initialize
print "Initializing...","\n"

pygame.init()
midi.init()
joystick.init()

import gradient 
import devices

SLEEP_TIME = 0.001

if __name__=='__main__':
    gradient.procstart()
    while True:
        while devices.poll():
            pass

        time.sleep(SLEEP_TIME)


