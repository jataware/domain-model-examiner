# -*- coding: utf-8 -*-
"""
Get project owner info.
"""

import requests
from git import RemoteProgress, Repo
import os
import shutil, stat
import sys


class ProgressPrinter(RemoteProgress):
    """Class that implements progress reporting."""
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            percentage = '%.0f' % (100 * cur_count / (max_count or 100.0))
            sys.stdout.write('Downloaded %s%% %s \r' % (percentage, message))
            #sys.stdout.write('update(%s, %s, %s, %s) \r'%(op_code, cur_count, max_count, message))

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
    shutil.rmtree('tmp', onerror=remove_readonly)


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def extract_about(repo_path, repo_name):
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

def extract_owner(file):
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


