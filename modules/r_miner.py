"""
Miner for R repos.

What is a Pirate's favorite letter?
You'd think it is R, but it would be the C.

"""

import os
import modules.utilities as util

class RRepoMiner:
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
                
                if file_ext == '.R':
                    if util.textfile_contains(full_filename, "commandArgs"):
                        mainfiles.append(full_filename)
                    # check for external data calls, downloads, API calls
                    # wget, request, https specific to R
                
                if file == 'Dockerfile':
                    self.report_dockerfile(full_filename)
        
        
        print('\t', len(mainfiles), '.R files with commandArgs found:')
        
        # Remove common path from filenames and output.
        cp = util.commonprefix(mainfiles)
        for f in mainfiles:
            print('\t\t' + f.replace(cp,''))
            
            
    def report_dockerfile(self, full_filename):
        # Report DockerFile if it contains ENTRYPOINT in uppercase.
        with open(full_filename) as f:
            for line in f:
                if 'ENTRYPOINT' in line:
                    print('\tDockerfile found with ENTRYPOINT:', full_filename)
                    print('\t\t', line)
                    return