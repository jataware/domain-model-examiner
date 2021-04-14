"""

Miner for Python repos.

"""

import os
import modules.utilities as util
import modules.docker_miner as dminer
import modules.repo_miner as repominer


class PyRepoMiner:
    """
    Python-specific repo miner.
    """
    def __init__(self, repo):
        self.repo_path = repo

        if os.name == 'nt':
            self.sep = '\\'
        else:
            self.sep = '/'        
            
        self.mine_files()
       
        
    def get_imports(self, filename):
        """
        Return unique set of imports.
        Improvement would be to ignore the repo's units.
        
        TODO: parse command-delimited imports
        """
        imports = set()
        with open(filename, 'r', encoding="utf8") as f:
            for line in f:
                if line.startswith('import'):
                    imports.add(line.split()[1].split('.')[0])
    
        return imports


    def mine_files(self):
        ## Probably move to another unit/class.
        ## Try to id the entry point file based on the identified language.
        ## Requires Iterating again, which makes this slow.
        yaml_dict = [{'language' : 'Python'}]
        docker = None
        comments = []
        imports = set()
        mainfiles = []        
        urls = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                filename, file_ext = os.path.splitext(file) 
                full_filename = root + self.sep + file
                
                if file_ext == '.py':
                    if util.textfile_contains(full_filename, "__name__ == \"__main__\""):
                        mainfiles.append(full_filename)
                                       
                    # Collate all imports                    
                    imports.update(self.get_imports(full_filename))
    
                    # urls
                    url_list = util.get_urls(full_filename)
                    if url_list:
                        urls.extend(url_list) 
                
                    # comments
                    comments.append({file: util.get_comments(full_filename) })
                
                elif file == 'Dockerfile':
                    docker = dict(docker_entrypoint=dminer.report_dockerfile(full_filename))
                    
                elif file.lower().startswith('readme'):
                    # add urls, then further processing
                    url_list = util.get_urls(full_filename)
                    if url_list:
                        urls.extend(url_list)                
        
        ## Report .py files, Remove common path from filenames and output.
        print('\t', len(mainfiles), '.py files with __main__ found:')
        cp = util.commonprefix(mainfiles)
        mainfiles = list(map(lambda s: s.replace(cp,''), mainfiles ))
        for f in mainfiles:
            print('\t\t' + f)
                                    
        ## Report imports.
        imports = sorted(imports)
        print('\t', len(imports), 'import(s) found:')        
        print('\t\t', end='')
        for i in imports:
            print(i, end=' ')
        print()                 
                    
        ## Report urls.
        #urls = sorted(urls)
        print('\t', len(urls), 'url(s) found:')        
        for i in urls:
            print('\t\t', i)
        print() 
        
        ## Append Yaml dictionary.   
        owner_info = repominer.report_owner(self.repo_path)
        yaml_dict.append(dict(owner=owner_info))
        
        if docker is None:
            yaml_dict.append(dict(docker_entrypoint=None))
        else:
            yaml_dict.append(docker)
        
        yaml_dict.append(dict(imports=imports))
        yaml_dict.append(dict(main_files=mainfiles))
        yaml_dict.append(dict(urls=util.group_urls(urls)))        
        yaml_dict.append(dict(comments=comments))
        
        # Write yaml file using utility to control newlines in comments.
        util.yaml_write_file(os.path.basename(self.repo_path), yaml_dict)
        

            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            