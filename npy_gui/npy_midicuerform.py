"""The main form holding the MIDICues list."""

import curses
import npyscreen
import os


class CueList(npyscreen.MultiLineAction):
    """List of the cues."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super(CueList, self).__init__(*args, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            curses.KEY_IC: self.add_cue,
            curses.KEY_DC: self.del_cue,
            'b': self.beat_up,
            'B': self.beat_down,
            't': self.tempo_up,
            'T': self.tempo_down
        })

        # set up additional multiline options
        self.slow_scroll = True

    def beat_up(self, keypress=None):
        """Add beat."""
        self.values[self.cursor_line].beat_up()
        self.update_values()

    def beat_down(self, keypress=None):
        """Substract beat."""
        self.values[self.cursor_line].beat_down()
        self.update_values()

    def tempo_up(self, keypress=None):
        """Add tempo."""
        self.values[self.cursor_line].tempo_up()
        self.update_values()

    def tempo_down(self, keypress=None):
        """Substract tempo."""
        self.values[self.cursor_line].tempo_down()
        self.update_values()

    def update_values(self):
        """Update values."""
        self.parent.parentApp.tmpCues.sort()
        self.values = self.parent.parentApp.tmpCues._cues

        self.display()

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

    def choose_file(self):
        """Choose a file to load, or save if save=True."""
        return npyscreen.selectFile(
            starting_value=os.getcwd(),
            confirm_if_exists=False
        )

    def new(self):
        """Create a new project."""
        really = npyscreen.notify_yes_no(
            'Really create a new project and clear actual (maybe unsaved!?) project?',
            form_color='WARNING'
        )

        if really:
            self.parentApp.tmpCues = self.parentApp.tmpCues.new()
            self.parentApp.theFile.file = None
            self.beforeEditing()

    def save(self):
        """Save project."""
        # prepare values
        is_valid = self.parentApp.theFile.valid
        is_new = self.parentApp.theFile.new_file
        content = self.parentApp.tmpCues.to_json()

        # simplest save: valid and new file
        if is_valid and is_new:
            saved = self.parentApp.theFile.save(content)

            if not saved:
                npyscreen.notify_confirm(
                    'Saving went wrong.',
                    form_color='WARNING'
                )
                return False

        # is valid, but not new, ask for overwrite
        elif is_valid and not is_new:
            overwrite = npyscreen.notify_yes_no(
                'Overwrite "{}"?'.format(self.parentApp.theFile.file),
                form_color='DANGER'
            )

            if overwrite:
                saved = self.parentApp.theFile.save(content)

                if not saved:
                    npyscreen.notify_confirm(
                        'Saving went wrong.',
                        form_color='WARNING'
                    )
                    return False

        # not valid, choose new file
        else:
            self.parentApp.theFile.file = self.choose_file()
            self.save()

        self.update_title()

    def save_as(self):
        """Save project as."""
        self.parentApp.theFile.file = self.choose_file()
        self.save()

    def load(self):
        """Load project."""
        self.parentApp.theFile.file = self.choose_file()
        content = self.parentApp.theFile.load()

        if content is False:
            retry = npyscreen.notify_yes_no(
                'Loading went wrong. Choose another file?',
                form_color='WARNING'
            )

            if retry:
                self.load()

        else:
            self.parentApp.tmpCues = self.parentApp.tmpCues.from_json(js=content)

        self.update_title()

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
        self.m.addItem(text='New', onSelect=self.new, shortcut='n')
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

    def update_title(self):
        """Update form title."""
        self.name = 'midicuer ({})'.format(
            self.parentApp.theFile.file
        )

    def beforeEditing(self):
        """Get values."""
        self.update_title()

        # update cues
        self.cue_box.entry_widget.update_values()
