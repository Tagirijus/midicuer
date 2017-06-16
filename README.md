This tool is an approach to generate a midi file (*.mid), which contains the perfect tempo automation according to given cue points for scoring film music.

# Problem

The film composer gets a movie scene. This scene has important things happening at an exact timecode. For example the screen is black and at timecode 00:10:000 (format is MM:SS:d) the first picture appears and the music has to start here. At 00:13:276 maybe an explosion happens and the music has to increase its tempo and get very action like. At 00:30:754 everything gets calm again and the music has to slow down as well.

With these so called cue points the composer has to find the best tempo and compose the music such that it fits the scene. Unfortunately music is build up in beats and bars which have different lengths depending on the tempo. Some music software sequencers already have tools which let the composer chose on which timecode which bar will be. But not all sequencers. This is where this tool comes in.

# Solution

The idea is that the user gives the program all important cue points (the timecode points) as an input. Then he can choose on each cue point whether the bar shall be calculated according to the given tempo or the tempo shall be calculated which is needed to reach the bar the user chose (in the given time between the previous timecode and the cue points timecode). After that the program exports a midifile (*.mid) which contains the cue points as a single note and the overall tempo changes as a tempo automation. Every host should be able to import this midi file or just the tempo automation if wished.

# Installation

To be honest: totally helpless here. I have installed my tweaked version of `npyscreen` in the system and my freelance script in my folder, which I start with `python3 run.py`, when in the folder (I made some shortcuts, of course). This is probably totally noob-alike. Maybe somebody is going to improve it some day?

The frontend is made with my tweaked version of [npyscreen](https://github.com/Tagirijus/npyscreen/tree/NotifyInput).

# Usage

When you started the programm, these keyboard shortcuts will help you:

Ctrl+X:		Opens the menu.
INSERT:		Insert a cue point.
DELETE:		Delete the selected cue point (except the first).
ENTER:		Edit the selected cue point in detail.
t:			Increase the tempo of the selected cue point by 1.
T:			Decrease the tempo of the selected cue point by 1.
b:			Increase the beat of the selected cue point by the resolution.
B:			Decrease the beat of the selected cue point by the resolution.

Everything else should be self-explaining. If not, mail me and I probably will answer quite fast.
