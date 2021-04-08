"""

Utitliies

"""

import os
import re

def commonprefix(args, sep="\\"):
    """
    Return the common prefix string for a list of file paths.
    Typically used to remove that prefix to shorten the filename for display.
    """
    return os.path.commonprefix(args).rpartition(sep)[0]


def get_urls(filename):
    """
    Return set of urls.
    """
    urls = set()
    with open(filename) as f:
        for line in f:
            if ('http' in line):
                # get url between delimiters
                regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                url = re.findall(regex,line)                      
                urls.add([x[0] for x in url][0])
    return urls

def textfile_contains(filename, marker):
    """
    Return True if a textfile contains a string.
    """
    with open(filename, 'r') as file:
        text = file.read();
        if marker in text:
            return True        
    return False

