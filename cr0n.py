import pygame
from pygame import midi
from pygame import joystick



# Initialize
print "Initializing...","\n"

pygame.init()
midi.init()
joystick.init()

import gradient 
import devices

if __name__=='__main__':
    gradient.procstart()
    while True:
        devices.poll()

