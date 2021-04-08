"""

Utitliies

"""

import os

def commonprefix(args, sep="\\"):
    """
    Return the common prefix string for a list of file paths.
    Typically used to remove that prefix to shorten the filename for display.
    """
    return os.path.commonprefix(args).rpartition(sep)[0]


def textfile_contains(filename, marker):
    """
    Return True if a textfile contains a string.
    """
    with open(filename, 'r') as file:
        text = file.read();
        if marker in text:
            return True        
    return False