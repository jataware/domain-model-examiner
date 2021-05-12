# Domain-Model-Examiner (DMX)

The goal of this process is to perform machine reading over the model codebase in order to automatically extract key metadata about:
- Input files
- Output files
- System requirements
- Software requirements
- Model entry points
- Model descriptions
- Maintainer information


## Installation

First, recommended installation is to create a new conda environment and then intall from requirements.txt:

```
conda create --name=dmx python=3.8
conda activate dmx
conda install uvicorn
pip install -r requirements.txt
```

Docker Install and Run
```
docker build -t dmx .
docker run -p 80:80 dmx
```

## Usage

#### List command line options
```
python main.py --help
```

#### Process Local Repository

Clone or download the repository of interest. For example:

```
cd /tmp
git clone https://github.com/jataware/dummy-model.git
```

Next, analyze this repo with:

```
python main.py --repo="/tmp/dummy-model"
```

#### Process Remote Repository

```
python main.py --url="https://github.com/jataware/dummy-model.git"
```

This creates and deletes a tempory folder 'tmp'.

#### Output

The application produces a .yaml file with prefix 'dmx-' concatenated with the repo name. 

## Running the API

Run API:
```
uvicorn api:app
http://127.0.0.1:8000/
```
Do not use --reload flag, since the app will download the repo to the api folder.


## Testing Repositories

* https://github.com/jataware/dummy-model
* https://github.com/djgroen/FabFlee
* https://github.com/jataware/maxhop
* https://github.com/DSSAT/pythia/tree/develop [`develop` branch]
* https://github.com/mjpuma/FSC-WorldModelers 


Note that Pythia is a highly abstracted Python version of the [DSSAT model](https://github.com/DSSAT/dssat-csm-os).
