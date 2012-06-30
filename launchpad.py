from gradient import parent
import random
from config import *

# Launchpad

# Launchpad colors
green = 48
red = 3

buttons = []

for x in xrange(64):
    buttons.append([0,[]])
    for y in xrange(8):
        buttons[x][1].append([0,ParamState()])

armed = []

for x in xrange(8):
    armed.append(0)

def set(position, state):
    '''
    Set the button on the Launchpad in position (0-63) to the state 0 (off) or 1 (on)
    '''
    if state:
        rand_param(buttons[position][1])
        if buttons[position][0] == 0:
            buttons[position][0] = 1
            parent.send([position,'on'])
            midiout(note=position,velocity=127,device=yoke8) # Order matters
            launchpad_out.note_on(position/8*16 + position%8,48,0)
    if not state:
        if buttons[position][0] == 1:
            for i in xrange(8):
                buttons[position][1][i][0] = 0
            buttons[position][0] = 0
            parent.send([position,'off'])
        
        midiout(note=position,velocity=0,device=yoke8) # Order matters
        launchpad_out.note_on(position/8*16 + position%8,0,0)
        

def toggle(note):
    '''
    Toggle the button on the Launchpad in position given by note (0-7, 16-23, etc...)
    '''
    position = note/16*8 + note%16
    if buttons[position][0] == 0:
        rand_param(buttons[position][1])
        midiout(note=position,velocity=127,device=yoke8,channel=0)
        parent.send([position,'on'])
        buttons[position][0] = 1
        launchpad_out.note_on(note,green,0)
    elif buttons[position][0] == 1:
        for i in xrange(8):
            buttons[position][1][i][0] = 0
        buttons[position][0] = 0
        launchpad_out.note_on(note,0,0)
        parent.send([position,'off'])
        midiout(note=position,velocity=0,device=yoke8,channel=0)

def clear(row):
    for x in range(8):
        set(row*8 + x,0)   

def rand(row):
    '''
    Randomize specified row's device on states
    '''
    random.seed()
    for x in range(8):
        set(x+row*8,int(round(random.uniform(0,1 - sparsity/2))))

def rand_all():
    for x in range(8):
        rand(x)

def push_params(external_data):
    for x in xrange(64):
        for y in xrange(8):
            if buttons[x][1][y][0] and buttons[x][0] and armed[x/8]:
                midiout(device=yoke7, note=y + x*8 - (x/8)*64,
                        velocity=buttons[x][1][y][1].push_out(external_data),channel=(x/8)+1)

