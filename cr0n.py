# Initialize
print "Initializing...","\n"


import pygame
pygame.init()

from pygame import midi
midi.init()

import config
import devices
import time


if config.joystick_set:
    from pygame import joystick
    joystick.init()


if config.remotesl_set: import gradient 


SLEEP_TIME = 0.050

if __name__=='__main__':

    if config.midi_mode:
        print "Entering midi mode! Ctrl-c to quit (I know super jank)"
        while True:
            note = input('Please enter note: ')
            channel = input('Please enter channel: ')
            print "Sending..."
            config.midiout(device=config.yoke4,note=note,channel=channel,velocity=127)
    else:

        if config.remotesl_set and config.joystick_set:
            print "Slapping on butter and a lot of it"
            gradient.procstart()
        else: print "No cr0n? You are a goddamn douchebag. Install some sort of fucking debug mode you ass"

        while True:
            while devices.poll():
                pass

            time.sleep(SLEEP_TIME)


