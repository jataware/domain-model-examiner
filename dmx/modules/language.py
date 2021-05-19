"""

  Language Identifier

"""

import os


languages = {'.py': 'Python',
       '.R': 'R',
       '.java': 'Java',
       '.c': 'C',
       '.cs':'C#',
       '.cpp': 'C++',
       '.rb': 'Ruby',
       '.php': 'PHP',
       '.pas': 'Pascal',
       '.pl': 'Perl',
       '.f': 'Fortran',
       '.go': 'Go',
       '.jl': 'Julia'
       }

def detect_language(repo_path):
  ### Iterate repo to get counts by file extension.
  counts = {}
  for root, dirs, files in os.walk(repo_path):
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
      #print ("\twritten in {0}, {1} {2} file(s).".format(languages[key], counts[key], key ));
      return key
  else:
    #print ("\tlanguage not detected.");
    return None





