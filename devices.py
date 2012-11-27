import pygame
from processing import Process, Pipe
import config
from config import *
if config.launchpad_set: import launchpad
import gradient
parent,child = Pipe()

global launchpad_in, launchpad_out, nanokontrol_in, yoke1, yoke2, yoke3, yoke4, yoke7, yoke8

if config.launchpad_set:
    # Clear Launchpad
    print "\n","Clearing...","\n"
    for i in xrange(8):
        launchpad.clear(i)

plateu_range = .4

if config.joystick_set: import logitech as lt
rand_mode = 'off'

buttondown = 10
buttonup = 11
axismotion = 7
controlpad = 9
noevent = 0

def poll():
    global shell, rand_mode
    seen_stuff = False

    if config.launchpad_set:
        if launchpad_in.poll():
            seen_stuff = True
            data = launchpad_in.read(1)
            control = data[0][0][0]
            note = data[0][0][1]
            row = (note-8)/16
            position = note - 8*(note/16)
            
            velocity = data[0][0][2]
            print "rand_mode: %s" % rand_mode
            
            if rand_mode == 'off':
                if velocity == 127:
                    #if lt.logitech_in.get_button(1):
                    #    navigation.switch_fx(note/16*8 + note%16)
                    if control == 176:
                        launchpad.clear(note - 104)
                    elif note%16 < 8:
                        launchpad.toggle(note)
                 
                    elif note%16 == 8:
                        launchpad.rand(row)
            elif rand_mode == 'on':
                rand_param(launchpad.buttons[position][1])

    if config.remotesl_set:

        if gradient.parent.poll():
            seen_stuff = True
            data = gradient.parent.recv()
            if data[0] == 8:
                config.sparsity = data[1]
            elif data[0] > 23 and data[0] < 32:
                launchpad.armed[data[0] - 24] = data[1]/127

    # nanokontrol CCs all on channel 0
    # knobs 16-23
    # sliders 0-7
    # solo 32-39
    # mute 48-55
    # rec 64-71
    # rew 43
    # ff 44
    # stop 42
    # play 41
    # record 45
    # cycle 46
    # set left right 60-62
    # trackleft trackright 58-59

    if config.nanokontrol_set:
        if nanokontrol_in.poll():
            seen_stuff = True
            data = nanokontrol_in.read(1)
            note = data[0][0][1]
            velocity = data[0][0][2]
            if (note > 31 and note < 40):
                midiout(note=note,velocity=127,channel=12,device=yoke3)
            elif (note > 47 and note < 56):
                midiout(note=note, velocity=127 if velocity == 0 else 0, channel=12,device=yoke3)
            elif (note > 63 and note < 72):
                midiout(note=note,velocity=127,channel=12,device=yoke3)
            elif (note > 15 and note < 24):
                if velocity < 64:
                    midiout(note=note+56,velocity = int( 127*max(min((velocity/(63.0 - 64.0*plateu_range)),1.0),0.0)    ) ,channel=12,device=yoke3)
                else:
                    midiout(note=note+64,velocity=int( 127*max(min(((velocity - 64 - 64.0*plateu_range)/(63.0 - 64.0*plateu_range)),1.0),0.0)    ),channel=12,device=yoke3)
            else:
                midiout(note=note,velocity=velocity,channel=12,device=yoke3)

    if config.joystick_set: 

        

        #global lt.pad_state, lt.axis2_state
        tmpevent = pygame.event.poll()

        if tmpevent.type == buttondown:
            seen_stuff = True
            for i in xrange(12):
                if lt.logitech_in.get_button(i):
                    if i == 0:
                        midiout(note=0,velocity=127,channel=13,device=yoke3)
                    #UNDO PT	
                    if i == 4:
                        rand_mode = 'on'
                        launchpad.flash(0,0,'on')
                    if i == 6:
                        lt.start_axis = lt.logitech_in.get_axis(0)/3
                        lt.old_axis = lt.axis_state
                    if i == 9:
                        parent.send('reload')
                    if i == 10:
                        if lt.logitech_in.get_button(6): lt.start_axis = lt.logitech_in.get_axis(0)/3
                        else: lt.start_axis = lt.logitech_in.get_axis(0)/8
                        if lt.axis_button_state == 'off': 
                            lt.axis_button_state = 'on'

        if tmpevent.type == buttonup:
            seen_stuff = True
            for i in xrange(12):
                if not lt.logitech_in.get_button(i):
                    if i == 4: 
                        rand_mode = 'off'
                        launchpad.flash(0,0,'off')
                    if i == 6:
                        lt.start_axis = lt.logitech_in.get_axis(0)/8
                        lt.old_axis = lt.axis_state
                    if i == 10:
                        if lt.axis_button_state == 'on': 
                            lt.old_axis = lt.axis_state
                            lt.axis_button_state = 'off'

        if tmpevent.type == controlpad:
            seen_stuff = True

        if tmpevent.type == axismotion:
            seen_stuff = True

            if lt.axis_button_state == 'on':
                if lt.logitech_in.get_button(6):
                    tmp = lt.logitech_in.get_axis(0)/3 - lt.start_axis + lt.old_axis
                else:
                    tmp = lt.logitech_in.get_axis(0)/8 - lt.start_axis + lt.old_axis
                if tmp != lt.axis_state:
                    lt.axis_state = tmp
                    launchpad.push_params(lt.axis_state)

            """
            if lt.logitech_in.get_button(6):
                tmp = lt.logitech_in.get_axis(0)
                pygame.event.clear()
                if (lt.axis_state != tmp) and lt.logitech_in.get_button(10):
                lt.axis_state = tmp
                launchpad.push_params(lt.axis_state + lt.axis2_state)
            else:
                tmp2 = lt.logitech_in.get_axis(0)/8
                pygame.event.clear()
                if (lt.axis2_state != tmp2) and lt.logitech_in.get_button(10):
                lt.axis2_state = tmp2
                launchpad.push_params(lt.axis_state + lt.axis2_state)
            #Coarse
            """

    return seen_stuff
