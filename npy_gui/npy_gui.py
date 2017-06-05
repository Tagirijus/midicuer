"""The graphical user interface for the ledgeradd programm."""

from general import file_handling
from general import midicuer
import npyscreen


class midicuerApplication(npyscreen.NPSAppManaged):
    """The main application object."""

    def __init__(self, file=None, *args, **kwargs):
        """Initialize the class."""
        super(midicuerApplication, self).__init__(*args, **kwargs)

        # set global temp variables
        self.tmpMIDICues = []

        # set file


    def onStart(self):
        """Create all the forms and variables, which are needed."""
        # create the forms
        self.addForm(
            'MAIN',
            midicuerForm,
            name='midicuer'
        )
