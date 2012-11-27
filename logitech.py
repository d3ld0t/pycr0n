from pygame import joystick
# Logitech definitions...

if joystick.get_init():
    print "Joystick module initialized...","\n"

    print joystick.get_count(), "joystick(s)...","\n"
    logitech_in = joystick.Joystick(0)

    logitech_in.init()
    print logitech_in.get_name(), " initialized...","\n"

pad_state = (0,0)
axis_button_state = 'off'
start_axis = 0.0
old_axis = 0.0
axis_state = 0
axis2_state = 0    
axis3_state = 0
