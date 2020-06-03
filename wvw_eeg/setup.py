import sys
import socket
from psychopy import parallel, event, logging, visual, gui, core
from psychopy.hardware import keyboard

'''
    - Before running this script on a given computer, you will need to update the address for networking
        between the stim and dig computers, as well as the parallel port address.
    - Check and update the refresh rate of the monitor to have accurate 
        timing of stimulus presentation.
    - Update the window to be the correct size of your monitor
'''


class Setup:
    def __init__(self):
        self.debug = True

        self.monitor = None
        self.EEG = None
        self.port = None

        self.rr = None
        self.ms100 = None

        self.log_host = None
        self.log_port = None
        self.addr = None
        self.UDPSock = None

        self.win = None
        self.text = None

        self.dlg_dict = None
        self.dlg = None

        self.kb = None
        self.ver = None
        self.ver_num = None

        self.log = None

    def set_specs(self):
        #  Name monitor and EEG cabin
        self.monitor = 'CABIN1'
        self.EEG = 1

        if self.debug:
            self.monitor = "EM"
            self.EEG = None

        # Parallel port address for cabin1 in Psych (booth)
        if self.EEG:
            self.port = parallel.ParallelPort(address=0x0378)

        # Define refresh rate
        self.rr = 60.0
        self.ms100 = self.rr / 10.0

        # Give Host and Port Addresses for socket
        self.log_host = '192.17.53.41'
        self.log_port = 17322
        self.addr = (self.log_host, self.log_port)

        # This is for networking between the dig and stim computer to send which item it is currently on
        self.UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def set_win(self):
        # Define window (this is for psych booth)
        self.win = visual.Window(size=[1280, 1024], monitor=self.monitor, fullscr=True, units='deg',
                                 viewPos=None, color=[-0.2, -0.2, -0.2])

        if self.debug:
            self.win = visual.Window(size=[2560, 1600], monitor=self.monitor, fullscr=True, units='deg',
                                     viewPos=None, color=[-0.2, -0.2, -0.2])

        self.win.recordFrameIntervals = True
        self.win.refreshThreshold = 1/self.rr + 0.004
        logging.console.setLevel(logging.WARNING)

    def set_text(self):
        self.text = visual.TextStim(self.win, text='', alignText='center', height=0.8, units='deg', autoLog=False)
        self.text.autoDraw = True

    def make_gui(self):
        # Make a gui and initialize a dictionary for ID
        self.dlg_dict = {'Participant ID': ''}
        self.dlg = gui.DlgFromDict(self.dlg_dict, title='New session')

    def set_kb_mouse(self):
        # Set keyboard to be kb and hide mouse
        self.kb = keyboard.Keyboard()
        self.win.mouseVisible = False

    def set_exit_proc(self):
        event.globalKeys.clear()
        event.globalKeys.add(key='q', modifiers=['ctrl', 'alt'], func=core.quit())

    def set_ver(self):
        if len(sys.argv) < 2:
            self.ver = "1"  # If input given is less than two characters, default to version 1
        else:
            self.ver = sys.argv[1]

        self.ver_num = int(self.ver[0])

    def make_log(self):
        self.log = logging.LogFile("exp WvW_EEG v%s.log" % self.ver, level=logging.EXP, filemode='a')
