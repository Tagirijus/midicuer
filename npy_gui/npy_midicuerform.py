"""The main form holding the MIDICues list."""

import curses
import npyscreen


class CueList(npyscreen.MultiLineAction):
    """List of the cues."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super(CueList, self).__init__(*args, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            curses.KEY_IC: self.add_cue,
            curses.KEY_DC: self.del_cue
        })

        # set up additional multiline options
        self.slow_scroll = True

    def update_values(self):
        """Update values."""
        self.parent.parentApp.tmpCues.sort()
        self.values = self.parent.parentApp.tmpCues._cues

        self.display()

        # clear filter for not showing doubled entries (npyscreen bug?)
        self.clear_filter()

    def display_value(self, vl):
        """Display values."""
        return vl

    def add_cue(self, keypress=None):
        """Add a new cue."""
        # quick add a cue point - ask title and timecode and add it already
        # detailed editing will be done on pressing enter in list
        timecode = npyscreen.notify_input(
            'Timecode:'
        )

        if timecode is False:
            return False

        title = npyscreen.notify_input(
            'Title:'
        )

        if title is False:
            return False

        # append this
        self.parent.parentApp.tmpCues.append(
            title=title,
            timecode=timecode
        )

        # refresh list
        self.update_values()

    def del_cue(self, keypress=None):
        """Ask to delete the cue and do it if yes."""
        # cancel if there are no projects
        if len(self.values) < 1:
            return False

        # also cancel if it's the first entry
        if self.cursor_line == 0:
            return False

        # get selected cue
        cue = self.values[self.cursor_line]

        really = npyscreen.notify_yes_no(
            'Really delete the cue "{}"?'.format(cue.title),
            form_color='WARNING'
        )

        # yepp, deactivate it
        if really:
            self.parent.parentApp.tmpCues.pop(self.cursor_line)
            self.update_values()

    def actionHighlighted(self, act_on_this, keypress=None):
        """Do something, because a key was pressed."""
        try:
            self.parent.parentApp.tmpCue = act_on_this

            # switch to the cue edit form
            self.parent.parentApp.setNextForm('MIDICueEdit')
            self.parent.parentApp.switchFormNow()
        except:
            npyscreen.notify_confirm(
                'Something went wrong, sorry!',
                form_color='WARNING'
            )


class CueListBox(npyscreen.BoxTitle):
    """Box holding the CueList."""

    _contained_widget = CueList


class MIDICueForm(npyscreen.FormBaseNewWithMenus):
    """MIDICueForm."""

    def save(self):
        """Save project."""
        pass

    def save_as(self):
        """Save project as."""
        pass

    def load(self):
        """Load project."""
        pass

    def project(self):
        """Switch to project settings."""
        self.parentApp.setNextForm('Project')
        self.parentApp.switchFormNow()

    def exit(self):
        """Exit the programm."""
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

    def create(self):
        """Initialize the form with its widgets."""
        # create the menu
        self.m = self.new_menu(name='Menu')
        self.m.addItem(text='Save', onSelect=self.save, shortcut='s')
        self.m.addItem(text='Save as...', onSelect=self.save_as, shortcut='S')
        self.m.addItem(text='Load', onSelect=self.load, shortcut='l')
        self.m.addItem(text='Project', onSelect=self.project, shortcut='p')
        self.m.addItem(text='Exit', onSelect=self.exit, shortcut='e')

        # create the box with the project list and update the list
        self.cue_box = self.add(
            CueListBox,
            name='Cues'
        )

    def beforeEditing(self):
        """Get values."""
        # update cues
        self.cue_box.entry_widget.update_values()
