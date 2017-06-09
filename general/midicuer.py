"""The module for the MIDICue class."""

from decimal import Decimal
from timecode import Timecode as Timecode_original


def beat_to_float(beat=1):
    """Convert musical beat to float length."""
    if beat != 0:
        return (1.0 / beat) * 4
    else:
        return 0.0


def float_to_beat(float=1.0):
    """Convert float length to musical beat."""
    if float != 0:
        return round(1.0 / (float / 4))
    else:
        return 0


def tempo_to_ms(tempo=120):
    """Return milliseconds which will pass for one beat with the given [tempo]."""
    return round((60.0 / tempo) * 1000)


def ms_to_tempo(ms=1000):
    """Return tempo according to one beat passed in the given time [ms]."""
    return round((1000 / ms) * 60)


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
            return round(self.frame_number * (1000 / float(self._int_framerate)))
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
        timesignature_upper=4,
        timesignature_lower=4,
        tempo=120,
        hold_tempo=False,
        bar=0
    ):
        """Initialize the class."""
        self.cuelist = cuelist

        self.first = first

        self.title = title
        self.comment = comment

        self._framerate = framerate

        self._timecode = Timecode(self._framerate, 0)
        self.timecode = timecode

        """
        upper and lower specifying the time signature. the upper value is the amount
        of notes in a bar and the lower value is the note lengths, which should
        be something like typical musical note lengths like: 1, 2, 4, 8, 16, 32, 64 ...
        """
        self.timesignature_upper = timesignature_upper
        self.timesignature_lower = timesignature_lower

        self.tempo = tempo

        self.hold_tempo = hold_tempo

        self.bar = bar
        self.bar_readable = ''

        # what to calculate? 'bar' or 'tempo' ?
        self.calc = 'bar'

        # calculate
        self.cuelist.calculate()

    def __repr__(self):
        """Represent yourself."""
        return self._timecode

    def __str__(self):
        """Represent yourself as a string (Timecode: Title)."""
        return '{}: {}'.format(self.title, str(self.__repr__()))

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
        # do not change the first timecode at 0 ms
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

        # try to convert the timecode
        try:
            self._timecode = Timecode(self._framerate, tc)
        except:
            return False

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

    @property
    def tempo(self):
        """Get tempo."""
        return self._tempo

    @tempo.setter
    def tempo(self, value):
        """Set tempo."""
        try:
            self._tempo = int(value)
        except:
            pass

    @property
    def hold_tempo(self):
        """Get hold_tempo."""
        return self._hold_tempo

    @hold_tempo.setter
    def hold_tempo(self, value):
        """Set hold_tempo."""
        self._hold_tempo = bool(value)

    @property
    def bar(self):
        """Get bar."""
        return self._bar

    @bar.setter
    def bar(self, value):
        """Set bar."""
        try:
            self._bar = Decimal(value)
        except:
            pass

    @property
    def bar_readable(self):
        """Get bar_readable."""
        return self._bar_readable

    @bar_readable.setter
    def bar_readable(self, value):
        """Set bar_readable."""
        self._bar_readable = str(value)

    @property
    def calc(self):
        """Get what to calculate."""
        return self._calc

    @calc.setter
    def calc(self, value):
        """Set what to calculate."""
        if value == 'bar' or value == 0:
            self._calc = 'bar'
        elif value == 'tempo' or value == 1:
            self._calc = 'tempo'


class MIDICueList(object):
    """The object holding some settings and a list with the MIDICues."""

    def __init__(
        self,
        framerate=None,
        def_timesignature_upper=4,
        def_timesignature_lower=4,
        resolution=64
    ):
        """Initialize the class."""
        # add the needed first cuepoint at 00:00:00:00
        self._cues = [
            MIDICue(
                cuelist=self,
                first=True,
                title='Start',
                timecode='0'
            )
        ]

        self.framerate = 1000 if framerate is None else framerate

        """
        upper and lower specifying the time signature. the upper value is the amount
        of notes in a bar and the lower value is the note lengths, which should
        be something like typical musical note lengths like: 1, 2, 4, 8, 16, 32, 64 ...
        """
        self.def_timesignature_upper = def_timesignature_upper
        self.def_timesignature_lower = def_timesignature_lower

        """
        the resolution determines the stepsize for calculating the tempo or bar of
        a cuepoint. it should be a musical note length like: 1, 2, 4, 8, 1, 32, 64 ...
        the higher the value the higher the accuracy of calculation, but probably the
        higher the calculation time.
        """
        self.resolution = resolution

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

    def append(
        self,
        title='Cue point',
        comment='',
        timecode='0',
        timesignature_upper=4,
        timesignature_lower=4,
        tempo=120,
        hold_tempo=False,
        bar=0
    ):
        """Append a cue point."""
        # generate cuepoint
        add_me = MIDICue(
            cuelist=self,
            title=title,
            comment=comment,
            framerate=self.framerate,
            timecode=timecode,
            timesignature_upper=timesignature_upper,
            timesignature_lower=timesignature_lower,
            tempo=tempo,
            hold_tempo=hold_tempo,
            bar=bar
        )

        # check if given timecode exists already
        tc_exists = True
        while tc_exists:
            if add_me.timecode.frames not in [c.timecode.frames for c in self._cues]:
                tc_exists = False
            else:
                add_me.timecode.frames += 1

        self._cues.append(add_me)

    def pop(self, index):
        """Pop a cue point with given index from list - but not the first."""
        if index != 0:
            self._cues.pop(index)

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
            cue.timecode.framerate = value

    @property
    def def_timesignature_upper(self):
        """Get def_timesignature_upper."""
        return self._def_timesignature_upper

    @def_timesignature_upper.setter
    def def_timesignature_upper(self, value):
        """Set def_timesignature_upper."""
        try:
            self._def_timesignature_upper = int(value)
        except:
            pass

    @property
    def def_timesignature_lower(self):
        """Get def_timesignature_lower."""
        return self._def_timesignature_lower

    @def_timesignature_lower.setter
    def def_timesignature_lower(self, value):
        """Set def_timesignature_lower."""
        try:
            self._def_timesignature_lower = int(value)
        except:
            pass

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

    def calculate(self):
        """
        Calculate the spicy information.

        This is the core method of the whole programm. It will calculate
        either the new bar or the new tempo for each cuepoint, depending
        on the MIDICue.calc variable.
        """
        pass
