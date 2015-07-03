import pygame, cmd, os, math
from time import sleep
from midiutil.MidiFile import MIDIFile
from tabulate import tabulate

path_to_project = os.path.dirname(os.path.realpath(__file__))


# functions


# midi file

def SaveIt(out_file):
	out = open(out_file, 'wb')
	Midi.writeFile(out)
	out.close()

def AddTempo(bar, tempo):
	Midi.addTempo(track, bar, tempo)

def AddNote(bar):
	Midi.addNote(track, 1, 60, bar, 1, 100)


# sound generation

def BpmToSec(bpm):
	return 60.0 / bpm

def Beep(which=1):
	if which == 1:
		hi.play(maxtime=0)
	else:
		lo.play(maxtime=0)

def Metronome(bpm=120, bars=2, beats=4, length=4):
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
		if '.' in str(step):
			decimals = len(str(step).split('.')[1])
		else:
			decimals = 1
		r = start
		out = []
		while r < stop:
			out.append( round(r, decimals) )
			r += step
		return out

def retMs(time):
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
		self.stepsize = 0.0625

	def load(self, filename):
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

		print 'Debuggin:'
		for x in sorted(out):
			print x, out[x]

		SaveIt(filename)

	def save(self, filename):
		content = str(self.beats_per_bar) + ',' + str(self.beat_length) + ',' + str(self.stepsize) + '\n'
		for x in self.entries:
			content += ','.join(str(y) for y in x) + '\n'
		out = open(filename, 'w')
		out.write(content)
		out.close()
		print 'Saved to', filename

	def update(self):
		self.entries.sort(key=lambda x: x[0])
		for x in xrange(1,len(self.entries)):

			# calculate bar
			if self.entries[x][4] == 'bar':
				self.entries[x][3] = self.calcBar(x)

			# calculate bpm
			elif self.entries[x][4] == 'bpm':
				self.entries[x][2] = self.calcBpm(x)

	def show(self):
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
		idx = -1
		for cx, x in enumerate(self.entries):
			if beat == x[3]:
				idx = cx
		if idx == -1:
			return False
		else:
			return idx if idx > 0 else True

	def TimeExists(self, ms):
		idx = -1
		for cx, x in enumerate(self.entries):
			if ms == x[0]:
				idx = cx
		if idx == -1:
			return False
		else:
			return idx if idx > 0 else True

	def EditOrAdd(self, time):
		# getting default name and ask for delete
		if self.TimeExists(time) and time != 0:
			the_name = self.entries[ self.TimeExists(time) ][1]
			delme = raw_input(the_name + ' delete [no] > ')
			if delme:
				if delme == 'y' or delme == 'yes':
					self.entries.pop( self.TimeExists(time) )
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
		actual = self.TimeExists(time)
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
			elif self.TimeExists(time) and time == 0:
				self.entries[0][1] = cuepoint
			else:
				self.entries[ self.TimeExists(time) ][1] = cuepoint

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
			calc = raw_input(cuepoint + ' > calculate [' + self.entries[actual][4] + '] > ')
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
					bar = raw_input(cuepoint + ' > bar [' + str(self.entries[actual][3]) + '] > ')
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
		single_beat = 4.0 / self.beat_length
		beats_in_bar = single_beat * self.beats_per_bar
		actual_bar  = int( ( bar - ( bar % beats_in_bar) ) / beats_in_bar ) + 1
		actual_beat = ( bar % beats_in_bar ) + 1
		return str(actual_bar) + '-' + str(actual_beat) + ' (' + str(bar) + ')'







# start program

track = 0
time_start = 0
tempo_default = 120


# init stuff
pygame.mixer.pre_init(44100,-16,2, 1024)
pygame.mixer.init()
hi = pygame.mixer.Sound(path_to_project + '/metronome/high.wav')
lo = pygame.mixer.Sound(path_to_project + '/metronome/low.wav')

Cues = Cues_Class()


# do stuff
print
print 'MIDI Cuer program'

run = True
while run:
	user = raw_input('\n> ')

	# debug
	if user[0:3] == 'deb':
		try:
			args = user.split(' ')
			if len(args) > 2:
				bts = float(args[2])
			else:
				bts = False
			print 'Debug:', Cues.calcBeatToMs(int(args[1]), bts)
		except Exception, e:
			print 'Error'

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