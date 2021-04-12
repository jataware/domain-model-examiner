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

import argparse, json, os
import modules.language as language
import modules.python_miner as pyminer
import modules.r_miner as rminer



def main():
    parser = argparse.ArgumentParser(
        description='Domain Model Examiner (DMX) mines codebases to semi-automate installation and execution',
        epilog='Good luck.'
        
        )
    parser.add_argument('--repo', help="GitHub repo path in double quotes")
    args = parser.parse_args()
           
    repos = []
    if args.repo != None:
        repos.append(args.repo)
    else: 
        # resort to reading from parameters.json
        params = open('parameters.json').read()
        params = json.loads(params)
        for repo in params['repositories']:
            repos.append(repo['path'])

    for repo in repos:  
        print(os.path.basename(repo))
        lang = language.detect_language (repo)    
        
        if (lang == '.py'):
            pyminer.PyRepoMiner(repo)
        elif (lang == '.R'):
            rminer.RRepoMiner(repo)
        
        print()
        


if __name__ == "__main__":
    main()



