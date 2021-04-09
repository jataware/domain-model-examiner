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
        

    def get_imports(self, filename):
        """
        Return unique set of imports.
        Improvement would be to ignore the repo's units.
        """
        imports = set()
        with open(filename) as f:
            for line in f:
                if line.startswith('import'):
                    imports.add(line.split()[1].split('.')[0])
    
        return imports


    def mine_files(self):
        ## Probably move to another unit/class.
        ## Try to id the entry point file based on the identified language.
        ## Requires Iterating again, which makes this slow.
        mainfiles = []
        imports = set()
        urls = set()
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                filename, file_ext = os.path.splitext(file) 
                full_filename = root + '\\' + file
                
                if file_ext == '.py':
                    if util.textfile_contains(full_filename, "__name__ == \"__main__\""):
                        mainfiles.append(full_filename)
                   
                    # check for external data calls, downloads, API calls
                    # wget, request, https
                    
                    # report any urls
                    
                    # Collate all imports                    
                    imports.update(self.get_imports(full_filename))
    
                    # urls
                    urls.update(util.get_urls(full_filename))
                
                if file == 'Dockerfile':
                    dminer.report_dockerfile(full_filename)
        
        
        # Report .py files, Remove common path from filenames and output.
        print('\t', len(mainfiles), '.py files with __main__ found:')
        cp = util.commonprefix(mainfiles)
        for f in mainfiles:
            print('\t\t' + f.replace(cp,''))
            
        # Report imports.
        imports = sorted(imports)
        print('\t', len(imports), 'import(s) found:')        
        print('\t\t', end='')
        for i in imports:
            print(i, end=' ')
        print()                               
        
        # Report urls.
        urls = sorted(urls)
        print('\t', len(urls), 'url(s) found:')        
        for i in urls:
            print('\t\t', i)
        print() 
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            