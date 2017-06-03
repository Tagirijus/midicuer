# Program for generating best midi tempo automation with given cuepoints
#
# Author: Manuel Senfft (www.tagirijus.de/en)
# github: https://github.com/Tagirijus/midicuer
#
#
# Mainly this programm gets input from the user and calculates either the bar with the given bpm
# or the most perfect bpm with the given beat - according to previous cuepoint-entries.
#
# One of the core functions is the Cue_Class.calcBpm() function. It iters through most possibilities from the
# previous cuepoint, calculates length in milliseconds for every step (Cue_Class.stepsize) according to the actual
# bpm which is calculated with Cue_Class.iterBpm() from previous to actual cuepoint. It also calculates the actual
# bar for every testing step with Cue_Class.calcBar() and stops, if the bar is correct (the user input bar).
#
# I have to confess that it's hard to describe and this really may not be the best solution now, since it's mostly
# like trial and error. Maybe I (or other people) will find a better solution and support this project!



import pygame, cmd, os, math
from time import sleep
from midiutil.MidiFile import MIDIFile
from tabulate import tabulate

# get the actual path to the python script - for relative loading of the metronome sounds
path_to_project = os.path.dirname(os.path.realpath(__file__))


# functions


# midi file

def SaveIt(out_file):
	'Saves the midi data into the [out_file]'
	out = open(out_file, 'wb')
	Midi.writeFile(out)
	out.close()

def AddTempo(bar, tempo):
	'Adds a new tempo event with the given [tempo] at the given [bar]'
	Midi.addTempo(track, bar, tempo)

def AddNote(bar):
	'Adds a predefined note at the given [bar]'
	Midi.addNote(track, 1, 60, bar, 1, 100)


# sound generation

def BpmToSec(bpm):
	'Returns seconds which will pass for one beat with the given [bpm]'
	return 60.0 / bpm

def Beep(which=1):
	'Makes a single beep. [which=1] is default and beeps high, [which!=1] beeps low'
	if which == 1:
		hi.play(maxtime=0)
	else:
		lo.play(maxtime=0)

def Metronome(bpm=120, bars=2, beats=4, length=4):
	'Starts a metronome with the tempo [bpm] for the length of N [bars] and the time signature of [beats] / [length]'
	boing = True
	b = 1
	bar = 0
	factor = length / 4.0
	bpm = int( (length / 4.0) * bpm )
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


# other stuff

def drange(start, stop, step=1):
	'Iter generator like xrange or range, but with the ability to use decimal numbers for the [step]'
	if '.' in str(step):
		decimals = len(str(step).split('.')[1])
	else:
		decimals = 1
	r = start
	out = []

	if stop > start:
		while r < stop:
			out.append( round(r, decimals) )
			r += step
		return out
	elif stop < start:
		while r > stop:
			out.append( round(r, decimals) )
			r -= step
		return out

def retMs(time):
	'Converts a string with the format [MM:SS] or [MM:SS:d] to an integer for milliseconds'
	if time.count(':') == 1:
		parts = time.split(':')
		try:
			MM = int(parts[0])
			SS = int(parts[1])
			MS = 0
		except Exception, e:
			return -1
	elif time.count(':') == 2:
		parts = time.split(':')
		try:
			MM = int(parts[0])
			SS = int(parts[1])
			MS = int(parts[2])
		except Exception, e:
			return -1
	else:
		return -1
	return MS + (SS*1000) + (MM*60000)

def retTime(ms):
	'Converts an integer which contains milliseconds to a readable time string with the format [MM:SS:d]'
	MM = ms / 60000
	SS = (ms % 60000) / 1000
	MS = (ms % 60000) % 1000
	if MM < 10:
		MM = '0' + str(MM)
	else:
		MM = str(MM)
	if SS < 10:
		SS = '0' + str(SS)
	else:
		SS = str(SS)
	if MS < 100 and MS > 9:
		MS = '0' + str(MS)
	elif MS < 10:
		MS = '00' + str(MS)
	else:
		MS = str(MS)
	return MM + ':' + SS + ':' + MS


# classes

class Cues_Class(object):
	def __init__(self):
		# time in ms, cuepoint-name, tempo, bar, calculate
		self.entries = []
		self.beats_per_bar = 4
		self.beat_length = 4
		self.stepsize = 0.03125

	def load(self, filename):
		'Loads a project file'
		ret = []
		if os.path.isfile(filename):
			out = open(filename, 'r')
			data = out.readlines()
			for cx, x in enumerate(data):
				data[cx] = x.rstrip()
			out.close()
			try:
				self.beats_per_bar = int(data[0].split(',')[0])
				self.beat_length = int(data[0].split(',')[1])
				self.stepsize = float(data[0].split(',')[2])
			except Exception, e:
				print 'Error loading file. Content maybe corrupt.'
			for x in data[1:]:
				tmp = []
				try:
					tmp.append( int(x.split(',')[0]) ) 		# time
					tmp.append( x.split(',')[1] )			# name
					tmp.append( int(x.split(',')[2]) )		# tempo
					tmp.append( float(x.split(',')[3]) )	# bar
					tmp.append( x.split(',')[4] )			# calculate
					ret.append( tmp )
				except Exception, e:
					print 'Error loading file. Content maybe corrupt.'
			self.entries = ret
			self.update()
			print 'Loaded', filename

	def export(self, filename):
		'Exports the project to a MIDI-file'
		# entries must contain stuff
		if len(self.entries) == 0:
			return

		# reset the midi variable
		global Midi
		Midi = MIDIFile(1)
		Midi.addTrackName(track, time_start, 'MIDI Cuer')

		# the great export loop
		all_beats = int( math.ceil( self.entries[len(self.entries)-1][3] ) )
		out = {}
		for x in xrange(1, len(self.entries)):
			out.update( self.calcIterBeats( self.entries[x-1][3], self.entries[x][3], self.entries[x-1][2], self.entries[x][2], self.stepsize ) )


		for x in sorted(out.iterkeys()):
			AddTempo(x, out[x])
			if self.BeatExists(x):
				AddNote(x)

		# de-comment following 3 lines for debugging during output
		# print 'Debuggin:'
		# for x in sorted(out):
		# 	print x, out[x]

		SaveIt(filename)

	def save(self, filename):
		'Saves the project to [filename]'
		content = str(self.beats_per_bar) + ',' + str(self.beat_length) + ',' + str(self.stepsize) + '\n'
		for x in self.entries:
			content += ','.join(str(y) for y in x) + '\n'
		out = open(filename, 'w')
		out.write(content)
		out.close()
		print 'Saved to', filename

	def update(self):
		'Sorts and updates the self.entries variable'
		self.entries.sort(key=lambda x: x[0])
		for x in xrange(1,len(self.entries)):

			# calculate bar
			if self.entries[x][4] == 'bar':
				self.entries[x][3] = self.calcBar(x)

			# calculate bpm
			elif self.entries[x][4] == 'bpm':
				self.entries[x][2] = self.calcBpm(x)

	def show(self):
		'Prints out all cuepoints in a readable table'
		print
		print 'Time signature: ' + str(self.beats_per_bar) + '/' + str(self.beat_length)
		print
		out = []
		for cx, x in enumerate(self.entries):
			tmp = []
			tmp.append( retTime(x[0]) ) # time
			tmp.append( x[1] ) # name
			tmp.append( x[2] ) # bpm
			tmp.append( self.BarToReadableBar( x[3] ) ) # bar
			tmp.append( x[4] ) # calculate
			out.append(tmp)
		head = ['Time [MM:SS:MS]', 'Cuepoint', 'BPM', 'Bar-Beat', 'Calc']
		print tabulate(out, head)

	def BeatExists(self, beat):
		'Returns true if [beat] exists in the self.entries variable'
		idx = -1
		for cx, x in enumerate(self.entries):
			if beat == x[3]:
				idx = cx
		# return empty list if nothing found
		if idx < 0:
			return []
		# else singleton list with index inside
		else:
			return [idx]

	def TimeExists(self, ms):
		'Returns true if [ms] exists in the self.entries variable'
		idx = -1
		for cx, x in enumerate(self.entries):
			if ms == x[0]:
				idx = cx
		# return empty list if nothing found
		if idx < 0:
			return []
		# else singleton list with index inside
		else:
			return [idx]

	def EditOrAdd(self, time):
		'Adds a new entry or edits an existing one - or lets the user delete the selected entry'
		# getting default name and ask for delete
		if self.TimeExists(time) and time != 0:
			the_name = self.entries[ self.TimeExists(time)[0] ][1]
			delme = raw_input(the_name + ' delete [no] > ')
			if delme:
				if delme == 'y' or delme == 'yes':
					self.entries.pop( self.TimeExists(time)[0] )
					return
		elif self.TimeExists(time) and time == 0:
			the_name = self.entries[0][1]
			delme = raw_input(the_name + ' delete [no] > ')
			if delme:
				if delme == 'y' or delme == 'yes':
					self.entries.pop( 0 )
					return
		else:
			the_name = ''

		# editing time if it exists
		if self.TimeExists(time):
			actual = self.TimeExists(time)[0]
		else:
			actual = False
		if actual and time != 0:
			new_time_bool = False
			while not new_time_bool:
				new_time = raw_input('Time [' + retTime( self.entries[ actual ][0] ) + '] > ')
				try:
					if new_time:
						new_time = retMs(new_time)
						rel_time = raw_input('Changing following entries relatively [yes] ? ')
						if rel_time == 'n' or rel_time == 'no':
							# changing just the time for the acutal entry; must be between previous and following
							if len(self.entries) > actual:
								if new_time > self.entries[ actual-1 ][0] and new_time < self.entries[ actual+1 ][0]:
									self.entries[ actual ][0] = new_time
									self.update()
									time = new_time
									new_time_bool = True
								else:
									print 'Time has to be between previous and following entry.'
							elif len(self.entries) == actual:
								if new_time > self.entries[ actual-1 ][0]:
									self.entries[ actual ][0] = new_time
									self.update()
									time = new_time
									new_time_bool = True
								else:
									print 'Time has to be over the previous time.'
						else:
							# changing the time relatively for all following entries
							if len(self.entries) >= actual:
								diff = new_time - self.entries[actual][0]
								for x in xrange(actual,len(self.entries)):
									self.entries[x][0] += diff
								self.update()
								time = new_time
								new_time_bool = True
					else:
						new_time_bool = True
				except Exception, e:
					print 'No valid time format.'

		# editing or adding entry
		if self.TimeExists(0) or time == 0:
			cuepoint = raw_input(retTime(time) + ' name [' + the_name +  '] > ')
			if not cuepoint:
				cuepoint = the_name

			# add default entry: time, name, tempo, bar, calculate
			if not self.TimeExists(time):
				self.entries.append([time, cuepoint, tempo_default, 0.0, 'bar'])
				self.update()
				actual = self.TimeExists(time)[0]
			elif self.TimeExists(time) and time == 0:
				self.entries[0][1] = cuepoint
			else:
				self.entries[ self.TimeExists(time)[0] ][1] = cuepoint

			# only name and BPM for the first entry
			if time == 0:
				tempo_bool = False
				while not tempo_bool:
					tempo = raw_input(cuepoint + ' > tempo [' + str(tempo_default) + '] > ')
					if tempo:
						try:
							self.entries[0][2] = int(tempo)
							tempo_bool = True
						except Exception, e:
							print 'Please insert integer.'
					else:
						self.entries[0][2] = tempo_default
						tempo_bool = True
				self.update()
				return

			# edit entries over 0
			calc = raw_input(cuepoint + ' > calculate bpm or bar [' + self.entries[actual][4] + '] > ')
			if calc:
				if calc == 'bpm' or calc == 'bar':
					self.entries[actual][4] = calc


			# chose what shall be entered and what calculated

			#
			# calculate the bar
			#
			if self.entries[actual][4] == 'bar':
				tempo_bool = False
				while not tempo_bool:
					tempo = raw_input(cuepoint + ' > tempo [' + str(self.entries[actual-1][2]) + '] > ')
					if tempo:
						try:
							self.entries[actual][2] = int(tempo)
							tempo_bool = True
						except Exception, e:
							print 'Invalid tempo.'
					else:
						self.entries[actual][2] = self.entries[actual-1][2]
						tempo_bool = True
				self.update()
				return

			#
			# calculate the tempo
			#
			elif self.entries[actual][4] == 'bpm':
				bar_bool = False
				while not bar_bool:
					bar = raw_input(cuepoint + ' > bar [' + str(self.BarToReadableBar(self.entries[actual][3])) + '] > ')
					try:
						bar = float(bar)
						if bar <= self.entries[actual-1][3]:
							print 'Bar must be higher than in the previous cue.'
						else:
							self.entries[actual][3] = bar
							bar_bool = True
					except Exception, e:
						print 'Invalid bar. Maybe bar is below the bar of the previous cue?'
				self.update()
		else:
			print 'Add cuepoint at 00:00:000 first, please.'

	def options(self):
		'Enters the settings / options menu'
		print
		print '(1) Time signatur'
		print '(2) Stepsize'
		print '(3) Start-Tempo + Tempo for entries with bar-calculation'
		print '(4) Back'
		user = raw_input('\noptions > ')
		if user == '1':
			userr = raw_input('options > Time signature > Beats [' + str(self.beats_per_bar) + '] > ')
			if userr:
				try:
					userr = int(userr)
					if userr > 0:
						self.beats_per_bar = userr
				except Exception, e:
					print 'Beats invalid or unchanged.'
			userrr = raw_input('options > Time signature > Note value [' + str(self.beat_length) + '] > ')
			if userr:
				try:
					userrr = int(userrr)
					if userrr > 0:
						self.beat_length = userrr
				except Exception, e:
					print 'Note value invalid or unchanged.'
		elif user == '2':
			print '\nStepsize is the duration for one tempo event, while 1 is equal to a quarter note.'
			userr = raw_input('options > Stepsize [' + str(self.stepsize) + '] > ')
			if userr:
				try:
					userr = float(userr)
					if userr > 0:
						self.stepsize = userr
				except Exception, e:
					print 'Stepsize invalid or unchanged.'
		elif user == '3':
			print '\nChanges the tempo of the first entry and of A L L entries, which have the calcultion set to "bar".'
			print 'Set if you really sure, otherwise press enter without typing a value.'
			userr = raw_input('options > Tempochange > ')
			if userr:
				try:
					userr = int(userr)
					if userr > 0:
						for cx, x in enumerate(self.entries):
							if x[4] == 'bar':
								self.entries[cx][2] = userr
				except Exception, e:
					pass

	def calcBeatToMs(self, bpm, beat=False):
		'Calculates how much milliseconds are [beat]s with the actual [bpm]'
		if not beat:
			beat = self.stepsize
		if bpm > 0:
			factor = (60.0 / bpm) * 1000
		else:
			print 'BPM must be over 0.'
			exit() ### DEBUG
			return 0
		return factor*beat

	def calcBpm(self, entry):
		'Iterates through all possible bpms for self.entries[ [entry] ] and tries to find best bpm so that the given beat at the gien timecode fits'
		if entry > 0 and entry < len(self.entries):
			this_tempo = self.entries[entry][2]
			self.entries[entry][2] = self.entries[entry-1][2]
			do_bar = self.entries[entry][3]
			this_bar = self.calcBar(entry)

			# make bpm slower
			if this_bar > do_bar:
				while this_bar > do_bar:
					if self.entries[entry][2]-1 == 0:
						print 'Impossible to find correct BPM for this entry:', self.entries[entry][0], self.entries[entry][1] + '.'
						print 'Resetting it to "find bar" with the tempo of previous entry.'
						self.entries[entry][2] = self.entries[entry-1][2]
						self.entries[entry][3] = self.calcBar(entry)
						self.entries[entry][4] = 'bar'
						return self.entries[entry][2]
					self.entries[entry][2] -= 1
					this_bar = self.calcBar(entry)
				return self.entries[entry][2]

			# make bpm faster
			elif this_bar < do_bar:
				while this_bar < do_bar:
					self.entries[entry][2] += 1
					this_bar = self.calcBar(entry)
				return self.entries[entry][2]

			# bpm already fits
			else:
				return this_tempo
		else:
			if len(self.entries) > 0:
				return self.entries[0][2]
			else:
				return tempo_default

	def calcBar(self, entry):
		'Simply calculates the bar for self.entries[ [entry] ] according to previous entries, positions and bpms'
		if entry > 0 and entry < len(self.entries):
			pos_ms = self.entries[entry-1][0]
			pos_bt = self.entries[entry-1][3]
			iterme = self.calcIterBpm( self.entries[entry-1][0], self.entries[entry][0], self.entries[entry-1][2], self.entries[entry][2] )
			while pos_ms <= self.entries[entry][0]:
				pos_ms += self.calcBeatToMs( iterme[int(pos_ms)] )
				if pos_ms <= self.entries[entry][0]:
					pos_bt += self.stepsize
			return pos_bt
		else:
			return 0.0

	def calcIterBpm(self, start_ms, end_ms, start_bpm, end_bpm):
		'Returns a dict with an uniformly distributed list over another. List2 which goes from [start_bpm] to [end_bpm] is distributed over List1 which goes from [start_ms] to [end_ms]. Result will be accessed like  out[list1_position] = list2_position'
		if start_bpm > end_bpm:
			end_bpm -= 1
		else:
			end_bpm += 1
		dif_ms = abs( start_ms - end_ms )
		dif_bt = abs( start_bpm - end_bpm )
		if dif_bt == 0:
			dif_bt = 1
		dif_am = float(dif_ms) / float(dif_bt)
		dif_am_c = dif_am
		out = {}
		step = 1 if start_bpm < end_bpm else -1
		bpms = range(start_bpm, end_bpm, step)
		possible = len(bpms)
		actual = start_bpm if possible == 0 else 0
		new_bpm = start_bpm
		for cx, x in enumerate(xrange(start_ms,end_ms+1)):
			if cx >= dif_am_c:
				dif_am_c += dif_am
				if possible > 0 and actual < possible-1:
					actual += 1
					new_bpm = bpms[actual]
			out[x] = new_bpm
		return out

	def calcIterBeats(self, start_beat, end_beat, start_bpm, end_bpm, stepsize):
		'Returns a dict with an uniformly distributed list over another. List2 which goes from [start_bpm] to [end_bpm] is distributed over List1 which goes from [start_beat] to [end_beat]. Result will be accessed like  out[list1_position] = list2_position'
		if start_bpm < end_bpm:
			end_bpm += 1
		else:
			end_bpm -= 1
		iterme = drange(start_beat,end_beat+stepsize,stepsize)
		dif_beat = len( iterme )
		dif_bt = abs( start_bpm - end_bpm )
		if dif_bt == 0:
			dif_bt = 1
		dif_am = float(dif_beat) / float(dif_bt)
		dif_am_c = dif_am
		out = {}
		step = 1 if start_bpm < end_bpm else -1
		bpms = range(start_bpm, end_bpm, step)
		possible = len(bpms)
		actual = start_bpm if possible == 0 else 0
		new_bpm = start_bpm
		for cx, x in enumerate( iterme ):
			if cx >= dif_am_c:
				dif_am_c += dif_am
				if possible > 0 and actual < possible-1:
					actual += 1
					new_bpm = bpms[actual]
			out[x] = new_bpm
		return out

	def BarToReadableBar(self, bar):
		'Converts the absolute midi bar position (e.g. 3.0) to a readable string with the format bar-beat like 1-3.0'
		single_beat = 4.0 / self.beat_length
		beats_in_bar = single_beat * self.beats_per_bar
		actual_bar  = int( ( bar - ( bar % beats_in_bar) ) / beats_in_bar ) + 1
		actual_beat = ( bar % beats_in_bar ) + 1
		return str(actual_bar) + '-' + str(actual_beat) + ' (' + str(bar) + ')'







# start program

# declare standard midi variables
track = 0
time_start = 0
tempo_default = 120


# init pygame mixer stuff - used for the metronome only
pygame.mixer.pre_init(44100,-16,2, 1024)
pygame.mixer.init()
hi = pygame.mixer.Sound(path_to_project + '/metronome/high.wav')
lo = pygame.mixer.Sound(path_to_project + '/metronome/low.wav')


# generate the Cues variable
Cues = Cues_Class()


# real program starts here
print
print 'MIDI Cuer program'

run = True
while run:
	# first input from user aquired
	user = raw_input('\n> ')

	# deb: used for developing purpose only - no feature for the actual user in the end
	if user[0:3] == 'deb':
		print 'Debugging ...'

	# edit / add entry
	if ':' in user:
		if not retMs(user) == -1:
			Cues.EditOrAdd(retMs(user))

	# show
	if user == 's' or user == 'show':
		Cues.show()

	# metronome
	if user[0:3] == 'met' or user[0:2] == 'm ':
		args = user.split(' ')
		if len(args) == 3:
			try:
				bpm = float(args[1])
				bars = int(args[2])
				Metronome(bpm, bars, Cues.beats_per_bar, Cues.beat_length)
			except Exception, e:
				print 'Invalid arguments. User "met X Y" or "m X Y", where X=BPM and Y=bars.'

	# options / settings
	if user == 'o' or user == 'options':
		Cues.options()

	# new file / project
	if user == 'n' or user == 'new':
		userr = raw_input('Seriously? ')
		if userr == 'y' or userr == 'yes':
			Cues.entries = []
			Cues.beats_per_bar = 4
			print 'New file / project started.'

	# load and save and export
	if user[0:4] == 'load':
		if '.midicuer' in user:
			Cues.load(user[5:])
		else:
			Cues.load(user[5:] + '.midicuer')
	elif user[0:4] == 'save':
		if '.midicuer' in user:
			Cues.save(user[5:])
		else:
			Cues.save(user[5:] + '.midicuer')
	elif user[0:6] == 'export':
		if '.mid' in user:
			Cues.export(user[7:])
		else:
			Cues.export(user[7:] + '.mid')

	# help
	if user == 'h' or user == 'help':
		head = ['command', 'result']
		cont = [
			['[MM:SS] / [MM:SS:MS]', 'adds / edits entry'],
			['n / new', 'new file / project'],
			['s / show', 'shows the cue list'],
			['met/m X Y', 'start a metronome with BPM X for Y bars'],
			['o / options', 'options / settings of the project'],
			['export *', 'export to file *.mid'],
			['load *', 'loads file *.midicuer'],
			['save *', 'saves file *.midicuer'],
			['h / help', 'this help text here'],
			['e / end / exit', 'quits the program']
		]
		print tabulate(cont, head)

	# exit the program
	if user == 'e' or user == 'end' or user == 'exit':
		run = False

print