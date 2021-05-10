"""

Miner for Python repos.

"""


import os
import modules.utilities as util
import modules.docker_miner as dminer
import modules.repo_miner as repominer
import re

class PyRepoMiner:
    """
    Python-specific repo miner.
    """
    def __init__(self, repo_path, repo_name):
        self.repo_path = repo_path
        self.repo_name = repo_name

        if os.name == 'nt':
            self.sep = '\\'
        else:
            self.sep = '/'        
            
        self.mine_files()
       
        
    def get_imports(self, filename, root_dirs=()):
        """
        Return unique set of imports.
        Improvement would be to ignore the repo's units.        
        """                
        imports = set()
        with open(filename, 'r', encoding="utf8") as f:
            for line in f:
                line = line.split('#')[0] # remove inline comments
                
                if line.startswith('import') and ',' in line and 'as' in line:                    
                    # e.g. import argparse as ap, json as js, os as opsys
                    line = line.replace('import', '').replace('as','')
                    sa = line.split(',') # break in to library and alias pairs
                    for s in sa:
                        lib = s.split()[0].strip
                        if not lib.startswith(root_dirs):
                            imports.add(s.split()[0].strip) # add library name   
                        
                elif line.startswith('import') and ',' in line:                               
                    # e.g. import argparse, json, os 
                    line = line.replace('import', '')
                    sa = line.split(',')
                    for s in sa:
                        lib = s.strip()
                        if not lib.startswith(root_dirs):
                            imports.add(s.strip())                
                    
                elif line.startswith('import'):
                    # e.g. import argparse
                    #imports.add(line.split()[1].split('.')[0])
                    lib = line.split()[1]
                    if not lib.startswith(root_dirs):
                        imports.add(line.split()[1])
                    
                elif line.startswith('from') and 'import' in line:
                    # eg from git import RemoteProgress, Repo
                    sa = line.split()
                    # iterate tokens in line after the "import"
                    lib = sa[1]
                    if not lib.startswith(root_dirs):
                        for l in sa[3:]:
                            imports.add(sa[1] + '.' + l.strip(','))
                        
        return imports

    def get_output(self, filename):
        """
        Python-specific
        Return set of tuples: source_file, output_file
        Use group_tuple_pairs() to organize these for output to yaml etc.
        
        Cases:      
        
        (1) 
        writer(open())
        
        
        (2)
        with open(
                write...
                
        (3)
        file = open()
        write...
        close()
        """    
        def get_open_filename(line):
            quoted_stuff = re.search('"([^"]*)"', line)
            if quoted_stuff:
                return quoted_stuff.group(0)
            else:
                try:
                    return line.split('(')[1].split(',')[0]    
                except:
                    return ''
        
        output_files = []
        with open(filename, 'rt', encoding='utf8') as file:
            lines = file.read().splitlines() # read into a list to allow backtracking
            
            open_file = False
            with_open = False
            t = ()
            for idx, line in enumerate(lines):
                
                ## Handle single line write e.g. csv.writer(open())                
                if ('write' in line and 'open(' in line):                                      
                    t = (filename, "ln {0:>4}: {1}".format(idx+1, get_open_filename(line)))                    
                    output_files.append(t)
                    
                ## Handle with open() block
                elif ('with open(' in line and not with_open):                                                     
                    t = (filename, "ln {0:>4}: {1}".format(idx+1, get_open_filename(line)))
                    with_open = True
                elif (with_open and 'write(' in line):
                    output_files.append(t)
                    with_open = False
                    
                ## Handle assignment of file handle with open()
                ## e.g.
                ## file = open()
                ## write...
                ## close
                elif ('open(' in line and not open_file):                                                    
                    t = (filename, "ln {0:>4}: {1}".format(idx+1, get_open_filename(line)))
                elif ( (open_file or with_open) and '.read' in line):
                    open_file = False
                    with_open = False
                elif (open_file and 'close(' in line):
                    # closing an openfile used for writing
                    output_files.append(t)
                    open_file = False
                
        return output_files

    def mine_files(self):
        ## Probably move to another unit/class.
        ## Try to id the entry point file based on the identified language.
        ## Requires Iterating again, which makes this slow.
        yaml_dict = [{'language' : 'Python'}]
        comments = []
        data_files = set()
        docker = None
        imports = set()
        mainfiles = [] 
        output_files = set() # organize by source, output_file path
        readmes = []
        urls = set()
        
        root_dirs = ()
        for root, dirs, files in os.walk(self.repo_path):
            if root == self.repo_path:
                # Mechanism in get_imports to ignore local libraries based on 
                # directories in path root folder. Also add "." to the list and 
                # converted to a tuple to be used with str.startswith.
                root_dirs = dirs
                root_dirs.append('.')
                root_dirs = tuple(root_dirs)           
                
            for file in files:
                filename, file_ext = os.path.splitext(file) 
                full_filename = root + self.sep + file
                
                if file_ext == '.py':
                    if util.textfile_contains(full_filename, "__name__ == \"__main__\""):
                        mainfiles.append(full_filename)
                                       
                    # Collate all imports                    
                    imports.update(self.get_imports(full_filename, root_dirs))
    
                    # output files
                    temp_list = self.get_output(full_filename)
                    if temp_list:
                        output_files.update(temp_list)
    
                    # urls
                    temp_list = util.get_urls(full_filename)
                    if temp_list:
                        urls.update(temp_list) 
                        
                    # file_names
                    data_files.update(util.get_filenames(full_filename))
                
                    # comments
                    comments.append({file: util.get_comments(full_filename) })
                
                elif file == 'Dockerfile':
                    docker = dict(docker_entrypoint=dminer.report_dockerfile(full_filename))
                    
                elif file.lower().startswith('readme'):
                    
                    # load entire readme until a better desription is generated
                    with open(full_filename, 'rt', encoding='utf8') as readme_file:
                        readmes.append({ full_filename: readme_file.read()})
                        
                    # add urls, then further processing
                    temp_list = util.get_urls(full_filename)
                    if temp_list:
                        urls.update(temp_list)           
                        
                    # file_names
                    data_files.update(util.get_filenames(full_filename))
        
        ## Report .py files, Remove common path from filenames and output.
        print('\t', len(mainfiles), '.py files with __main__ found:')
        cp = util.commonprefix(mainfiles)
        mainfiles = list(map(lambda s: s.replace(cp,''), mainfiles ))
        for f in mainfiles:
            print('\t\t' + f)
                                    
        ## Report imports and model types.        
        model_types = sorted(util.get_model_types_from_libraries(imports, self.sep, 'Python'))
        print('\tmodel types:', model_types)
        
        
        imports = sorted(imports)
        print('\t', len(imports), 'import(s) found:')        
        print('\t\t', end='')
        for i in imports:
            print(i, end=' ')
        print() 
          
        ## Report output files, a set of tuples.
        ## Remove common path from source files in output_files
        output_files = util.replace_cp_in_tuple_set(output_files, cp)
        print('\t', len(output_files), 'output file(s) found:')        
        for i in output_files:  
            print('\t\t', i)
        print() 
                            
        ## Report urls.
        #urls = sorted(urls)
        print('\t', len(urls), 'url(s) found:')        
        for i in urls:
            print('\t\t', i)
        print() 
        
        ## Remove common path from readme filenames.
        readmes = util.replace_cp_in_dict_list(readmes, cp)
    
        
        # Call Git REST API to get owner info and About description.        
        owner_info = repominer.extract_owner(self.repo_path)
        yaml_dict.append(dict(owner=owner_info))
        
        about_desc = repominer.extract_about(self.repo_path, self.repo_name)
        yaml_dict.append(dict(about=about_desc))
        
        
        if docker is None:
            yaml_dict.append(dict(docker_entrypoint=None))
        else:
            yaml_dict.append(docker)
        
        yaml_dict.append(dict(model_types=model_types))
        yaml_dict.append(dict(imports=imports))
        yaml_dict.append(dict(main_files=mainfiles))
        yaml_dict.append(dict(data_files=sorted(data_files)))
        yaml_dict.append(dict(output_files=util.group_tuple_pairs(output_files)))  
        yaml_dict.append(dict(urls=util.group_tuple_pairs(urls)))      
        yaml_dict.append(dict(readmes=readmes))
        yaml_dict.append(dict(comments=comments))
        
        # Write yaml file using utility to control newlines in comments.
        util.yaml_write_file(os.path.basename(self.repo_name), yaml_dict)
        

            
            
            
"""          
line = 'from git import RemoteProgress, Repo'
line = 'import modules.getcomments as getcomments'
line = 'from itertools import groupby'
sa = line.split()
print(sa[3:])
for l in sa[3:]:
    print(sa[1] + '.' + l.strip(','))
"""                                  
            
            
            
            
            
            
            
            
            
            
            