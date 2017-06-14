"""
A programm for generaing a MIDI tempo automation based on cue points.

This tool is an approach to generate a midi file (*.mid), which contains
the perfect tempo automation according to given cue points for scoring
film music.

Author: Manuel Senfft (www.tagirijus.de)
"""

import argparse
from general import midicuer
from npy_gui import npy_gui
import os


def main():
    """Run the programm."""
    # arguments for the programm
    args = argparse.ArgumentParser(
        description=(
            'A programm for generaing a MIDI tempo automation based on cue points.'
        )
    )

    args.add_argument(
        'file',
        nargs='?',
        default=None,
        help='a .midicuer file. just enter [FILE].midicuer or just [FILE]'
    )

    args = args.parse_args()
    file = (
        '{}/{}'.format(os.getcwd(), args.file)
        if args.file is not None
        else None
    )

    app = npy_gui.MIDICuerApplication(file=file)
    app.run()


if __name__ == '__main__':
    main()
