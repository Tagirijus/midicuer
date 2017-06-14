"""The form for editing the project settings."""

import npyscreen


class ProjectForm(npyscreen.ActionFormWithMenus):
    """ProjectForm."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super(ProjectForm, self).__init__(*args, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            '^O': self.on_ok,
            '^Q': self.on_cancel
        })

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
        self.framerate = self.add(
            npyscreen.TitleText,
            name='Framerate:'
        )
        self.resolution = self.add(
            npyscreen.TitleText,
            name='Resolution:'
        )
        self.timesignature_upper = self.add(
            npyscreen.TitleText,
            name='Timesig. upp.:',
            begin_entry_at=20
        )
        self.timesignature_lower = self.add(
            npyscreen.TitleText,
            name='Timesig. low.:',
            begin_entry_at=20
        )

    def beforeEditing(self):
        """Get values."""
        self.framerate.value = str(self.parentApp.tmpCues.framerate)
        self.resolution.value = str(self.parentApp.tmpCues.resolution)
        self.timesignature_upper.value = str(self.parentApp.tmpCues.timesignature_upper)
        self.timesignature_lower.value = str(self.parentApp.tmpCues.timesignature_lower)

    def on_ok(self, keypress=None):
        """Store new values."""
        self.parentApp.tmpCues.framerate = self.framerate.value
        self.parentApp.tmpCues.resolution = self.resolution.value
        self.parentApp.tmpCues.timesignature_upper = self.timesignature_upper.value
        self.parentApp.tmpCues.timesignature_lower = self.timesignature_lower.value

        # and switch form
        self.parentApp.setNextForm('MAIN')
        self.parentApp.switchFormNow()

    def on_cancel(self, keypress=None):
        """Cancel and switch back."""
        self.parentApp.setNextForm('MAIN')
        self.parentApp.switchFormNow()
