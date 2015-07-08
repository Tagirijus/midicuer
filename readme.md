MIDI Cuer tool for filmmusic composers
======================================

Short description
-----------------

This tool is an approach to generate a midi file (*.mid), which contains the perfect tempo automation according to given cue points.


#Problem
The film composer gets a movie scene. This scene has important things happening at an exact timecode. For example the screen is black and at timecode 00:10:000 (format is MM:SS:d) the first picture appears and the music has to start here. At 00:13:276 maybe an explosion happens and the music has to increase its tempo and get very action like. At 00:30:754 everything gets calm again and the music has to slow down as well.

With these so called cue points the composer has to find the best tempo and compose the music such that it fits the scene. Unfortunately music is build up in beats and bars which have different lengths depending on the tempo. Some music software sequencers already have tools which let the composer chose on which timecode which bar will be.But not all sequencers. This is where this tool comes in.


#Solution
The idea is that the user gives the program all mandatory cue points (the timecode points) as an input. Then he can choose on each cuepoint whether the bar shall be computed according to the given tempo or the tempo shall be computed which is needed to reach the bar the user chose. After that the program exports a midifile (*.mid) which contains the cuepoints as a single note and the overall tempo changes as a tempo automation. Every host should be able to import this midi file or just the tempo automation if wished.


#Usage
According to the upper example the usage of the program could be like this (typing 'h' or 'help' shows possible commands):

First we have to add the initial cuepoint at 00:00:000:

	> 0:0
	00:00:000 name [] > Start
	Start > tempo [120] >

	>

In this example we added a cuepoint at 00:00:000 by just typing in 0 minutes and 0 seconds in the format "M:S". After that we chose the name 'Start' for this first cuepoint and we used the default tempo by not entereing a tempo. The default values are always shown in brackets.

Now to the real first cuepoint:

	> 0:10
	00:10:000 name [] > First scene
	First scene > calculate [bar] >
	First scene > tempo [120] >

We added a cuepoint at 00:10:000 by entering 0 minutes and 10 seconds. The name for this cuepoint is 'First scene'. The caculation mode ('bar') and tempo are at default.

The next cuepoint:

	> 00:13:276
	00:13:276 name [] > Explosion
	Explosion > calculate [bar] >
	Explosion > tempo [120] >

Now we added the next cuepoint by entering minutes, seconds AND milliseconds.

Finally the last cuepoint:

	> 00:30:754
	00:30:754 name [] > Calm down
	Calm down > calculate [bar] >
	Calm down > tempo [120] >

You'll get the idea.

Now we can show the first result in a table, by entering 'show' or 's':

	> s

	Time signature: 4/4

	Time [MM:SS:MS]    Cuepoint       BPM  Bar-Beat             Calc
	-----------------  -----------  -----  -------------------  ------
	00:00:000          Start          120  1-1.0 (0.0)          bar
	00:10:000          First scene    120  6-1.0 (20.0)         bar
	00:13:276          Explosion      120  7-3.5 (26.5)         bar
	00:30:754          Calm down      120  16-2.4375 (61.4375)  bar

The program computes the bars and beats for every cuepoint according to the given tempo at this point. The number in parentheses is the absolute beat. The number before that is an approach to display this absolute beat in a readable bar-beat format according to the given time signature (you can change time signature and other stuff by entering 'o' or 'options').

We can now change a different tempo for the beginning. The scene will contain action, so a faster tempo would be nice. We can easily change the tempo for one cue at a time the following way:

	> 0:0
	Start delete [no] >
	00:00:000 name [Start] >
	Start > tempo [120] > 160

0:0 selects the first cuepoint. Deletion is not wanted so pressing enter will get the default value which is 'no' here: nothing will be delted. The name can stay as it is. The Tempo: here we go. 120 will be replaced by 160. changing the next cuepoints tempo:

	> 0:10
	First scene delete [no] >
	Time [00:10:000] >
	00:10:000 name [First scene] >
	First scene > calculate [bar] >
	First scene > tempo [160] > 160

Chosing 0:10, no deletion. Then we could change the time for this current cuepoint (maybe the client sent a new cut to the composer? this is where this program can get very handy, since the composition may just need a new tempo-automation, while the composition can stay the same or similar!). We'll use the same time for now, the same name and the same calculation mode. Only the tempo will be changed to 160 now. Let's do it for the other cuepoints as well and look at the new table:

	> s

	Time signature: 4/4

	Time [MM:SS:MS]    Cuepoint       BPM  Bar-Beat            Calc
	-----------------  -----------  -----  ------------------  ------
	00:00:000          Start          160  1-1.0 (0.0)         bar
	00:10:000          First scene    160  7-3.625 (26.625)    bar
	00:13:276          Explosion      160  9-4.3125 (35.3125)  bar
	00:30:754          Calm down      160  21-2.875 (81.875)   bar

We can see that the first important cuepoint already is at a very uncommon bar-beat. The program can help now:

	> 0:10
	First scene delete [no] >
	Time [00:10:000] >
	00:10:000 name [First scene] >
	First scene > calculate [bar] > bpm
	First scene > bar [26.625] > 28

We choose the cuepoint, do not delete it, use the same timecode, same name, but then we choose bpm so that we can type in the whished absolute beat in the next step (the ability to input bar-beat will be implemented later maybe). Then we will chose 28, since it will be in the 8th bar on beat 1. Let's see if this really worked:

	> s

	Time signature: 4/4

	Time [MM:SS:MS]    Cuepoint       BPM  Bar-Beat             Calc
	-----------------  -----------  -----  -------------------  ------
	00:00:000          Start          160  1-1.0 (0.0)          bar
	00:10:000          First scene    177  8-1.0 (28.0)         bpm
	00:13:276          Explosion      160  10-2.1875 (37.1875)  bar
	00:30:754          Calm down      160  21-4.75 (83.75)      bar

It did. The tempo was just increased to 177 bpm, but that should be no real problem for now - it's still fast and should fit to an action scene. We can see that the next cuepoint would be at bar 10 and beat 2.1875 - what a strange beat. Let's try to fix this:

	> 0:13:276
	Explosion delete [no] >
	Time [00:13:276] >
	00:13:276 name [Explosion] >
	Explosion > calculate [bar] > bpm
	Explosion > bar [37.1875] > 38

	> s

	Time signature: 4/4

	Time [MM:SS:MS]    Cuepoint       BPM  Bar-Beat             Calc
	-----------------  -----------  -----  -------------------  ------
	00:00:000          Start          160  1-1.0 (0.0)          bar
	00:10:000          First scene    177  8-1.0 (28.0)         bpm
	00:13:276          Explosion      190  10-3.0 (38.0)        bpm
	00:30:754          Calm down      160  23-1.9375 (88.9375)  bar

Now the Explosion-cuepoint would be in bar 10 on beat 3 exactly - unluckily the tempo increased even further.


#Notes
This program is still "work in progress". The midi export function is not that accurate yet and I assume that some internal calculation may not be absolutely correct at the moment. Furthermore the handling of adding cuepoints and maybe even abrupt tempochanges is difficult. The main goal of this readme text is mostly to show the idea of the program. Every help improving this program is appreciated!

Oh and you only need the pygame module for the built-in metronome. The main program should work without the module and without the metronome function.