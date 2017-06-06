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
        pass

        self.display()

        # clear filter for not showing doubled entries (npyscreen bug?)
        self.clear_filter()

    def display_value(self, vl):
        """Display values."""
        return vl

    def add_cue(self, keypress=None):
        """Add a new cue."""
        pass

        # switch to the cue edit form
        self.parent.parentApp.setNextForm('MIDICueEdit')
        self.parent.parentApp.switchFormNow()

    def del_cue(self, keypress=None):
        """Ask to delete the cue and do it if yes."""
        # cancel if there are no projects
        if len(self.values) < 1:
            return False

        # get selected cue
        cue = self.values[self.cursor_line]

        cue_str = '"{}: {}"'.format(cue.client_id, cue.title)
        really = npyscreen.notify_yes_no(
            'Really deactivate the cue {}?'.format(project_str),
            form_color='WARNING'
        )

        # yepp, deactivate it
        if really:
            pass

    def actionHighlighted(self, act_on_this, keypress=None):
        """Do something, because a key was pressed."""
        try:
            pass

            # switch to the cue edit form
            self.parent.parentApp.setNextForm('MIDICueEdit')
            self.parent.parentApp.switchFormNow()
        except Exception:
            npyscreen.notify_confirm(
                'Something went wrong, sorry!',
                form_color='WARNING'
            )


class CueListBox(npyscreen.BoxTitle):
    """Box holding the CueList."""

    _contained_widget = CueList


class MIDICueForm(npyscreen.FormBaseNewWithMenus):
    """MIDICueForm."""

    def exit(self):
        """Exit the programm."""
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

    def create(self):
        """Initialize the form with its widgets."""
        # create the menu
        self.m = self.new_menu(name='Menu')
        self.m.addItem(text='Exit', onSelect=self.exit, shortcut='e')

        # create the box with the project list and update the list
        self.cue_box = self.add(
            CueListBox,
            name='Cues'
        )

    def beforeEditing(self):
        """Get correct lists for clients and projects."""
        # update cues
        self.cue_box.entry_widget.update_values()
