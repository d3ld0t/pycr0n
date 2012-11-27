from pywinauto import application
import pygame
import logitech as lt
import pyperclip

app = application.Application()
app.connect_(path = r"C:\Program Files (x86)\Ableton\Live 8.2.1\Program\Live 8.2.1.exe")

#app2 = application.Application()
#app2.start_(r"C:\Windows\System32\notepad.exe")

dlg = app.top_window_()
#dlg2 = app2.top_window_()


def switch_fx(position):
    dlg.TypeKeys('1{RIGHT ' + str(position) + '}{ENTER}')

    while True:
        pygame.event.pump()
        if pygame.event.peek(pygame.JOYHATMOTION):
            print "hat"
            seen_stuff = True
            pygame.event.clear()
            if lt.logitech_in.get_hat(0) == (1,0):
                dlg.TypeKeys('{RIGHT}')
                #dlg2.TypeKeys('^v')
            elif lt.logitech_in.get_hat(0) == (-1,0):
                dlg.TypeKeys('{LEFT}')
            elif lt.logitech_in.get_hat(0) == (0,1):
                dlg.TypeKeys('{UP}')
                #dlg.TypeKeys('^r')
                #d#lg.TypeKeys('^c')
                #dl#g2.TypeKeys('^a')
                #dlg2.TypeKeys('^v')
                #print pyperclip.paste() 
                
            elif lt.logitech_in.get_hat(0) == (0,-1):
                dlg.TypeKeys('{DOWN}')
                #dlg.TypeKeys('^r')
                #dlg.TypeKeys('^c')
                #dlg2.TypeKeys('^a')
                #dlg2.TypeKeys('^v')
                #print pyperclip.paste() 
        elif pygame.event.peek(pygame.JOYBUTTONDOWN):
            pygame.event.clear()
            dlg.TypeKeys('{ENTER}')
            dlg.TypeKeys('{ESC}')
            break
