"""

    Language Identifier

"""

import os

languages = {'.py': 'Python', '.R': 'R', '.java': 'Java'}


def commonprefix(args, sep="\\"):
    return os.path.commonprefix(args).rpartition(sep)[0]

def contains(filename, marker):
    with open(filename, 'r') as file:
        text = file.read();
        if marker in text:
            return True        
    return False

class Language:
    """
        Language Identification class called form main.py.
    """
    
    def __init__(self, repo):
        self.repo_path = repo                
                    
    
    def mine_files(self, lang):
        ### Try to id the entry point file based on the identified language.
        ## Requires Iterating again, which makes this slow.
        mainfiles = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                filename, file_ext = os.path.splitext(file) 
                full_filename = root + '\\' + file
                
                if file_ext == lang and lang == '.py':
                    if contains(full_filename, "__name__ == \"__main__\""):
                        mainfiles.append(full_filename)
                    # check for external data calls, downloads, API calls
                    # wget, request, https
                elif file_ext == lang and lang == '.R':
                    if contains(full_filename, "commandArgs"):
                        mainfiles.append(full_filename)
                    # check for external data calls, downloads, API calls
                    # wget, request, https specific to R
                
                if file == 'Dockerfile':
                    self.report_dockerfile(full_filename)
        
        if (lang == '.py'):
            print('\t', len(mainfiles), '.py files with __main__ found:')
        elif (lang == '.R'):
            print('\t', len(mainfiles), '.R files with commandArgs found:')
        else:
            return
        
        # Remove common path from filenames and output.
        cp = commonprefix(mainfiles)
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
                
    
    def report_metrics(self):
        lang_ext = self.report_language()
        if lang_ext != None:
            self.mine_files(lang_ext)
    
   
    def report_language(self):           
        ### Iterate repo to get counts by file extension.
        counts = {}            
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                # Get file extension counts.
                filename, file_ext = os.path.splitext(file)                      
                if file_ext in counts:
                    counts[file_ext] += 1
                else:
                    counts[file_ext] = 1
                
        ### Process file extension counts.
        ### Reduce the counts to only the languages in which we are interested.
        counts = {k: counts[k] for k in counts.keys() & languages.keys()}
                
        ### Sort descending.
        counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))        
        
        ### Report the language, or not found. 
        if len(counts.values()) > 0:
            for key, value in counts.items():                    
                print ("\twritten in {0}, {1} {2} file(s).".format(languages[key], counts[key], key ));  
                return key
        else:
            print ("\tlanguage not detected.");
            return None
         
    
   

         
       