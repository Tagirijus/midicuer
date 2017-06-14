"""
The module for the MIDICue class.

Todo:
    Calculations do only work correctly (at least I assume, did not test), if
    timecodes lowest value is set to milliseconds (not 24, 25, ... frames).
"""

from decimal import Decimal
import json
from timecode import Timecode as Timecode_original
from midiutil.MidiFile import MIDIFile


def convert_beat(beat=Decimal('1.0')):
    """Convert musical beat to decimal beat or vice versa."""
    if beat != 0:
        return (Decimal(1) / Decimal(str(beat))) * Decimal(4)
    else:
        return Decimal('0')


class Timecode(Timecode_original):
    """Improved Timecode."""

    def tc_to_string(self, hrs, mins, secs, frs):
        """
        Fixed method for returning string of Timecode.

        In the original Timecode class this method would just have one leading
        zero for a timecode with the milliseconds framerate of 1000 milliseconds.
        So for a total of 1001 ms for a Timecode, this method would have returned
        00:00:01.01, while it should be 00:00:01.001
        """
        # check the lengths of the framerate number and generate the formating string
        fmt = '%02d:%02d:%02d%s%0{}d'.format(len(str(self._int_framerate - 1)))
        return fmt % (hrs,
                      mins,
                      secs,
                      self.frame_delimiter,
                      frs)

    def tc_to_ms(self):
        """Convert timecode to integer milliseconds."""
        if self._int_framerate > 0:
            return int(round(self.frame_number * (1000 / float(self._int_framerate))))
        else:
            return 0


class ReplacementDict(dict):
    """A dict with a __missing__ method."""

    def __missing__(self, key):
        """Return the key instead."""
        return '{' + str(key) + '}'


class MIDICue(object):
    """The object holding all the information for a film music cue point."""

    def __init__(
        self,
        cuelist=None,
        first=False,
        title='Cue point',
        comment='',
        framerate='ms',
        timecode='0',
        tempo=120,
        hold_tempo=False,
        beat=0
    ):
        """Initialize the class."""
        self.cuelist = cuelist

        self.first = first

        self.title = title
        self.comment = comment

        self._framerate = framerate

        self._timecode = Timecode(self._framerate, 0)
        self.timecode = timecode

        self.tempo = tempo

        self.hold_tempo = hold_tempo

        self.beat = beat

        # what to calculate? 'beat' or 'tempo' ?
        self.calc = 'beat'

    def __repr__(self):
        """Represent yourself."""
        return self._timecode

    def __str__(self):
        """Represent yourself as a string (Timecode: Title)."""
        return '{}: Tempo: {}, {} --- {}'.format(
            str(self.__repr__()),
            self.tempo,
            self.beat_readable(),
            self.title,
        )

    @property
    def cuelist(self):
        """Get cuelist."""
        return self._cuelist

    @cuelist.setter
    def cuelist(self, value):
        """Set cuelist."""
        self._cuelist = value

    @property
    def title(self):
        """Get title."""
        return self._title

    @title.setter
    def title(self, value):
        """Set title."""
        self._title = str(value)

    @property
    def comment(self):
        """Get comment."""
        return self._comment

    @comment.setter
    def comment(self, value):
        """Set comment."""
        self._comment = str(value)

    @property
    def timecode(self):
        """Get the timecode."""
        return self._timecode

    @timecode.setter
    def timecode(self, value):
        """Set the timecode."""
        # do not change the first cue point
        if self.first:
            return False

        v = str(value)
        v = v.replace(';', ':').replace('.', ':').split(':')

        # only one number given (frames or milliseconds)
        if len(v) == 1:
            tc = '0:0:0:{}'.format(v[0])

        # two numbers given (seconds and frames / milliseconds)
        elif len(v) == 2:
            tc = '0:0:{}:{}'.format(v[0], v[1])

        # three numbers given (minutes, seconds and frames / milliseconds)
        elif len(v) == 3:
            tc = '0:{}:{}:{}'.format(v[0], v[1], v[2])

        # four numbers given (hours, minutes, seconds and frames / milliseconds)
        elif len(v) == 4:
            tc = '{}:{}:{}:{}'.format(v[0], v[1], v[2], v[3])

        # too much given, cancel
        else:
            return False

        # convert the timecode
        add_me = Timecode(self._framerate, tc)

        # cuelist already set - check for doubled entries and shit
        if self.cuelist is not None:

            # check if given timecode exists already
            tc_exists = False if add_me == self._timecode else True
            while tc_exists:
                if add_me.frames not in [c.timecode.frames for c in self.cuelist]:
                    tc_exists = False
                else:
                    add_me.frames += 1

            self._timecode = add_me

            # and resort the list
            self.cuelist.sort()

        # cuelist not linked yet
        else:
            self._timecode = add_me

    @property
    def tempo(self):
        """Get tempo."""
        return self._tempo

    @tempo.setter
    def tempo(self, value):
        """Set tempo."""
        try:
            new_tempo = int(value)
            if new_tempo > 0:
                self._tempo = new_tempo
        except:
            pass

    def tempo_up(self):
        """Add 1 to the tempo."""
        self.calc = 'beat'
        self.tempo = self.tempo + 1
        self.cuelist.calculate()

    def tempo_down(self):
        """Substract 1 from the tempo."""
        self.calc = 'beat'
        self.tempo = self.tempo - 1
        self.cuelist.calculate()

    @property
    def hold_tempo(self):
        """Get hold_tempo."""
        return self._hold_tempo

    @hold_tempo.setter
    def hold_tempo(self, value):
        """Set hold_tempo."""
        self._hold_tempo = bool(value)

    @property
    def beat(self):
        """Get beat."""
        return self._beat

    @beat.setter
    def beat(self, value):
        """Set beat."""
        # do not change the first cue point
        if self.first:
            self._beat = Decimal('0')
            return False

        try:
            self._beat = Decimal(value)
        except:
            pass

    def beat_up(self):
        """Add resolution to beat."""
        if self.cuelist is not None and not self.first:
            self.calc = 'tempo'
            self.beat = self.beat + convert_beat(self.cuelist.resolution)
            self.cuelist.calculate()

    def beat_down(self):
        """Substract resolution from beat."""
        if self.cuelist is not None:
            self.calc = 'tempo'
            self.beat = self.beat - convert_beat(self.cuelist.resolution)
            self.cuelist.calculate()

    def beat_readable(self, beat=None):
        """Return readable beat string."""
        # return nothing, if no cuelist is set
        if self.cuelist is None or self.first:
            return 'Bar 1, Beat 1.0'

        # get parameter beat, or self._beat
        try:
            beat = Decimal(beat)
        except:
            beat = self._beat

        # init bar and bar values
        one_bar = (
            Decimal(self.cuelist.timesignature_upper) *
            convert_beat(self.cuelist.timesignature_lower)
        )

        bar = int(str(beat / one_bar).split('.', 1)[0]) + 1
        beats = (beat % one_bar) + 1

        return 'Bar {}, Beat {:.5}'.format(bar, beats)

    @property
    def calc(self):
        """Get what to calculate."""
        return self._calc

    @calc.setter
    def calc(self, value):
        """Set what to calculate."""
        if value == 'beat' or value == 0:
            self._calc = 'beat'
        elif value == 'tempo' or value == 1:
            self._calc = 'tempo'
        elif value == 'time' or value == 2:
            self._calc = 'time'

    def to_dict(self):
        """Convert object to dict."""
        out = {}

        # fetch the variables
        out['type'] = self.__class__.__name__
        out['first'] = self.first
        out['title'] = self.title
        out['comment'] = self.comment
        out['framerate'] = self.timecode.framerate
        out['timecode'] = self.timecode.tc_to_ms()
        out['tempo'] = self.tempo
        out['hold_tempo'] = self.hold_tempo
        out['beat'] = str(self.beat)

        return out

    def to_json(self, indent=2, ensure_ascii=False):
        """Convert variables data to json format."""
        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=True
        )

    @classmethod
    def from_json(cls, js=None):
        """Convert all data from json format."""
        if js is None:
            return cls()

        # get js as dict
        if type(js) is not dict:
            try:
                js = json.loads(js)
            except Exception:
                # return default object
                return cls()

        # create object from json
        if 'first' in js.keys():
            first = js['first']
        else:
            first = None

        if 'title' in js.keys():
            title = js['title']
        else:
            title = None

        if 'comment' in js.keys():
            comment = js['comment']
        else:
            comment = None

        if 'framerate' in js.keys():
            framerate = js['framerate']
        else:
            framerate = None

        if 'timecode' in js.keys():
            timecode = js['timecode']
        else:
            timecode = None

        if 'tempo' in js.keys():
            tempo = js['tempo']
        else:
            tempo = None

        if 'hold_tempo' in js.keys():
            hold_tempo = js['hold_tempo']
        else:
            hold_tempo = None

        if 'beat' in js.keys():
            beat = js['beat']
        else:
            beat = None


        # return new object
        return cls(
            first=first,
            title=title,
            comment=comment,
            framerate=framerate,
            timecode=timecode,
            tempo=tempo,
            hold_tempo=hold_tempo,
            beat=beat
        )


class MIDICueList(object):
    """The object holding some settings and a list with the MIDICues."""

    def __init__(
        self,
        framerate=None,
        resolution=64,
        timesignature_upper=4,
        timesignature_lower=4,
        cues=None
    ):
        """Initialize the class."""
        # add the needed first cuepoint at 00:00:00:00
        if cues is None:
            self._cues = []
            self._cues = [
                MIDICue(
                    cuelist=self,
                    first=True,
                    title='Start',
                    timecode='0'
                )
            ]
        else:
            self._cues = cues

        self.framerate = 1000 if framerate is None else framerate

        """
        the resolution determines the stepsize for calculating the tempo or beat of
        a cuepoint. it should be a musical note length like: 1, 2, 4, 8, 1, 32, 64 ...
        the higher the value the higher the accuracy of calculation, but probably the
        higher the calculation time.
        """
        self.resolution = resolution

        """
        upper and lower specifying the time signature. the upper value is the amount
        of notes in a bar and the lower value is the note lengths, which should
        be something like typical musical note lengths like: 1, 2, 4, 8, 16, 32, 64 ...
        """
        self.timesignature_upper = timesignature_upper
        self.timesignature_lower = timesignature_lower

    def __repr__(self):
        """Represent yourself as the cuelist."""
        return self._cues

    def __str__(self):
        """Represent yourself as a string (use __repr__ for this)."""
        return str([str(x) for x in self.__repr__()])

    def __iter__(self):
        """Iter through the cues."""
        for x in self._cues:
            yield x

    def __getitem__(self, index):
        """Get item from cuelist."""
        if index < 0:
            return self._cues[0]
        if index > 0 and index < len(self._cues):
            return self._cues[index]
        else:
            return self._cues[len(self._cues) - 1]

    def __setitem__(self, index, value):
        """Set item of cuelist."""
        if type(value) is MIDICue:
            if index < 0:
                self._cues[0] = value
            elif index > 0 and index < len(self._cues):
                self._cues[index] = value
            else:
                self._cues[len(self._cues) - 1] = value

    def new(self):
        """Return self with empty list."""
        return MIDICueList(
            framerate=self.framerate,
            resolution=self.resolution,
            timesignature_upper=self.timesignature_upper,
            timesignature_lower=self.timesignature_lower,
        )

    def sort(self):
        """Sort the cues."""
        self._cues = sorted(self._cues, key=lambda x: x.timecode.tc_to_ms())

    def append(
        self,
        title='Cue point',
        comment='',
        timecode='0',
        tempo=None,
        hold_tempo=False,
        beat=None
    ):
        """Append a cue point."""
        if tempo is None:
            tempo = self._cues[len(self._cues) - 1].tempo

        if beat is None:
            beat = self._cues[len(self._cues) - 1].beat

        # generate cuepoint
        add_me = MIDICue(
            cuelist=self,
            title=title,
            comment=comment,
            framerate=self.framerate,
            timecode=timecode,
            tempo=tempo,
            hold_tempo=hold_tempo,
            beat=beat
        )

        # check if given timecode exists already
        tc_exists = True
        while tc_exists:
            if add_me.timecode.frames not in [c.timecode.frames for c in self._cues]:
                tc_exists = False
            else:
                add_me.timecode.frames += 1

        self._cues.append(add_me)
        self.calculate()

    def pop(self, index):
        """Pop a cue point with given index from list - but not the first."""
        if index != 0:
            self._cues.pop(index)
            self.calculate()

    def index(self, cue):
        """Return index of cue."""
        return self._cues.index(cue)

    @property
    def framerate(self):
        """Get the framerate."""
        return self._framerate

    @framerate.setter
    def framerate(self, value):
        """Set the framerate for itself and all its cues entries."""
        self._framerate = value
        for cue in self._cues:
            if type(cue) is Timecode:
                cue.timecode.framerate = value

    @property
    def resolution(self):
        """Get resolution."""
        return self._resolution

    @resolution.setter
    def resolution(self, value):
        """Set resolution."""
        try:
            self._resolution = int(value)
        except:
            pass

    @property
    def timesignature_upper(self):
        """Get timesignature_upper."""
        return self._timesignature_upper

    @timesignature_upper.setter
    def timesignature_upper(self, value):
        """Set timesignature_upper."""
        try:
            self._timesignature_upper = int(value)
        except:
            pass

    @property
    def timesignature_lower(self):
        """Get timesignature_lower."""
        return self._timesignature_lower

    @timesignature_lower.setter
    def timesignature_lower(self, value):
        """Set timesignature_lower."""
        try:
            self._timesignature_lower = int(value)
        except:
            pass

    def calc_tempo(self, beats, start_tempo, end_tempo, beat=None):
        """
        Calculate tempo at beat in the given beats.

        The equation is based on:

        https://smartech.gatech.edu/bitstream/handle/1853/54588/WAC2016-49.pdf?sequence=1&isAllowed=y

        and the linear function in:

        https://github.com/echo66/bpm-timeline.js
        """
        x1 = Decimal(beats)
        y0 = Decimal(60 / start_tempo)
        y1 = Decimal(60 / end_tempo)
        x = Decimal(beats) if beat is None else x1

        return Decimal(60) / (y0 + (y1 - y0) * (x / x1))

    def calc_end_tempo(self, beats, start_tempo, time):
        """
        Calculate end tempo to fit beats in time and start tempo.

        Function also based on the sources mentioned in calc_tempo().
        """
        x1 = Decimal(beats)
        y0 = Decimal(60) / Decimal(start_tempo)
        t = Decimal(time) / Decimal(1000)

        if x1 == 0:
            return start_tempo
        else:
            return Decimal(60) / ((2 * t) / x1 - y0)

    def calc_time(self, beats, start_tempo, end_tempo, beat=None):
        """
        Calculate milliseconds passing in the given period or at beat.

        Function also based on the sources mentioned in calc_tempo().
        """
        x1 = Decimal(beats)
        y0 = Decimal(60) / Decimal(start_tempo)
        y1 = Decimal(60) / Decimal(end_tempo)
        x = Decimal(beats) if beat is None else x1

        delta = (y1 - y0) / x1

        seconds = (delta / 2) * (x ** 2) + y0 * x

        return int(round(seconds * 1000))

    def calc_beat(self, start_tempo, end_tempo, time):
        """
        Calculate the beats passed in milliseconds between tempos.

        I used the equation form the mentioned sources and then I used:

        http://www.wolframalpha.com/widgets/view.jsp?id=ad90fa06581eed56d398e0c50fb52357

        to change the equation and solve it to x, so that it gives me the beat, instead
        of the time.
        """
        y0 = Decimal(60) / Decimal(start_tempo)
        y1 = Decimal(60) / Decimal(end_tempo)
        t = Decimal(time) / Decimal(1000)

        if y0 + y1 == 0:
            return 0
        else:
            return (2 * t) / (y0 + y1)

    def calculate(self):
        """
        Calculate the spicy information.

        This is the core method of the whole programm. It will calculate
        either the new beat or the new tempo for each cuepoint, depending
        on the MIDICue.calc variable.
        """
        # cancel if there are not more than one entries
        if len(self._cues) < 1:
            return False

        # iter through all cuepoints
        for i, cue in enumerate(self._cues):

            # skip the first cue point, which should be at 0 ms and 0 beats
            if i == 0:
                continue

            # get start tempo from cue-tempo before this cue
            start_tempo = self._cues[i - 1].tempo

            # get end tempo from actual cue-tempo, if cue before this cue
            # is not set to hold_tempo
            end_tempo = (
                self._cues[i - 1].tempo
                if self._cues[i - 1].hold_tempo
                else cue.tempo
            )

            # get beats difference between this and cue before
            beats_diff = cue.beat - self._cues[i - 1].beat

            # get time difference between this and the cue before
            time_diff = cue.timecode.tc_to_ms() - self._cues[i - 1].timecode.tc_to_ms()

            # check which calculation method is set
            # or set it to bar, if cue before has hold_time
            if self._cues[i - 1].hold_tempo:
                cue.calc = 'beat'

            # caclulate the beat for this cue point
            if cue.calc == 'beat':

                # calculate the new beat for actual cue, based on beat of cue before
                cue.beat = self._cues[i - 1].beat + Decimal(self.calc_beat(
                    start_tempo=start_tempo,
                    end_tempo=end_tempo,
                    time=time_diff
                ))

            # calculate the tempo for this cue point
            elif cue.calc == 'tempo':

                # calculate the new tempo for actual cue
                cue.tempo = self.calc_end_tempo(
                    beats=beats_diff,
                    start_tempo=start_tempo,
                    time=time_diff
                )

            # calculate the time for this cue point
            elif cue.calc == 'time':

                # caluclate the new time for actual cue
                cue.timecode = self._cues[i - 1].timecode.tc_to_ms() + self.calc_time(
                    beats=beats_diff,
                    start_tempo=start_tempo,
                    end_tempo=end_tempo
                )

    def convert_and_link(self):
        """Convert MIDICues to objects and link them to self."""
        for i, cue in enumerate(self._cues):
            self._cues[i] = MIDICue().from_json(js=cue)
            self._cues[i].cuelist = self

    def to_dict(self):
        """Convert object to dict."""
        out = {}

        # fetch the variables
        out['type'] = self.__class__.__name__
        out['framerate'] = self.framerate
        out['resolution'] = self.resolution
        out['timesignature_upper'] = self.timesignature_upper
        out['timesignature_lower'] = self.timesignature_lower

        # fetch the jsons from the cues
        out['cues'] = []
        for cue in self._cues:
            try:
                out['cues'].append(cue.to_dict())
            except:
                out['cues'].append(str(cue))

        return out

    def to_json(self, indent=2, ensure_ascii=False):
        """Convert variables data to json format."""
        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=True
        )

    @classmethod
    def from_json(cls, js=None):
        """Convert all data from json format."""
        if js is None:
            return cls()

        # get js as dict
        if type(js) is not dict:
            try:
                js = json.loads(js)
            except Exception:
                # return default object
                return cls()

        # create object from json
        if 'framerate' in js.keys():
            framerate = js['framerate']
        else:
            framerate = None

        if 'resolution' in js.keys():
            resolution = js['resolution']
        else:
            resolution = None

        if 'timesignature_upper' in js.keys():
            timesignature_upper = js['timesignature_upper']
        else:
            timesignature_upper = None

        if 'timesignature_lower' in js.keys():
            timesignature_lower = js['timesignature_lower']
        else:
            timesignature_lower = None

        if 'cues' in js.keys():
            cues = js['cues']
        else:
            cues = None

        # convert MIDICues to object and link them to the MIDICueList
        obj = cls(
            framerate=framerate,
            resolution=resolution,
            timesignature_upper=timesignature_upper,
            timesignature_lower=timesignature_lower,
            cues=cues
        )

        obj.convert_and_link()

        # return new object
        return obj

    def export_to_midi(self, file=None):
        """Export the cuelist to midi tempo automation."""
        if type(file) is not str:
            return False

        if not file.endswith('.mid'):
            file += '.mid'

        midi = MIDIFile(1)
        midi.addTrackName(0, 0, 'Tagirijus - midicuer')

        # the great export loop
        for i, cue in enumerate(self._cues):

            # skip first entry, because the loop will always add the last one first
            if cue.first:
                continue
            else:
                last_cue = self._cues[i - 1]

            # add last ones beat
            beat = float(last_cue.beat)
            midi.addNote(0, 1, 60, beat, 1, 100)

            # either add simple tempo and continue
            if last_cue.hold_tempo:
                beat = last_cue.beat
                tempo = last_cue.tempo
                midi.addTempo(0, float(beat), tempo)

            # or iter through the tempo changes in resolution steps
            else:
                start_beat = last_cue.beat
                end_beat = cue.beat
                beat_diff = end_beat - start_beat
                beat = Decimal('0')
                while start_beat + beat < end_beat:
                    tempo = self.calc_tempo(
                        beats=beat_diff,
                        start_tempo=last_cue.tempo,
                        end_tempo=cue.tempo,
                        beat=beat
                    )
                    midi.addTempo(0, float(start_beat + beat), tempo)
                    beat += Decimal(str(convert_beat(self.resolution)))

        # add last beat
        beat = float(self._cues[len(self._cues) - 1].beat)
        midi.addNote(0, 1, 60, beat, 1, 100)

        # save it to the file
        with open(file, 'wb') as f:
            midi.writeFile(f)

        return True
