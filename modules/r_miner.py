"""
Miner for R repos.

What is a Pirate's favorite letter?
You'd think it is R, but it would be the C.

"""

import os
import modules.utilities as util
import modules.docker_miner as dminer
import modules.repo_miner as repominer
import re

class RRepoMiner:
    """
    R-specific repo miner.
    """
    def __init__(self, repo_path, repo_name):
        self.repo_path = repo_path
        self.repo_name = repo_name

        if os.name == 'nt':
            self.sep = '\\'
        else:
            self.sep = '/'           

        self.mine_files()
        
        
    def get_libraries(self, filename):
        """
        Return set of libraries.
        
        Examples:
            
        * install.packages("tidyr", repos = repo)
        
        * library(tidyr)
        
        * x<-c("plyr", "psych", "tm")
        * lapply(x, require, character.only = TRUE)
        
        * lapply(c("gganimate", "tidyverse", "gapminder"), require, character.only = TRUE)
        
        * if easypackages is installed:
        ** packages("dplyr", "ggplot2", "RMySQL", "data.table")
        ** my_packages <- c("dplyr", "ggplot2", "RMySQL", "data.table")
        ** libraries(my_packages)
        **libraries("dplyr", "ggplot2", "RMySQL", "data.table")
        
        """
        libraries = set()
        with open(filename, 'r', encoding="utf8") as f:
            for line in f:
                if line.startswith('library') or line.startswith('install.packages'): 
                    library = line.strip().split('(')[1].split(',')[0].split(')')[0]
                    libraries.add(library.strip('"'))
    
        return libraries
        
    
    
    def get_output(self, filename):
        """
        R-specific
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
                    
                    t = (filename, "ln {0:>4}: obj: {1}; partial path: {2}".format(idx+1, object_name, ''.join(quoted_stuff)))
                    
                    output_files.append(t)
        return output_files
                
                    
    
    def mine_files(self):
        ## Probably move to another unit/class.
        ## Try to id the entry point file based on the identified language.
        ## Requires Iterating again, which makes this slow.
        yaml_dict = [{'language' : 'R'}]
        comments = []        
        data_files = set()
        docker = None
        libraries = set()
        mainfiles = []
        output_files = set() # organize by source, output_file path
        readmes = []
        urls = set()
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                filename, file_ext = os.path.splitext(file) 
                full_filename = root + self.sep + file
                
                if file_ext == '.R':
                    if util.textfile_contains(full_filename, "commandArgs"):
                        mainfiles.append(full_filename)
                
                    # Collate all libraries                    
                    libraries.update(self.get_libraries(full_filename))
                    
                    # output files
                    temp_list = self.get_output(full_filename)
                    if temp_list:
                        output_files.update(temp_list)
                    
                    # urls
                    temp_list = util.get_urls(full_filename)
                    if temp_list:
                        urls.update(temp_list)  
                    
                    # comments
                    comments.append({file: util.get_comments(full_filename) })
                    
                    # file_names
                    data_files.update(util.get_filenames(full_filename))
                    
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
                    util.get_filenames(full_filename)       
                    
                    # file_names
                    data_files.update(util.get_filenames(full_filename))
                    
        
        print('\t', len(mainfiles), '.R files with commandArgs found:')
        
        ## Remove common path from filenames and output.
        cp = util.commonprefix(mainfiles)
        mainfiles = list(map(lambda s: s.replace(cp,''), mainfiles ))
        for f in mainfiles:
            print('\t\t' + f)
            
        ## Report imports and model types.        
        model_types = sorted(util.get_model_types_from_libraries(libraries, self.sep, 'R'))
        print('\tmodel types:', model_types)
                    
        ## Report libraries.
        libraries = sorted(libraries)
        print('\t', len(libraries), 'libraries found:')        
        print('\t\t', end='')
        for l in libraries:
            print(l, end=' ')
        print()    
            
        ## Report output files, a set of tuples.
        ## Remove common path from source files in output_files
        output_files = util.replace_cp_in_tuple_set(output_files, cp)
        print('\t', len(output_files), 'output file(s) found:')        
        for i in output_files:  
            print('\t\t', i)
        print() 
        
        ## Report urls.
        print('\t', len(urls), 'url(s) found:')        
        for i in urls:            
            print('\t\t', i)
        print() 
        
        ## Remove common path from readme and about (same as readme) filenames.
        readmes = util.replace_cp_in_dict_list(readmes, cp)        

        ## Append Yaml dictionary and write to file.

        # Call Git REST API to get owner info and About description.        
        owner_info = repominer.extract_owner(self.repo_path)
        yaml_dict.append(dict(owner=owner_info))
        
        about_desc = repominer.extract_about(self.repo_path, self.repo_name)
        yaml_dict.append(dict(about=about_desc))
        
        yaml_dict.append(dict(about=None))
                
        if docker is None:
            yaml_dict.append(dict(docker_entrypoint=None))
        else:
            yaml_dict.append(docker)
            
        yaml_dict.append(dict(model_types=model_types))            
        yaml_dict.append(dict(libraries=libraries))
        yaml_dict.append(dict(main_files=mainfiles))
        yaml_dict.append(dict(data_files=sorted(data_files)))
        yaml_dict.append(dict(output_files=util.group_tuple_pairs(output_files)))   
        yaml_dict.append(dict(urls=util.group_tuple_pairs(urls)))   
        yaml_dict.append(dict(readmes=readmes))
        yaml_dict.append(dict(comments=comments))
        
        ## Write yaml file using utility to control newlines in comments.
        util.yaml_write_file(os.path.basename(self.repo_name), yaml_dict)
        
