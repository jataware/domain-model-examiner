# domain-model-examiner
World Modelers Domain Model Examiner (DMX) - repo install / startup automaton

## Usage

First, run:

```
pip install -r requirements.txt
```

Then, clone or download the repository of interest. For example:

```
cd /tmp
git clone https://github.com/jataware/dummy-model.git
```

Next, analyze this repo with:

```
python main.py --repo="/tmp/dummy-model"
```

# research phase (Trello description)

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
