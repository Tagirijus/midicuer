"""The graphical user interface for the ledgeradd programm."""

from general import file_handling
from general import midicuer
import npyscreen
from npy_gui.npy_midicuerform import MIDICueForm
from npy_gui.npy_midicueeditform import MIDICueEditForm
from npy_gui.npy_projectform import ProjectForm


class MIDICuerApplication(npyscreen.NPSAppManaged):
    """The main application object."""

    def __init__(self, file=None, *args, **kwargs):
        """Initialize the class."""
        super(MIDICuerApplication, self).__init__(*args, **kwargs)

        # set global temp variables
        self.tmpCues = midicuer.MIDICueList()
        self.tmpCue = None

        # set file
        self.theFile = file_handling.FileObject(file=file)

    def onStart(self):
        """Create all the forms and variables, which are needed."""
        # create the forms
        self.addForm(
            'MAIN',
            MIDICueForm,
            name='midicuer'
        )
        self.addForm(
            'MIDICueEdit',
            MIDICueEditForm,
            name='midicuer > edit cue'
        )
        self.addForm(
            'Project',
            ProjectForm,
            name='midicuer > project settings'
        )

        if self.theFile.valid:
            self.getForm('MAIN').load(choose=False)
