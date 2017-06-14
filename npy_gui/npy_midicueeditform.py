"""The form for editing a MIDICue object."""

import npyscreen


class TitleMultiLineEdit(npyscreen.TitleText):
    """Titled MultiLineEdit."""

    _entry_type = npyscreen.MultiLineEdit
    scroll_exit = True

    def reformat(self):
        """Reformat the content."""
        self.entry_widget.full_reformat()


class MIDICueEditForm(npyscreen.ActionFormWithMenus):
    """MIDICueEditForm."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super(MIDICueEditForm, self).__init__(*args, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            '^O': self.on_ok,
            '^Q': self.on_cancel,
            '^F': self.clear_widget
        })

    def clear_widget(self, keypress=None):
        """Clear widget."""
        self.get_widget(self.editw).value = ''

    def exit(self):
        """Exit the programm."""
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

    def create(self):
        """Initialize the form with its widgets."""
        # create the menu
        self.m = self.new_menu(name='Menu')
        self.m.addItem(text='Exit', onSelect=self.exit, shortcut='e')

        # create widgets
        self.title = self.add(
            npyscreen.TitleText,
            name='Title:',
            begin_entry_at=20
        )
        self.comment = self.add(
            TitleMultiLineEdit,
            name='Comment:',
            begin_entry_at=20,
            max_height=2
        )
        self.timecode = self.add(
            npyscreen.TitleText,
            name='Timecode:',
            begin_entry_at=20
        )
        self.tempo = self.add(
            npyscreen.TitleText,
            name='Tempo:',
            begin_entry_at=20
        )
        self.hold_tempo = self.add(
            npyscreen.TitleMultiSelect,
            name='Hold tempo:',
            begin_entry_at=20,
            max_height=2,
            scroll_exit=True,
            values=['enabled']
        )
        self.beat = self.add(
            npyscreen.TitleText,
            name='Beat:',
            begin_entry_at=20
        )
        self.calc = self.add(
            npyscreen.TitleSelectOne,
            name='Calculate:',
            begin_entry_at=20,
            max_height=3,
            scroll_exit=True,
            values=[
                'Beat',
                'Tempo',
                'Timecode'
            ]
        )

    def beforeEditing(self):
        """Get values."""
        self.title.value = self.parentApp.tmpCue.title
        self.comment.value = self.parentApp.tmpCue.comment
        self.comment.reformat()
        self.timecode.value = str(self.parentApp.tmpCue.timecode)
        self.tempo.value = str(self.parentApp.tmpCue.tempo)
        self.hold_tempo.value = [0] if self.parentApp.tmpCue.hold_tempo else []
        self.beat.value = str(self.parentApp.tmpCue.beat)

        if self.parentApp.tmpCue.calc == 'beat':
            self.calc.value = [0]
        elif self.parentApp.tmpCue.calc == 'tempo':
            self.calc.value = [1]
        elif self.parentApp.tmpCue.calc == 'time':
            self.calc.value = [2]

    def on_ok(self, keypress=None):
        """Store new values."""
        self.parentApp.tmpCue.title = self.title.value
        self.parentApp.tmpCue.comment = self.comment.value.replace('\n', ' ')
        self.parentApp.tmpCue.timecode = self.timecode.value
        self.parentApp.tmpCue.tempo = self.tempo.value

        if self.hold_tempo.value == [0]:
            self.parentApp.tmpCue.hold_tempo = True
        else:
            self.parentApp.tmpCue.hold_tempo = False

        self.parentApp.tmpCue.beat = self.beat.value

        if self.calc.value == [0]:
            self.parentApp.tmpCue.calc = 'beat'
        elif self.calc.value == [1]:
            self.parentApp.tmpCue.calc = 'tempo'
        elif self.calc.value == [2]:
            self.parentApp.tmpCue.calc = 'time'

        # recalculate stuff
        self.parentApp.tmpCues.calculate()

        # and switch form
        self.parentApp.setNextForm('MAIN')
        self.parentApp.switchFormNow()

    def on_cancel(self, keypress=None):
        """Cancel and switch back."""
        self.parentApp.setNextForm('MAIN')
        self.parentApp.switchFormNow()
