
from wvw_eeg.setup import Setup

#  TODO - Need to test the read in stimuli function


class Stimuli(Setup):
    def __init__(self):
        super().__init__()
        self.all_items = None
        self.block = None
        self.blocks = None
        self.training = None
        self.col_names = None
        self.row_dict = None
        self.item_num = None
        self.triggers = None

    def read_in_stimuli(self):
        self.all_items = {"train": [], "block1": [], "block2": [], "block3": []}
        self.blocks = ["train", "block1", "block2", "block3"]
        with open("02.25.20 - wvw v%s.txt" % self.ver, "r") as f:
            self.col_names = f.readline().strip().split("\t")
            self.item_num = 0
            self.block = 1
            training = 1

            for row in f:
                self.item_num += 1
                self.row_dict = {}
                row_parts = row.strip().split("\t")
                for col in range(len(row_parts)):
                    self.row_dict[self.col_names[col]] = row_parts[col]

                words = self.row_dict['context'].split(" ")

                self.row_dict['context'] = words
                self.row_dict['ItemExpID'] = int(self.row_dict['ItemExpID'])
                self.row_dict['cond'] = int(self.row_dict['cond'])
                self.row_dict['triggers'] = self.triggers

                if training:
                    if self.row_dict["type"] == "train":
                        self.all_items["train"].append(self.row_dict)
                        continue
                    else:
                        training = 0
                        self.item_num = 1
                if self.item_num == 81:  # need to change this number to how many items will be per block
                    self.item_num = 1
                    self.block += 1
                self.all_items[self.blocks[self.block]].append(self.row_dict)

    def read_in_triggers(self):
        pass

