"""
    World Modelers Domain Model Examiner (DMX) - repo install / startup automaton

    **Overview**:
    Look at ~5 github repositories or codebases to try to identify:

    1. `language`
    2. execution command
    3. OS requirements
    4. hardware requirements
    5. settings files
    6. external data calls, API calls, downloads, etc.

    > We want to identify any piece of information that can be _automatically_ extracted and would be useful to installing, setting up, and running a model

    **Repos to examine**:

    1. https://github.com/jataware/dummy-model
    2. https://github.com/djgroen/FabFlee
    3. https://github.com/jataware/maxhop
    4. https://github.com/DSSAT/pythia/tree/develop [`develop` branch]
    5. https://github.com/mjpuma/FSC-WorldModelers

    > Note that Pythia is a highly abstracted Python version of the [DSSAT model](https://github.com/DSSAT/dssat-csm-os).

    **Other**:

    1. Are there other projects that do this well?
    2. Can we extract model descriptions, parameter descriptions, input/output descriptions from the documentation or code?



    **Initial logic flow**
        1. clone repo or otherwise acquire codebase (pass location as parameter)
        2. iterate path to identify language based on file extension
        3. confirm lanugage and main file based on known language execution methods
"""

import argparse
import json
import os
import modules.arbitrary_miner as arbminer
import modules.julia_miner as julieminer
import modules.language as language
import modules.python_miner as pyminer
import modules.r_miner as rminer
import modules.repo_miner as repo_miner
import modules.utilities as util


def main():
    parser = argparse.ArgumentParser(
        description='Domain Model Examiner (DMX) mines codebases to semi-automate installation and execution',
        epilog='Good luck.'
        )
    parser.add_argument('--repo', help="GitHub repo path in double quotes")
    parser.add_argument('--url',  help="GitHub repo URL in double quotes")
    args = parser.parse_args()

    repos = []
    url = None
    if args.url is not None:
        url = args.url
    elif args.repo is not None:
        repos.append(args.repo)
    else:
        # resort to reading from parameters.json
        params = open('parameters.json').read()
        params = json.loads(params)
        for repo in params['repositories']:
            repos.append(repo['path'])

    if url is not None:
        try:
            yaml_dict_list = []
            repo_miner.clone_repo(url)
            repo_name = os.path.splitext(os.path.basename(url))[0]

            # Call language-specific mining to append to yaml_dict_list
            lang = language.detect_language('tmp')
            if (lang == '.py'):
                yaml_dict_list = pyminer.PyRepoMiner('tmp', repo_name).yaml_dict
            elif (lang == '.R'):
                yaml_dict_list = rminer.RRepoMiner('tmp', repo_name).yaml_dict
            elif (lang == '.jl'):
                yaml_dict_list = julieminer.JuliaRepoMiner('tmp', repo_name).yaml_dict
            else:
                yaml_dict_list = arbminer.ArbitraryRepoMiner('tmp', repo_name, lang).yaml_dict

            # Call Repominer to get owner info and About descriptions.
            owner_info = repo_miner.extract_owner(url, 'tmp')
            yaml_dict_list.insert(1, dict(owner=owner_info))

            about_desc = repo_miner.extract_about(url, 'tmp', repo_name)
            yaml_dict_list.insert(2, dict(about=about_desc))

            # Write yaml file using utility to control newlines in comments.
            util.yaml_write_file(repo_name, yaml_dict_list)

            repo_miner.delete_repo()

        except Exception as e:
            print(e)
    else:
        for repo in repos:
            yaml_dict_list = []
            lang = language.detect_language(repo)
            repo_name = os.path.basename(repo)

            if (lang == '.py'):
                 yaml_dict_list = pyminer.PyRepoMiner(repo, repo_name).yaml_dict
            elif (lang == '.R'):
                 yaml_dict_list = rminer.RRepoMiner(repo, repo_name).yaml_dict
            elif (lang == '.jl'):
                 yaml_dict_list = julieminer.JuliaRepoMiner(repo, repo_name).yaml_dict
            else:
                 yaml_dict_list = arbminer.ArbitraryRepoMiner(repo, repo_name, lang).yaml_dict

            # Call Repominer to get owner info and About descriptions.
            # Assumes these are GitHub repos for local repos.
            owner_info = repo_miner.extract_owner(None, 'tmp')
            yaml_dict_list.insert(1, dict(owner=owner_info))

            about_desc = repo_miner.extract_about(None, 'tmp', repo_name)
            yaml_dict_list.insert(2, dict(about=about_desc))

            # Write yaml file using utility to control newlines in comments.
            print(repo_name)
            util.yaml_write_file(repo_name, yaml_dict_list)


if __name__ == "__main__":
    main()
