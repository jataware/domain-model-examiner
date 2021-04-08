"""

Miner for Python repos.

"""

import os
import modules.utilities as util
import modules.docker_miner as dminer

class PyRepoMiner:
    """
    Python-specific repo miner.
    """
    def __init__(self, repo):
        self.repo_path = repo
        self.mine_files()
        

    def mine_files(self):
        ## Probably move to another unit/class.
        ## Try to id the entry point file based on the identified language.
        ## Requires Iterating again, which makes this slow.
        mainfiles = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                filename, file_ext = os.path.splitext(file) 
                full_filename = root + '\\' + file
                
                if file_ext == '.py':
                    if util.textfile_contains(full_filename, "__name__ == \"__main__\""):
                        mainfiles.append(full_filename)
                   
                    # check for external data calls, downloads, API calls
                    # wget, request, https
 
                
                if file == 'Dockerfile':
                    dminer.report_dockerfile(full_filename)
        
        
        print('\t', len(mainfiles), '.py files with __main__ found:')
        
        # Remove common path from filenames and output.
        cp = util.commonprefix(mainfiles)
        for f in mainfiles:
            print('\t\t' + f.replace(cp,''))