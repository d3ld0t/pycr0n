import pygame
from pygame import midi

pygame.init()
midi.init()

for x in range(midi.get_count()):
    print x,midi.get_device_info(x)
	
print "setting launch"
launch = midi.Output(22)
