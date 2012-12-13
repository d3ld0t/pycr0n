
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
        if (self.current_progress == 1.0 and self.direction == 'up'):
            active_ramps.remove(self)
        if (self.current_progress == 0.0 and self.direction == 'down'):
            active_ramps.remove(self)
            midiout(note=self.position,velocity=0,device=yoke8) # Order matters
        if self.direction == 'up':
            self.current_progress = self.current_progress + ((now - self.start_time)/duration)
            self.start_time = now
            self.current_progress = max(min(self.current_progress, 1), 0) # Clamp to [0,1]
            midiout(yoke4,self.position,int(floor(self.current_progress*127)),11)
        else:
            self.current_progress = self.current_progress - ((now - self.start_time)/duration)
            self.start_time = now
            self.current_progress = max(min(self.current_progress, 1), 0) # Clamp to [0,1]
            midiout(yoke2,self.position,int(ceil(self.current_progress*127)),11)

if remotesl_set:

    def gradient(conn):
	'''
	Thanks to Randall Leeds (Twitter @tilgovi) for help on this one. <3<3
	'''
        print "Gradient Initiated..."

        global duration, remotesl_in
            
        offset = 1
        slowdown = 0
        SLEEP_TIME = 0.050
        while True:                         # Loop constantly

                
            if conn.poll():
                tmp = conn.recv()           # tmp[0] is note, tmp[1] is new state in string form
                if tmp[1] == 'duration':
                    duration = tmp[0] 
                elif tmp[1]=='on':

                    found_yet = False                
                    for j in active_ramps:
                        if tmp[0] == j.position:  # If note is already in queue, change it from down to up
                            j.direction = 'up'
                            print "up!"
                            j.start_time = time.time()
                            found_yet = True
                        j.push()

                    if not found_yet:
                        active_ramps.append(RampState(tmp[0],'up'))
                        active_ramps[-1].push()
                else:
                    found_yet = False
                    for j in active_ramps:     
                        if tmp[0] == j.position:  # If note is already in queue, change it from up to down
                            j.direction = 'down'
                            print "down!"
                            j.start_time = time.time()
                            found_yet = True
                        j.push()

                    if not found_yet:
                        active_ramps.append(RampState(tmp[0],'down'))
                        active_ramps[-1].push()

            else:
                for j in active_ramps:
                    j.push()

            time.sleep(SLEEP_TIME)
	
    p = Process(target=gradient,args=(child,))
    def procstart(): #Initialize separate process
        print "Process started..."
        p.start()

            

