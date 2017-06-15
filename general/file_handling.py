"""Module for saving and loading a string to / from a file."""

import os


class FileObject(object):
    """The FileObject for saving and loading a string."""

    def __init__(self, file=None):
        """Initialize the class."""
        self.file = file
        self.validate_file()

    def validate_file(self):
        """Check if file is valid."""
        # no file set
        if self._file is None:
            self._new_file = True
            self._valid = False
            return False

        # check if file exists already
        if os.path.exists(self._file):
            self._new_file = False
        else:
            self._new_file = True

        # if it's a dir it's not valid
        if os.path.isdir(self._file):
            self._valid = False
        else:
            self._valid = True

    @property
    def file(self):
        """Get file."""
        return self._file

    @file.setter
    def file(self, value=None):
        """Set the file and validate it."""
        self._file = value

        # check if string and append fileending
        if type(self._file) is str:
            if not self._file.endswith('.midicuer'):
                self._file += '.midicuer'

        self.validate_file()

    @property
    def valid(self):
        """Get valid."""
        return self._valid

    @valid.setter
    def valid(self, value=None):
        """Basically do nothing - valid is not setable, but must be checked."""
        self.validate_file()

    @property
    def new_file(self):
        """Get new_file."""
        return self._new_file

    @new_file.setter
    def new_file(self, value=None):
        """Basically do nothing - new_file is not setable, but must be checked."""
        self.validate_file()

    def save(self, string=None):
        """Save the string to the file."""
        # cancel if filename is not valid and not new_file
        if not self.valid and not self.new_file:
            return False

        # save the string
        with open(self.file, 'w') as f:
            f.write(str(string))

        return True

    def load(self):
        """Load a string from file and return it."""
        # cancel if filename is not valid or new file (should not exist)
        if not self.valid:
            return False

        if self.new_file:
            return True

        # load the string
        with open(self.file, 'r') as f:
            out = f.read()

        return out
