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

def report_owner(file):
    r = Repo(file)
    repo_owner = r.remotes.origin.url.split('.git')[0].split('/')[-2]
    
    response = requests.get("https://api.github.com/users/" + repo_owner)
    user = response.json()
    
    if user['login']:
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
        return response.json
    
    
    
