"""
Miner for repos without a specific miner.

"""

import os
import modules.utilities as util
import modules.docker_miner as dminer
import modules.language as language

IGNORE_FILE_EXT = ['.txt','.html','.css','.json','xml','.csv','.pdf','.yml',
       '.yaml','.ini', '.png', '.store', '.mp3', '.jar', '.webp',
       '.so', '.pack', '','.db', '.idx', '.jks', '.cert', '.der',
       '.ogg', '.ttf']

class ArbitraryRepoMiner:
  """
  Non-specific repo miner.
  """
  def __init__(self, repo_path, repo_name, lang):
    self.repo_path = repo_path
    self.repo_name = repo_name
    self.lang = language.languages[lang] if lang != None else 'unknown'

    if os.name == 'nt':
      self.sep = '\\'
    else:
      self.sep = '/'

    self.mine_files()


  def mine_files(self):
     yaml_dict = [{'language' : self.lang}]
     data_files = set()
     docker = None
     output_files = set() # organize by source, output_file path
     readmes = []
     urls = set()

     for root, dirs, files in os.walk(self.repo_path):
       for file in files:
         filename, file_ext = os.path.splitext(file)
         full_filename = root + self.sep + file

         if file == 'Dockerfile':
           docker = dict(docker_entrypoint=dminer.report_dockerfile(
              full_filename))
         elif file.lower().startswith('readme'):
           # load entire readme until a better desription is generated
           with open(full_filename, 'r', encoding='utf8') as readme_file:
             readmes.append({ full_filename: readme_file.read()})
           # add urls, then further processing
           temp_list = util.get_urls(full_filename)
           if temp_list:
             urls.update(temp_list)
           # file_names
           data_files.update(util.get_filenames(full_filename))

         elif file_ext not in IGNORE_FILE_EXT:
           # urls
           temp_list = util.get_urls(full_filename)
           if temp_list:
             urls.update(temp_list)

           # file_names
           data_files.update(util.get_filenames(full_filename))

     ## Remove rep path from readme filenames.
     readmes = util.replace_cp_in_dict_list(readmes, self.repo_path)

     ## Append Yaml dictionary list.
     if docker is None:
       yaml_dict.append(dict(docker_entrypoint=None))
     else:
       yaml_dict.append(docker)

     yaml_dict.append(dict(data_files=sorted(data_files)))
     yaml_dict.append(dict(output_files=util.group_tuple_pairs(output_files)))
     yaml_dict.append(dict(urls=util.group_tuple_pairs(urls)))
     yaml_dict.append(dict(readmes=readmes))

     self.yaml_dict = yaml_dict
