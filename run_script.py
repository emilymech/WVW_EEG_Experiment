from wvw_eeg.experiment import Experiment


def main():
    experiment = Experiment()

    # Setup
    experiment.set_specs()
    experiment.set_win()
    experiment.set_text()
    experiment.set_kb_mouse()
    experiment.set_exit_proc()
    experiment.set_ver()
    experiment.make_log()
    experiment.make_gui()

    # Stimuli

    # Experiment
    experiment.present_gui()


main()

