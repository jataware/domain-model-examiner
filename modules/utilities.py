"""

Utitliies

"""

from itertools import groupby
import modules.getcomments as getcomments
from operator import itemgetter
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

def replace_cp(in_list, cp):
    """
    Remove the common prefix (cp) for keys of filenames in a list of dictionaries.
    e.g. for readme files.
    """
    out_list = []
    for d in in_list:
        key, value = list(d.items())[0]
        out_list.append({ key.replace(cp,''): value  })
    return out_list


def get_comments(filename):
    """
    Get Python and R comments.
    """
    
    comments = []
    with open(filename, 'r', encoding="utf8") as fp:
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
           

def get_filenames(filename):
    """
    Return list of unique file references.
    """
    with open(filename, 'rt', encoding='utf8') as file:
        words = re.split("[\n\\, \-!?;'//]", file.read())
        #files = filter(str.endswith(('csv', 'zip')), words)
        files = set(filter(lambda s: s.endswith(('.csv', '.zip', '.pdf', '.txt')), words))        
        return list(files)
    

def get_urls(filename):
    """
    Return set of urls.
    """
    urls = [] 
    with open(filename, 'r', encoding="utf8") as f:
        for line in f:
            if ('http' in line):
                # get url between delimiters 
                sa = line.split(']')
                for s in sa:
                    # handle markup and other garbage in README.MD files that break the regex
                    s = re.sub('\?|\!|\;|\]|\[|\*', '', s)
                    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                    url = re.findall(regex,s)       
                    if len(url) > 0:
                        url = [x[0] for x in url][0]                        
                        # Report urls as key-value pair where 2nd level domain is key
                        ext = tldextract.extract(url)
                        #url = '.'.join(ext[1:3]) + ' ' + url
                        url = ('.'.join(ext[1:3]), url)
                        urls.append(url)                    
    return urls


def group_urls(urls):
    """
    From a list of tuples of (domain.com, urls), return a dictionary of
    domain.com: (url1, url2, ...)
    for yaml output
    """
    sorter = sorted(urls, key=itemgetter(0))
    grouper = groupby(sorter, key=itemgetter(0))
    
    return {k: list(map(itemgetter(1), v)) for k, v in grouper}


def textfile_contains(filename, marker):
    """
    Return True if a textfile contains a string.
    """
    with open(filename, 'r', encoding="utf8") as file:
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
    # not sure if this representer should be added on every call, or just once per session.
    yaml.add_representer(str, yaml_repr_str, Dumper=yaml.SafeDumper)
    with open("dmx-%s.yaml" % (filename), 'w') as file:
        yaml.safe_dump(yaml_dict, file)
    







