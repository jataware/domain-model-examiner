"""
DMX API

This is copied to main.py by the Dockerfile.
"""

from fastapi import FastAPI

import os

import modules.arbitrary_miner as arbminer
import modules.julia_miner as julieminer
import modules.language as language
import modules.python_miner as pyminer
import modules.r_miner as rminer
import modules.repo_miner as repo_miner
import modules.utilities as util


tags_metadata = [
    {
        "name": "examine",
        "description": "Pass the GitHub repo url here e.g. examine/?url=https://github.com/jataware/dummy-model.git",
    },
    {
        "name": "root",
        "description": "Confirms the beast is alive.",
    },
]

app = FastAPI(
    title="Domain Model eXaminer",
    description="Performs machine reading over the model codebase in order to automatically extract key metadata.",
    version="0.0.1",
    openapi_tags = tags_metadata
    )


@app.get("/", tags=["root"])
def read_root():
    return {"status": "running"}

@app.get("/examine/", tags=["examine"])
async def get_examination(url):
    yaml_dict = None

    repo_miner.clone_repo(url)
    repo_name = os.path.splitext(os.path.basename(url))[0]

    lang = language.detect_language('tmp')

    if (lang == '.py'):
        yaml_dict = pyminer.PyRepoMiner('tmp', repo_name).yaml_dict
    elif (lang == '.R'):
        yaml_dict= rminer.RRepoMiner('tmp', repo_name).yaml_dict
    elif (lang == '.jl'):
        yaml_dict = julieminer.JuliaRepoMiner('tmp', repo_name).yaml_dict
    else:
        yaml_dict = arbminer.ArbitraryRepoMiner('tmp', repo_name, lang).yaml_dict

    repo_miner.delete_repo()

    return util.yaml_dump(yaml_dict)



