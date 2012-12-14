import pygame
from pygame import midi
from processing import Process, Pipe
import config
from config import *
if config.launchpad_set: import launchpad
import gradient
parent,child = Pipe()
import time
import samplebox

global launchpad_in, launchpad_out, nanokontrol_in, remotesl_in, yoke1, yoke2, yoke3, yoke4, yoke7, yoke8

if config.launchpad_set:
    # Clear Launchpad
    print "\n","Clearing...","\n"
    for i in xrange(8):
        launchpad.clear(i)

plateu_range = .4

if config.joystick_set: import logitech as lt
rand_mode = 'off'
sample_mode = 'off'
note_state = "off"
sample_off_queue = []

buttondown = 10
buttonup = 11
axismotion = 7
controlpad = 9
noevent = 0

def poll():
    global shell, rand_mode, sample_mode
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
                if control == 176 and velocity == 127:
                    if note == 104:
                        # Randomize which knobs controllable for on devices
                        for i in xrange(64):
                            if launchpad.buttons[i][0] == 1:
                                rand_param(launchpad.buttons[i][1])
                    elif note == 105:
                        # Randomize which knobs controllable + randomize position of all knobs
                        # for on devices
                        for i in xrange(64):
                            if launchpad.buttons[i][0] == 1:
                                rand_param(launchpad.buttons[i][1])
                                rand_param_val(i,launchpad.buttons[i][1]) 

                elif note%16 < 8:
                    rand_param(launchpad.buttons[position][1])

    if config.remotesl_set:

        if remotesl_in.poll():
	    print "remotesl!"
            seen_stuff = True
            remotesl_data = remotesl_in.read(1)
            sl_type = remotesl_data[0][0][0]
            sl_control = remotesl_data[0][0][1]
            sl_value = remotesl_data[0][0][2]
    

            if sl_type == 178:
                midiout(velocity=sl_value,note=sl_control,channel=9,device=yoke4)

                if sl_control == 16:         # Duration
                    gradient.parent.send([8.0*(sl_value + 1)/(127 + 1),'duration'])

                elif sl_control == 17:       # Sparsity
                    config.sparsity=float(sl_value)/127
                elif sl_control == 18:       # Sparsity_param
                    config.sparsity_param = float(sl_value)/127

                elif (sl_control > 23 and sl_control < 32): # Butter/No butter
		    print "slider"
                    launchpad.armed[sl_control -24] = sl_value/127
            elif sl_type == 146: 
                # Touch pads
                yoke4.write([[[144,sl_control,127],midi.time()],
                [[128,sl_control,64],midi.time()+int(float(sl_value)/127*4000) + 200]])
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

    if config.nanokey_set:
        if nanokey_in.poll():
            data = nanokey_in.read(1)
            status = data[0][0][0]
            note = data[0][0][1]
            velocity = data[0][0][2]
            channel = data[0][0][3]
            timestamp = data[0][1]
            max_time = 4000 #ms
            if config.verbose: print "Velocity: %i note: %i status %i channel %i timestamp %i" \
                    % (velocity,note,status,channel,timestamp)

            if status == 144:
                yoke4.write_short(144,note,127)
                sample_off_queue.append([note,timestamp + int(random.uniform(0.0,1.0)*max_time)])
       
            seen_stuff = True

        for item in sample_off_queue[:]: # a copy
            if midi.time() > item[1]:
                yoke4.write_short(128,item[0],64)
                sample_off_queue.remove(item)

    if config.joystick_set: 
        

        #global lt.pad_state, lt.axis2_state
        tmpevent = pygame.event.poll()

        if tmpevent.type == buttondown:
            seen_stuff = True
            if tmpevent.button == 0:
                midiout(note=0,velocity=127,channel=13,device=yoke3)
            #UNDO PT	
            elif tmpevent.button == 4:
                rand_mode = 'on'
                launchpad.flash(0,48,'on')
            elif tmpevent.button == 5:
                sample_mode = 'on'
                rand_param(samplebox.samplebox)
                launchpad.flash(0,3,'on')
            elif tmpevent.button == 6:
                lt.start_axis = (lt.logitech_in.get_axis(0) + lt.logitech_in.get_axis(1))/6
                lt.old_axis = lt.axis_state
            elif tmpevent.button == 7:
                lt.start_axis2 = (lt.logitech_in.get_axis(2) + lt.logitech_in.get_axis(3))/6
                lt.old_axis2 = lt.axis_state2
            elif tmpevent.button == 9:
                parent.send('reload')
            elif tmpevent.button == 10:
                if lt.logitech_in.get_button(6): lt.start_axis = (lt.logitech_in.get_axis(0) + lt.logitech_in.get_axis(1))/6
                else: lt.start_axis = (lt.logitech_in.get_axis(0) + lt.logitech_in.get_axis(1))/16
                if lt.axis_button_state == 'off': 
                    lt.axis_button_state = 'on'
            elif tmpevent.button == 11:
                if lt.logitech_in.get_button(7): lt.start_axis2 = (lt.logitech_in.get_axis(2) + lt.logitech_in.get_axis(3))/6
                else: lt.start_axis2 = (lt.logitech_in.get_axis(2) + lt.logitech_in.get_axis(3))/16
                if lt.axis_button_state2 == 'off': 
                    lt.axis_button_state2 = 'on'

        if tmpevent.type == buttonup:
            seen_stuff = True
            for i in xrange(12):
                if not lt.logitech_in.get_button(i):
                    if i == 4: 
                        rand_mode = 'off'
                        launchpad.flash(0,0,'off')
                    if i == 5:
                        sample_mode = 'off'
                        launchpad.flash(0,3,'off')
                    if i == 6:
                        lt.start_axis = (lt.logitech_in.get_axis(0) + lt.logitech_in.get_axis(1))/16
                        lt.old_axis = lt.axis_state
                    if i == 7:
                        lt.start_axis2 = (lt.logitech_in.get_axis(2) + lt.logitech_in.get_axis(3))/16
                        lt.old_axis2 = lt.axis_state2
                    if i == 10:
                        if lt.axis_button_state == 'on': 
                            lt.old_axis = lt.axis_state
                            lt.axis_button_state = 'off'
                    if i == 11:
                        if lt.axis_button_state2 == 'on': 
                            lt.old_axis2 = lt.axis_state2
                            lt.axis_button_state2 = 'off'

        if tmpevent.type == controlpad:
            seen_stuff = True

        if tmpevent.type == axismotion: 
                
            seen_stuff = True

            if sample_mode == 'off':

                if lt.axis_button_state == 'on':
                    if lt.logitech_in.get_button(6):
                        tmp = (lt.logitech_in.get_axis(0) + lt.logitech_in.get_axis(1))/6 - lt.start_axis + lt.old_axis
                    else:
                        tmp = (lt.logitech_in.get_axis(0) + lt.logitech_in.get_axis(1))/16 - lt.start_axis + lt.old_axis
                    if tmp != lt.axis_state:
                        lt.axis_state = tmp
                        launchpad.push_params(lt.axis_state)
            else:
                if lt.axis_button_state2 == 'on':
                    if lt.logitech_in.get_button(7):
                        tmp2 = (lt.logitech_in.get_axis(2) + lt.logitech_in.get_axis(3))/6 - lt.start_axis2 + lt.old_axis2
                    else:
                        tmp2 = (lt.logitech_in.get_axis(2) + lt.logitech_in.get_axis(3))/16 - lt.start_axis2 + lt.old_axis2
                    if tmp2 != lt.axis_state2:
                        lt.axis_state2 = tmp2
                        # for all in samplebox param state push out 
                        for note in xrange(8):
                            if samplebox.samplebox[note][0] == 1:
                                midiout(device=yoke7, note=note,
                                        velocity=samplebox.samplebox[note][1].push_out(lt.axis_state2),channel=10)
                
            

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
