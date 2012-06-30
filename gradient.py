from config import *
import time
from processing import Process, Pipe
parent, child = Pipe()

# Gradient

active_ramps = []

duration = 0.1 # Duration of 1.0 sweeps in seconds

class RampState():
    # int, int, float, float
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
        self.start_time = time.time()
        if direction == 'up':
            self.current_progress = 0.0
            self.transfer = 0.0
        else:
            self.current_progress = 1.0
            self.transfer = 1.0

    def push(self):
        now = time.time()
        if ((self.current_progress == 1.0 and self.direction == 'up') or
           (self.current_progress == 0.0 and self.direction == 'down')):
            active_ramps.remove(self)
        if self.direction == 'up':
            self.current_progress = self.current_progress + ((now - self.start_time)/duration)
            self.start_time = now
            self.current_progress = max(min(self.current_progress, 1), 0) # Clamp to [0,1]
            print self.current_progress
            midiout(yoke2,self.position,int(floor(self.current_progress*127)),11)
        else:
            self.current_progress = self.current_progress - ((now - self.start_time)/duration)
            self.start_time = now
            self.current_progress = max(min(self.current_progress, 1), 0) # Clamp to [0,1]
            print self.current_progress,self.position
            midiout(yoke2,self.position,int(ceil(self.current_progress*127)),11)


def gradient(conn):
    '''
    Thanks to Randall Leeds (Twitter @tilgovi) for help on this one. <3<3
    '''
    print "Gradient Initiated..."

    global duration, remotesl_in
        
    offset = 1
    while True:                         # Loop constantly
        if remotesl_in.poll():
            remotesl_data = remotesl_in.read(1)
            sl_control = remotesl_data[0][0][1]
            sl_value = remotesl_data[0][0][2]
            midiout(velocity=sl_value,note=sl_control,channel=9,device=yoke6)
            if sl_control == 16:
                duration = 8.0*(sl_value + offset)/(127 + offset)
            elif sl_control == 8:
                conn.send((8,float(sl_value)/127))
            elif (sl_control > 23 and sl_control < 32):
                print (sl_control,sl_value)
                conn.send((sl_control,sl_value))
                
        if conn.poll():
            tmp = conn.recv()           # tmp[0] is note, tmp[1] is new state in string form
            if tmp[1]=='on':
                found = False                
                for j in active_ramps:
                    if tmp[0] == j.position:  # If note is already in queue, change it from down to up
                        j.direction = 'up'
                        print "up!"
                        j.start_time = time.time()
                        found = True
                    j.push()

                if not found:
                    active_ramps.append(RampState(tmp[0],'up'))
                    active_ramps[-1].push()
            else:
                found = False
                for j in active_ramps:     
                    if tmp[0] == j.position:  # If note is already in queue, change it from up to down
                        j.direction = 'down'
                        print "down!"
                        j.start_time = time.time()
                        found = True
                    j.push()

                if not found:
                    active_ramps.append(RampState(tmp[0],'down'))
                    active_ramps[-1].push()

        else:
            for j in active_ramps:
                j.push()
    
p = Process(target=gradient,args=(child,))
def procstart(): #Initialize separate process
    print "Process started..."
    p.start()

            

