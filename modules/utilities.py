"""

Utitliies

"""

from itertools import groupby
import json
import modules.getcomments as getcomments
from operator import itemgetter
import os
import re
import tldextract
import yaml


def commonprefix(args, sep="\\"):
    """
    Return the common prefix string for a list of file paths.
    Typically used to remove that prefix to shorten the filename for display,
    i.e. to provide relative file paths.
    """
    return os.path.commonprefix(args).rpartition(sep)[0]


def get_comments(filename):
    """
    Get Julia, Python, R comments.
    """

    comments = []
    try:
        with open(filename, 'r', encoding='utf8') as fp:
            filename = os.path.basename(filename)
            for comment, start, end in getcomments.get_comment_blocks(fp):
                comments.append({ "ln%s" % (start[0]) : comment.rstrip()})
    except Exception as e:
        print(e)

    return comments


def get_filenames(filename):
    """
    Return list of unique file references within a passed file.
    """
    try:
        with open(filename, 'r', encoding='utf8') as file:
            words = re.split("[\n\\, \-!?;'//]", file.read())
            #files = filter(str.endswith(('csv', 'zip')), words)
            files = set(filter(lambda s: s.endswith(('.csv', '.zip', '.pdf', '.txt', '.tsv', '.cfg', '.ini')), words))
            return list(files)
    except Exception as e:
        print(e)
        return []


def get_model_types_from_libraries(imports, self_sep, language_name):
        """
          Return list of model_types from model-type-libraries based on libraries.

          example:
              import import scipy.ndimage.fourier
              library: "scipy.ndimage"

        """
        model_types = set()
        imports = set(item.lower() for item in imports) # convert to lowercase set

        library_filename = 'data_files' + self_sep + 'model-type-libraries.json' # already lowercase
        matches = []
        try:
           library_file = open(library_filename).read()
           library_file = json.loads(library_file)
           for lang in library_file['languages']:
               if (lang['name'] == language_name):
                   for model in lang['model_types']:
                       for lib_name in model['libraries']:
                           # match if the entire library name matches, or if the library name
                           # is the prefix for the import.
                           matches = [i for i in imports if (lib_name in i.split() or i.startswith(lib_name + '.'))]
                           if len(matches) > 0:
                               model_types.add(model['name'])
        except Exception as e:
            print('get_model_types_from_libraries error', e)
        return model_types



def get_output1(filename):
    """
    Supports Python, Julia
    Return set of tuples: source_file, output_file
    Use group_tuple_pairs() to organize these for output to yaml etc.

    Cases:

    (1)
    writer(open())
    writer.writerows(object)

    (2) with open()
            write

        example from pythia:
        def compose_peerless(context, config, env):
            print(".", end="", flush=True)
            this_output_dir = context["contextWorkDir"]
            symlink_wth_soil(this_output_dir, config, context)
            xfile = pythia.template.render_template(env, context["template"], context)
            with open(os.path.join(context["contextWorkDir"], context["template"]), "w") as f:
                f.write(xfile)
            return context["contextWorkDir"]

    (3)
    file = open()
    write...
    close()
    """

    def get_open_filepath(line):

        quoted_stuff = re.findall(r"['\"](.*?)['\"]", line) # single and double quotes
        if quoted_stuff:
            # remove a or w directives from list
            for s in ['a', 'w']:
                if s in quoted_stuff:
                    quoted_stuff.remove(s)
            if quoted_stuff is None:
                # e.g.: with open(output_csv, 'w') as csv_file:
                obj_name = line.split('(')[0].split(',')[0]
                if obj_name in object_dict:
                    obj_name = object_dict[obj_name]
                return obj_name
            else:
                return ' '.join(quoted_stuff)
        else:
            try:
                return line.split('(')[1].split(',')[0]
            except:
                return ''

    object_dict = {}  # dict of objects defined in file
    output_files = []
    with open(filename, 'rt', encoding='utf8') as file:
        lines = file.read().splitlines()
        line_num = None  # store line with open()
        file_path = None

        for idx, line in enumerate(lines):
            line = line.strip()
            # ignore comment lines and remove inline comments
            if (line.startswith('#')):
                continue
            line = line.split('#')[0].strip()

            if line.count('=') == 1:
                # Parse simple assignment lines
                # e.g. xfile = pythia.template.render_template(env, context["template"], context)
                sa = line.split('=')
                object_dict[sa[0].strip()] = sa[1].strip()

            elif '.open(' in line:
                # Handle single line write e.g. csv.writer(open())
                line_num = idx + 1
                file_path = get_open_filepath(line)

            ## Handle with open() block
            elif ('with open(' in line):
                #t = (filename, "ln {0:>4}: {1}".format(idx+1, get_open_filepath(line)))
                #with_open = True
                line_num = idx + 1
                file_path = get_open_filepath(line)

            elif 'write(' in line and file_path is not None:
                obj_name = line.split('(')[1].split(')')[0]
                if obj_name in object_dict:
                    obj_name = object_dict[obj_name]


                #output_dict = dict(line = line_num, path = file_path, write = obj_name)
                output_files.append((filename, line_num, file_path, obj_name))
                file_path = None


    return output_files


def get_output2(filename):
    """
    Supports R
    Return set of tuples: source_file, output_file
    Use group_tuple_pairs() to organize these for output to yaml etc.

    """
    output_files = []
    with open(filename, 'rt', encoding='utf8') as file:
        for idx, line in enumerate(file):
            if ('write' in line and '(' in line):
                # write.csv(Gstrength_in_df,paste0("COVID-19_data/data_network/", runname[1],"Gstrength_in_", unitname, ".csv"), row.names = FALSE)
                #
                sa = line.split(',')

                # handle first split, which should include the outputed object; its name should be informative
                object_name = sa[0].split('(')[1]

                # collect everything remaining in quotations.
                quoted_stuff = re.findall('"([^"]*)"', line)

                # t = (filename, "ln {0:>4}: obj: {1}; partial path: {2}".format(idx+1, object_name, ''.join(quoted_stuff)))
                output_files.append((filename, idx+1, ''.join(quoted_stuff), object_name))
    return output_files

def get_urls(filename):
    """
    Return set of tuples: url_domain, complete_url
    Use group_tuple_pairs() to organize these for output to yaml etc.
    """
    urls = []
    try:
        with open(filename, 'r', encoding='utf8') as f:
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
                            ext = tldextract.extract(url)   # parses url
                            url = ('.'.join(ext[1:3]), url) # create 2nd level domain from ext object, add as first element in tuple(to use as key later)
                            urls.append(url)
    except Exception as e:
        print('get urls error in ' + filename, e)

    return urls


def group_tuple_pairs(list_of_tuples):
    """
    From a list of tuples of (domain.com, urls), return a dictionary of
    domain.com: (url1, url2, ...)
    for yaml output
    """
    sorter = sorted(list_of_tuples, key=itemgetter(0))
    grouper = groupby(sorter, key=itemgetter(0))

    return {k: list(map(itemgetter(1), v)) for k, v in grouper}



def replace_cp_in_dict_list(in_list, cp):
    """
    Remove the common prefix (cp) for keys of filenames in a list of dictionaries.
    e.g. for readme files.
    """
    out_list = []
    for d in in_list:
        key, value = list(d.items())[0]
        out_list.append({ key.replace(cp,''): value  })
    return out_list


def replace_cp_in_tuple_set(in_set, cp):
    """
    Remove the common prefix (cp) from the first tuple item in a set.
    e.g. for source filenames paired with output file information.
    """
    out_list = []
    for t in in_set:
        new_t = (t[0].replace(cp,''),) + t[1:]
        out_list.append(new_t)

    return sorted(out_list)


def reorg_output_files(output_files):
    """
    assumes output_files is a list or set of tuples:
    (filename, line, path, write_object)
    reorganize into a tuple (filename, [dict of last 3 items])
    """
    for i in range(0, len(output_files)):
        t = output_files[i]
        output_files[i] = (t[0],) + (dict(line=t[1], path=t[2], write=t[3]),)
    return output_files


def textfile_contains(filename, marker):
    """
    Return True if a textfile contains a string.
    """
    try:
        with open(filename, 'r', encoding='utf8') as file:
            text = file.read();
            if marker in text:
                return True
    except Exception as e:
        print(e)

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








