import pygame
from time import sleep
from midiutil.MidiFile import MIDIFile




# functions
		

# midi file

def SaveIt(out_file):
	out = open(out_file, 'wb')
	Midi.writeFile(out)
	out.close()

def ChangeTempo(time, tempo):
	Midi.addTempo(track, time, tempo)


# sound generation

def BpmToSec(bpm):
	return 60.0 / bpm

def Beep(which=1):
	if which == 1:
		hi.play(maxtime=0)
	else:
		lo.play(maxtime=0)

def Metronome(bpm=120, bars=2, beats=4):
	boing = True
	b = 1
	bar = 0
	while bar < (bars*beats):
		if b == 1:
			Beep(1)
			b += 1
		else:
			Beep(2)
			b += 1
			if b == beats+1:
				b = 1
		bar += 1
		sleep(BpmToSec(bpm))








# start program

track = 0
time = 0


# init stuff
pygame.mixer.pre_init(44100,-16,2, 1024)
pygame.mixer.init()
hi = pygame.mixer.Sound('./metronome/high.wav')
lo = pygame.mixer.Sound('./metronome/low.wav')

Midi = MIDIFile(1)
Midi.addTrackName(track, time, 'MIDI Cuer')


# do stuff
ChangeTempo(0, 120)
ChangeTempo(0.25, 140)