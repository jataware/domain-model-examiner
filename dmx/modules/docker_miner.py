# -*- coding: utf-8 -*-
"""
Find any useful goodies in DockerFile
"""

def report_dockerfile(filename):
  """
  Report DockerFile if it contains ENTRYPOINT in uppercase.
  """
  with open(filename) as f:
    for line in f:
      if 'ENTRYPOINT' in line:
        #print('\tDockerfile found with ENTRYPOINT:', filename)
        #print('\t\t', line.strip())
        return line.strip()
