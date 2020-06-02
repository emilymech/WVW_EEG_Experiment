import sys
import time
import socket

from random import random
from psychopy import parallel, event, logging, visual, gui, core
from psychopy.hardware import keyboard


'''README:
    - Before running this script on a given computer, you will need to update the address for networking
        between the stim and dig computers, as well as the parallel port address.
    - Check and update the refresh rate of the monitor to have accurate 
        timing of stimulus presentation.
    - Update the window to be the correct size of your monitor
        '''

'''Definitions'''


class Setup:
    def __init__(self):
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
        self.EEG = 1  # Set this to none if you are debugging without sending triggers

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
        # Define window
        self.win = visual.Window(size=[1280, 1024], monitor=self.monitor, fullscr=True, units='deg',
                                 viewPos=None, color=[-0.2, -0.2, -0.2])
        self.win.recordFrameIntervals = True
        self.win.refreshThreshold = 1/self.rr + 0.004
        logging.console.setLevel(logging.WARNING)

    def set_text(self):
        self.text = visual.TextStim(self.win, text='', alignText='center', height=0.8, units='deg', autoLog=False)
        self.text.autoDraw = True

    def make_gui(self):
        # Make a gui and initialize a dictionary for ID
        self.dlg_dict = {'Subject ID': ''}
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


class Stimuli(Setup):
    def __init__(self):
        super().__init__()
        self.all_items = None
        self.blocks = None

        self.triggers = None

    def plausibility(self):
        pass

    def expected(self, expect, triggers, times, to_log=""):  # need to define expect
        self.text.text = "On a scale of 1-10, how much did you expect to see the last word in the sentence?"

        if self.triggers[current_item] != 0:
            datetime = time.strftime('%Y-%m-%d %H:%M:%S')
            msg = "%s\t%s\t%d\t%s" % (datetime, to_log, self.triggers[current_item], expect[current_item])
            self.win.logOnFlip(level=logging.EXP, msg=msg)

            self.win.flip()
        else:
            self.win.flip()

    def read_in_stimuli(self):
        self.all_items = {"train": [], "block1": [], "block2": [], "block3": []}
        self.blocks = ["train", "block1", "block2", "block3"]
        with open("02.25.20 - wvw v%s.txt" % self.ver, "r") as f:
            col_names = f.readline().strip().split("\t")
            ix = 0
            block = 1
            block_name = "block1"
            training = 1

            for row in f:
                ix += 1
                row_dict = {}
                parts = row.strip().split("\t")
                for cx in range(len(parts)):
                    row_dict[col_names[cx]] = parts[cx]

                words = row_dict['context'].split(" ")
                wx = len(words) - 2
                mark = 0

                row_dict['context'] = words
                row_dict['ItemExpID'] = int(row_dict['ItemExpID'])
                row_dict['cond'] = int(row_dict['cond'])

                len_words = len(words)

        # deal with this trigger part
        # +2 bc adj & noun EM: need to edit the base here to reflect my changes in the text files
        # if row_dict['typ'] == "train":
        #     base = 0
        #     triggers = [base] * (len_words + 2)
        #
        # else:
        #     base = (row_dict['cond'] << 4)  # condition number, 2 bits
        #     base += ((row_dict['ItemExpID'] & 3) << 6)  # last two bits of internal item ID number
        #     self.triggers = [base] * (len_words + 2)  # +2 bc adj & noun
        #     for wx in range(len_words):
        #         trigger = min(len_words + 2 - wx, 15)  # words at pos 16+ -> pos=15; +2 bc room for adj&noun
        #         triggers[wx] += trigger
        #
        # row_dict['trigger_base'] = base
        # row_dict['triggers'] = self.triggers
        #
        # if training:
        #     if row_dict["typ"] == "train":
        #         self.all_items["train"].append(row_dict)
        #         continue
        #     else:
        #         training = 0
        #         ix = 1
        # if ix == 81:
        #     ix = 1
        #     block += 1
        # self.all_items[self.blocks[block]].append(row_dict)

    def read_in_triggers(self):
        pass


class Experiment(Stimuli):
    def __init__(self):
        super().__init__()
        self.countdown = None

    def send_udp(self, msg):
        self.UDPSock.sendto(msg.encode(), self.addr)

    def wait_for_space(self):
        event.clearEvents()
        self.kb.getKeys(clear=True)
        while 1:
            key_presses = self.kb.getKeys(['space'])
            if len(key_presses):
                break
            self.win.flip()

    def present_gui(self):
        self.text.draw()
        self.text.text = "v%s" % self.ver
        self.wait_for_space()

    def show_seq(self, words, times, triggers, to_log=""):
        assert len(words) == len(times)
        current_thr = 0
        current_item = -1
        for frameN in range(int(sum(times))):
            if frameN == current_thr:
                current_item += 1
                current_thr += int(times[current_item])
                self.text.text = words[current_item]

                if words[current_item] != "" or triggers[current_item] != 0:
                    datetime = time.strftime('%Y-%m-%d %H:%M:%S')
                    msg = "%s\t%s\t%d\t%s" % (datetime, to_log, triggers[current_item], words[current_item])
                    self.win.logOnFlip(level=logging.EXP, msg=msg)

                self.win.flip()
                self.send_eeg_trig(self.triggers[current_item])
            else:
                self.win.flip()

    def send_eeg_trig(self):
        if not self.triggers or not self.EEG:
            return
        self.port.setData(self.triggers)
        core.wait(0.0005)
        self.port.setData(0)

    def present_experiment(self):
        self.countdown = 0
        for block in blocks:
            countdown += len(self.all_items[stage])


for stage in stages:
    items = all_items[stage]
    if stage == "train":
        text.text = "Training session.\n\nPlease press SPACE to proceed."
    elif stage == "block1":
        text.text = "End of the training session.\n\nPlease wait for the experimenter."
        wait_for_space()
        text.text = "The main part of the study.\n\nPlease press SPACE to proceed."
    else:
        text.text = "Time for a break.\n\nPlease press SPACE when you are ready."
    wait_for_space()

    for item in items:
        countdown -= 1
        send_udp("%d" % countdown)
        show_seq([""], [10 * ms100], [0])
        expected()
        wait_for_space()
        plausibility()
        wait_for_space()
        words = ["", "+++", ""]
        times = [10 * ms100, 5 * ms100, round((4.0 + random() * 4.0) * ms100)]
        triggers = [0, item['trigger_base'], 0]

        for wx in range(len(item['context'])):
            words += [item['context'][wx], ""]
            times += [3 * ms100, 2 * ms100]
            triggers += [item['triggers'][wx], 0]
        words += [item['adj'], "", item['noun'] + ".", "", ""]
        times += [3 * ms100, 2 * ms100, 3 * ms100, 10 * ms100, 2 * ms100]
        if stage == "train":
            triggers += [0] * 5
        else:
            triggers += [item['trigger_base'] + 2, 0, item['trigger_base'] + 1, 0, item['ItemExpID']]

        show_seq(words, times, triggers, "%s\t%s\t%d" % (dlg_dict['Subject ID'], item['Item'], countdown))
        logging.flush()

text.text = "This is the end of this part of the study.\n\nPlease wait for the experimenter."
wait_for_space()

print('Overall, %i frames were dropped.' % self.win.nDroppedFrames)

core.quit()
