# -*- coding: utf-8 -*-
"""
Get project owner info.
"""

import requests
from git import RemoteProgress, Repo
import os
import shutil, stat
import sys

# #######
# Classes
# #######

class ProgressPrinter(RemoteProgress):
  """Class that implements progress reporting."""
  def update(self, op_code, cur_count, max_count=None, message=''):
    if message:
      percentage = '%.0f' % (100 * cur_count / (max_count or 100.0))
      sys.stdout.write('Downloaded %s%% %s \r' % (percentage, message))
      #sys.stdout.write('update(%s, %s, %s, %s) \r'%(op_code, cur_count, max_count, message))


# ###############
# General Methods
# ###############

def clone_repo(url):
  # Take out the garbage.
  if os.path.exists('tmp'):
    delete_repo()

  # Pile up the new garbage.
  os.mkdir('tmp')
  print('Cloning ' + url)
  Repo.clone_from(url, 'tmp', progress=ProgressPrinter())


def delete_repo():
  """
  Remove existing tmp dir. Uses stat library and remove_readonly() to handle
  read-only git folders.

  """
  shutil.rmtree('tmp', onerror=remove_readonly_permissions)


def extract_about(url, repo_path, repo_name):
  if url is None or 'github' in url:
    return github_extract_about(repo_path, repo_name)
  elif 'gitlab' in url:
    return gitlab_extract_about(repo_path, repo_name)


def extract_owner(url, repo_path):
  if url is None or 'github' in url:
    return github_extract_owner(repo_path)
  elif 'gitlab' in url:
    return gitlab_extract_owner(repo_path)


def remove_readonly_permissions(func, path, excinfo):
  os.chmod(path, stat.S_IWRITE)
  func(path)


# #######################
# GitHub-specific Methods
# #######################

def github_extract_about(repo_path, repo_name):
  try:
    r = Repo(repo_path)
    repo_owner = r.remotes.origin.url.split('.git')[0].split('/')[-2]

    endpoint = "https://api.github.com/repos/{0}/{1}".format(repo_owner, repo_name)
    response = requests.get(endpoint)

    resp = response.json()

    if "description" in resp:
      return resp['description']
    else:
      # github sometimes gets uppity about banging on their api.
      print ('repo description / about not found', response.text)
    return 'not found'
  except:
     return 'Not a valid git repository.'


def github_extract_owner(file):
  try:
    r = Repo(file)
    repo_owner = r.remotes.origin.url.split('.git')[0].split('/')[-2]

    response = requests.get("https://api.github.com/users/" + repo_owner)
    user = response.json()

    if "login" in user:
      return [{'login' : user['login']},
          {'repo_url' : r.remotes.origin.url },
          {'type' : user['type']},
          {'name' : user['name']},
          {'company' : user['company']},
          {'blog' : user['blog']},
          {'location' : user['location']},
          {'bio' : user['bio']} ]
    else:
      # github sometimes gets uppity about banging on their api.
      print (response.text)
      return 'Error connecting to GitHub API'
  except:
    return 'Not a valid git repository.'


# #######################
# GitLab-specific Methods
# #######################

def gitlab_extract_about(repo_path, repo_name):
  try:
    r = Repo(repo_path)
    repo_owner = r.remotes.origin.url.split('.git')[0].split('/')[-2]

    endpoint = "https://gitlab.com/api/v4/projects/{0}%2F{1}".format(repo_owner, repo_name)
    response = requests.get(endpoint)

    resp = response.json()

    if "description" in resp:
      return resp['description']
    else:
      # gitlab probably gets uppity sometimes about banging on their api.
      print ('repo description / about not found', response.text)
    return 'not found'
  except:
     return 'Not a valid git repository.'

def gitlab_extract_owner(file):
  try:
    r = Repo(file)
    repo_owner = r.remotes.origin.url.split('.git')[0].split('/')[-2]

    response = requests.get("https://gitlab.com/api/v4/users?username=" + repo_owner)

    # returns a list of json objects
    user = response.json()

    if user is not None and len(user) > 0 and "id" in user[0]:
      # Don't know how to get the project_id from the repo, so using first call.
      project_id = user[0]["id"]

      # Make call to 2nd endpoint to get more complete info.
      response = requests.get("https://gitlab.com/api/v4/users/" +  str(project_id))
      user = response.json()

      if 'username' in user:
        return [{'username' : user['username']},
            {'name' : user['name']},
            {'repo_url' : r.remotes.origin.url },
            {'organization' : user['organization']},
            {'job_title' : user['job_title']},
            {'website_url' : user['website_url']},
            {'location' : user['location']},
            {'bio' : user['bio']} ]
      else:
        print (response.text)
        return 'Error connecting to GitLab API'
    else:
      # gitlab probably gets uppity sometimes about banging on their api.
      print (response.text)
      return 'Error connecting to GitLab API'
  except Exception as e:
    print(e)
    return 'Not a valid git repository.'



