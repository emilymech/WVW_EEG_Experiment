
from wvw_eeg.setup import Setup

#  TODO - Need to test the read in stimuli function


class Stimuli(Setup):
    def __init__(self):
        super().__init__()
        self.all_items = None
        self.blocks = None

        self.triggers = None

    def read_in_stimuli(self):
        self.all_items = {"train": [], "block1": [], "block2": [], "block3": []}
        self.blocks = ["train", "block1", "block2", "block3"]
        with open("02.25.20 - wvw v%s.txt" % self.ver, "r") as f:
            col_names = f.readline().strip().split("\t")
            item_num = 0
            block = 1
            training = 1

            for row in f:
                item_num += 1
                row_dict = {}
                row_parts = row.strip().split("\t")
                for col in range(len(row_parts)):
                    row_dict[col_names[col]] = row_parts[col]

                words = row_dict['context'].split(" ")

                row_dict['context'] = words
                row_dict['ItemExpID'] = int(row_dict['ItemExpID'])
                row_dict['cond'] = int(row_dict['cond'])
                row_dict['triggers'] = self.triggers

                if training:
                    if row_dict["typ"] == "train":
                        self.all_items["train"].append(row_dict)
                        continue
                    else:
                        training = 0
                        item_num = 1
                if item_num == 81:
                    item_num = 1
                    block += 1
                self.all_items[self.blocks[block]].append(row_dict)

    def read_in_triggers(self):
        pass

