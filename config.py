from math import *
import random
from pygame import midi
from pygame import joystick

midi_mode = False
verbose = True

#from launchpad import buttons

def midiout(device,note=0,velocity=127,channel=0):                          
    device.write_short(0xB0+channel,note,velocity)

# Sparsity of button pushes (float 0-1)
# Determines how many launchpad toggles turn on
sparsity = 0.0 
sparsity_param = 0.0

# Initialize Devices
print "Initializing Devices..."

# Device Bools
nanokontrol_set = False
launchpad_set = False
remotesl_set = False
nanokey_set = False
if joystick.get_init() and joystick.get_count() > 0: joystick_set = True
else: joystick_set = False
     


# MIDI config
for x in range(midi.get_count()):
    dev_info = midi.get_device_info(x)
    print x, dev_info
    if 'Launchpad' in dev_info[1] and dev_info[2]:
        launchpad_in = midi.Input(x)
        launchpad_set = True
	print "Launchpad In set"
    elif 'Launchpad' in dev_info[1] and not dev_info[2]:
        launchpad_out = midi.Output(x)
        launchpad_set = True
	print "Launchpad Out set"
    elif 'nanoKONTROL2' in dev_info[1] and dev_info[2]:
        nanokontrol_in = midi.Input(x)
        nanokontrol_set = True
        print "nanoKONTROL set"
    elif 'nanoKEY' in dev_info[1] and dev_info[2]:
        nanokey_in = midi.Input(x)
        nanokey_set = True
        print "nanoKEY set"
    elif 'MIDIIN3' in dev_info[1] and 'ReMOTE ZeRO SL' in dev_info[1]:
        remotesl_in = midi.Input(x)
        remotesl_set = True
        print "RemoteSL Input set"
    elif 'loopMIDI Port 1' in dev_info[1] and not dev_info[2]:
        yoke1 = midi.Output(x)
        print "Yoke 1 discovered"
    elif 'loopMIDI Port 2' in dev_info[1] and not dev_info[2]:
        yoke2 = midi.Output(x)
        print "Yoke 2 discovered"
    elif 'loopMIDI Port 3' in dev_info[1] and not dev_info[2]:
        yoke3 = midi.Output(x)
        print "Yoke 3 discovered"
    elif 'loopMIDI Port 4' in dev_info[1] and not dev_info[2]:
        yoke4 = midi.Output(x,latency=1)
        print "Yoke 4 discovered"
    elif 'loopMIDI Port 7' in dev_info[1] and not dev_info[2]:
        yoke7 = midi.Output(x)
        print "Yoke 7 discovered"
    elif 'loopMIDI Port 8' in dev_info[1] and not dev_info[2]:
        yoke8 = midi.Output(x)
        print "Yoke 8 discovered"

# Parameters

# Determins parameter frequency
max_freq = 3

class ParamState():
    def __init__(self,sin_amt=.5, cos_amt=.5,sin_freq=pi,
                 cos_freq=pi,sin_phase=0.0,cos_phase=0.0):
        self.sin_amt = sin_amt
        self.cos_amt = cos_amt
        self.sin_freq = sin_freq
        self.cos_freq = cos_freq
        self.sin_phase = sin_phase
        self.cos_phase = cos_phase

    def push_out(self,x):
        return int(round(127*(self.sin_amt*sin(self.sin_freq*x + self.sin_phase) + 
               self.cos_amt*cos(self.cos_freq*x + self.cos_phase))))

def rand_param(ia):                                                  
    global sparsity_param
    '''
    Cellular Automata? Random primes? Based on B0ner theory?
    Randomizes which parameters on the specified rack become                # Here is where we can get creative.  If we need to make it deterministic, so be it
    'controllable.'  If there are too many, change the sparsity.
    Lag due to this is the biggest problem. 
    Accepts 8 element array of 1's and zeros, and outputs a different array of 1's and zeros, and changes the ParamState P.
    '''
    
    for i in xrange(8):
        if int(round(random.uniform(0,1 - sparsity_param/2))) == 1:
            ia[i][0] = 1
            ia[i][1].sin_amt = random.uniform(0.0,1.0)
            ia[i][1].cos_amt = 1.0-ia[i][1].sin_amt
            ia[i][1].sin_freq = random.randint(1,max_freq)*pi
            ia[i][1].cos_freq = random.randint(1,max_freq)*pi
            ia[i][1].sin_phase = random.uniform(0.0,2*pi)
            ia[i][1].cos_phase = random.uniform(0.0,2*pi)
        else:
            ia[i][0] = 0

def rand_param_val(note,ia):
    for i in xrange(8):
        ia[i][1].sin_amt = random.uniform(0.0,1.0)
        ia[i][1].cos_amt = 1.0-ia[i][1].sin_amt
        ia[i][1].sin_freq = random.randint(1,max_freq)*pi
        ia[i][1].cos_freq = random.randint(1,max_freq)*pi
        ia[i][1].sin_phase = random.uniform(0.0,2*pi)
        ia[i][1].cos_phase = random.uniform(0.0,2*pi)
        midiout(device=yoke7, note=i + note*8 - (note/8)*64,
                velocity=ia[i][1].push_out(random.uniform(0.0,1.0)),channel=(note/8)+1)

