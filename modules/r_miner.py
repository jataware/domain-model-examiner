"""
Miner for R repos.

What is a Pirate's favorite letter?
You'd think it is R, but it would be the C.

"""

import os
import modules.utilities as util
import modules.docker_miner as dminer
import modules.repo_miner as repominer

class RRepoMiner:
    """
    R-specific repo miner.
    """
    def __init__(self, repo):
        self.repo_path = repo

        if os.name == 'nt':
            self.sep = '\\'
        else:
            self.sep = '/'           

        self.mine_files()
        
        
    def get_libraries(self, filename):
        """
        Return set of libraries.
        
        install.packages("tidyr", repos = repo)
        """
        libraries = set()
        with open(filename, 'r', encoding="utf8") as f:
            for line in f:
                if line.startswith('library') or line.startswith('install.packages'): 
                    library = line.strip().split('(')[1].split(',')[0].split(')')[0]
                    libraries.add(library.strip('"'))
    
        return libraries
        
    
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
                    
                    # urls
                    url_list = util.get_urls(full_filename)
                    if url_list:
                        urls.update(url_list)  
                    
                    # comments
                    comments.append({file: util.get_comments(full_filename) })
                    
                    # file_names
                    data_files.update(util.get_filenames(full_filename))
                    
                elif file == 'Dockerfile':
                    docker = dict(docker_entrypoint=dminer.report_dockerfile(full_filename))
                    
                elif file.lower().startswith('readme'):
                    # load entire readme until a better desription is generated
                    with open(full_filename, 'rt', encoding='utf8') as readme_file:
                        readmes.append(readme_file.read())
                    
                    # add urls, then further processing                    
                    url_list = util.get_urls(full_filename)
                    if url_list:
                        urls.update(url_list)  
                    util.get_filenames(full_filename)       
                    
                    # file_names
                    data_files.update(util.get_filenames(full_filename))
                    
        
        print('\t', len(mainfiles), '.R files with commandArgs found:')
        
        ## Remove common path from filenames and output.
        cp = util.commonprefix(mainfiles)
        mainfiles = list(map(lambda s: s.replace(cp,''), mainfiles ))
        for f in mainfiles:
            print('\t\t' + f)
                    
        ## Report libraries.
        libraries = sorted(libraries)
        print('\t', len(libraries), 'libraries found:')        
        print('\t\t', end='')
        for l in libraries:
            print(l, end=' ')
        print()    
            
        ## Report urls.
        print('\t', len(urls), 'url(s) found:')        
        for i in urls:            
            print('\t\t', i)
        print() 
          
    
        ## Append Yaml dictionary and write to file.        
        owner_info = repominer.report_owner(self.repo_path)
        yaml_dict.append(dict(owner=owner_info))
                
        if docker is None:
            yaml_dict.append(dict(docker_entrypoint=None))
        else:
            yaml_dict.append(docker)
            
        yaml_dict.append(dict(libraries=libraries))
        yaml_dict.append(dict(main_files=mainfiles))
        yaml_dict.append(dict(data_files=sorted(data_files)))
        yaml_dict.append(dict(urls=util.group_urls(urls)))   
        yaml_dict.append(dict(readmes=readmes))
        yaml_dict.append(dict(comments=comments))
        
        ## Write yaml file using utility to control newlines in comments.
        util.yaml_write_file(os.path.basename(self.repo_path), yaml_dict)
        
