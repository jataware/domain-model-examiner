"""

    Language Identifier

"""

import os

lang_ext = {'.py': 'Python', '.R': 'R', '.java': 'Java'}

class Language:
    """
        Language Identification class called form main.py.
    """
    
    def __init__(self, repo):
        self.repo_path = repo
                 
    def report_language(self):      
        ### Iterate repo to get counts by file extension.
        counts = {}            
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                
                filename, file_ext = os.path.splitext(file)      
                
                if file_ext in counts:
                    counts[file_ext] += 1
                else:
                    counts[file_ext] = 1
        
        ### Reduce the counts to only the languages in which we are interested.
        counts = {k: counts[k] for k in counts.keys() & lang_ext.keys()}
                
        ### Sort descending.
        counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))        
        
        ### Report the language, or not found. 
        if len(counts.values()) > 0:
            for key, value in counts.items():                    
                print ("written in {0}, {1} {2} file(s).\n".format(lang_ext[key], counts[key], key ));                
                break;
        else:
            print ("language not detected.\n");
            
         
       