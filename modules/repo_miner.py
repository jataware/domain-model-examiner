# -*- coding: utf-8 -*-
"""
Get project owner info.
"""

import requests
from git import Repo

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
    