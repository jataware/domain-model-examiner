"""

Utitliies

"""

import modules.getcomments as getcomments
import os
import re
import tldextract 
import yaml

def commonprefix(args, sep="\\"):
    """
    Return the common prefix string for a list of file paths.
    Typically used to remove that prefix to shorten the filename for display.
    """
    return os.path.commonprefix(args).rpartition(sep)[0]


def get_comments(filename):
    
    comments = []
    with open(filename) as fp:
        filename = os.path.basename(filename)
        for comment, start, end in getcomments.get_comment_blocks(fp):
            #heading = "%s ln%s" % (filename, start[0])
            #print(heading)
            #print('-' * len(heading))
            #print('')
            #print(comment)
            #print('\n')
            comments.append({ "ln%s" % (start[0]) : comment.rstrip()})
            
    return comments       
            

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
                url = [x[0] for x in url][0]
                
                # Report urls as key-value pair where 2nd level domain is key
                ext = tldextract.extract(url)
                url = '.'.join(ext[1:3]) + ' (' + url + ')'
                urls.add(url)
                    
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


def yaml_repr_str(dumper, data):
    """
    PyYAML representer for strings with new lines e.g. multiline comments.
    """
    if '\n' in data:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
    return dumper.org_represent_str(data)

def yaml_write_file(filename, yaml_dict):
    """
    Handler for writing yaml files controlling for multiline comments.

    """
    yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str
    yaml.add_representer(str, yaml_repr_str, Dumper=yaml.SafeDumper)
    with open("dmx-%s.yaml" % (filename), 'w') as file:
        yaml.safe_dump(yaml_dict, file)
    







