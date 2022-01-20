# Dummy ASR Engine

Implementation of a dummy ASR engine using the tornado Python library.

## Create Conda Environment

```bash
$ conda env create --file server/environment.yml
$ conda activate tornado
```

## Run Websocket Server

```bash
$ cd server
$ python server.py --help
Usage: server.py [OPTIONS]

Options:
  -p, --port INTEGER
  --help              Show this message and exit.

$ python server.py -p 5000
2021-03-25 15:10:23,260 server INFO : Starting websocket server on port 5000
```
