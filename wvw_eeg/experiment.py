import time
from random import random
from psychopy import event, logging, core

from wvw_eeg.stimuli import Stimuli

# passed to show_seq:  , words, times, triggers, to_log=""
# [""], [10 * self.ms100], [0]


class Experiment(Stimuli):
    def __init__(self):
        super().__init__()
        self.countdown = None
        self.words = None
        self.times = None
        self.to_log = None
        self.datetime = None
        self.msg = None
        self.current_item = None
        self.expect = None
        self.blocks = None

    def send_udp(self):
        self.UDPSock.sendto(self.msg.encode(), self.addr)

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

    def show_seq(self):
        self.times = [10 * self.ms100]
        assert len(self.words) == len(self.times)
        current_thr = 0
        self.current_item = -1
        for frameN in range(int(sum(self.times))):
            if frameN == current_thr:
                self.current_item += 1
                current_thr += int(self.times[self.current_item])
                self.text.text = self.words[self.current_item]

                if self.words[self.current_item] != "" or self.triggers[self.current_item] != 0:
                    self.datetime = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.msg = "%s\t%s\t%d\t%s" % (self.datetime, self.to_log,
                                                   self.triggers[self.current_item],
                                                   self.words[self.current_item])
                    self.win.logOnFlip(level=logging.EXP, msg=self.msg)

                self.win.flip()
                self.send_eeg_trig()
            else:
                self.win.flip()

    def send_eeg_trig(self):
        if not self.triggers or not self.EEG:
            return
        self.port.setData(self.triggers)
        core.wait(0.0005)
        self.port.setData(0)

    def plausibility(self):
        pass

    def expected(self):  # need to define expect
        self.text.text = "On a scale of 1-10, how much did you expect to see the last word in the sentence?"

        if self.triggers[self.current_item] != 0:
            self.datetime = time.strftime('%Y-%m-%d %H:%M:%S')
            self.msg = "%s\t%s\t%d\t%s" % (self.datetime, self.to_log,
                                      self.triggers[self.current_item],
                                      self.expect[self.current_item])
            self.win.logOnFlip(level=logging.EXP, msg=self.msg)

            self.win.flip()
        else:
            self.win.flip()

    def present_experiment(self):
        self.countdown = 0
        for block in self.blocks:
            self.countdown += len(self.all_items[block])

            items = self.all_items[block]
            if block == "train":
                self.text.text = "Training session.\n\nPlease press SPACE to proceed."
            elif block == "block1":
                self.text.text = "End of the training session.\n\nPlease wait for the experimenter."
                self.wait_for_space()
                self.text.text = "The main part of the study.\n\nPlease press SPACE to proceed."
            else:
                self.text.text = "Time for a break.\n\nPlease press SPACE when you are ready."
            self.wait_for_space()

            for item in items:
                self.countdown -= 1
                self.send_udp()
                self.show_seq()
                self.expected()
                self.wait_for_space()
                self.plausibility()
                self.wait_for_space()
                self.words = ["", "+++", ""]
                self.times = [10 * self.ms100, 5 * self.ms100, round((4.0 + random() * 4.0) * self.ms100)]
                self.triggers = item[self.triggers]  # this needs to be fixed

                for word_num in range(len(item['context'])):
                    self.words += [item['context'][word_num], ""]
                    self.times += [3 * self.ms100, 2 * self.ms100]
                    self.triggers += [item['triggers'][word_num], 0]
                self.words += [item['adj'], "", item['noun'] + ".", "", ""]
                self.times += [3 * self.ms100, 2 * self.ms100, 3 * self.ms100, 10 * self.ms100, 2 * self.ms100]
                if block == "train":
                    self.triggers += [0] * 5
                else:
                    self.triggers += [item['trigger_base'] + 2, 0, item['trigger_base'] + 1, 0, item['ItemExpID']]

                self.show_seq()
                logging.flush()

        self.text.text = "This is the end of this part of the study.\n\nPlease wait for the experimenter."
        self.wait_for_space()

        print('Overall, %i frames were dropped.' % self.win.nDroppedFrames)

        core.quit()
