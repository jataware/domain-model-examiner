"""
Miner for R repos.

What is a Pirate's favorite letter?
You'd think it is R, but it would be the C.

"""

import os, yaml
import modules.utilities as util
import modules.docker_miner as dminer


class RRepoMiner:
    """
    R-specific repo miner.
    """
    def __init__(self, repo):
        self.repo_path = repo
        self.mine_files()
        
        
    def get_libraries(self, filename):
        """
        Return set of libraries.
        
        install.packages("tidyr", repos = repo)
        """
        libraries = set()
        with open(filename) as f:
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
        docker = None
        libraries = set()
        mainfiles = []
        urls = set()
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                filename, file_ext = os.path.splitext(file) 
                full_filename = root + '\\' + file
                
                if file_ext == '.R':
                    if util.textfile_contains(full_filename, "commandArgs"):
                        mainfiles.append(full_filename)
                    # check for external data calls, downloads, API calls
                    # wget, request, https specific to R
                
                     # Collate all libraries                    
                    libraries.update(self.get_libraries(full_filename))
                    
                    # urls
                    urls.update(util.get_urls(full_filename))
                    
                if file == 'Dockerfile':
                    docker = dict(docker_entrypoint=dminer.report_dockerfile(full_filename))
        
        
        print('\t', len(mainfiles), '.R files with commandArgs found:')
        
        # Remove common path from filenames and output.
        cp = util.commonprefix(mainfiles)
        mainfiles = list(map(lambda s: s.replace(cp,''), mainfiles ))
        for f in mainfiles:
            print('\t\t' + f)
            
            
        # Report libraries.
        libraries = sorted(libraries)
        print('\t', len(libraries), 'libraries found:')        
        print('\t\t', end='')
        for l in libraries:
            print(l, end=' ')
        print()    
            
        # Report urls.
        urls = sorted(urls)
        print('\t', len(urls), 'url(s) found:')        
        for i in urls:
            print('\t\t', i)
        print() 
   

   
        # Append Yaml dictionary and write to file.   
        
        if docker is None:
            yaml_dict.append(dict(docker_entrypoint=None))
        else:
            yaml_dict.append(docker)
            
        yaml_dict.append(dict(libraries=libraries))
        yaml_dict.append(dict(main_files=mainfiles))
        yaml_dict.append(dict(urls=urls))        
        with open('dmx-' + os.path.basename(self.repo_path) + '.yaml', 'w') as file:
            yaml.dump(yaml_dict, file)