# Slowbeast

Playground for symbolic execution. Originally created by Marek Chalupa, in FORMELA, Faculty of Informatics, Masaryk University. This fork allows for handling multi-threaded C programs. It's a work in progress, focussing on data race detection for now. But other tasks like reach safety and overflow detection should come for free with it. Soon ;)  

It is intended to be developed further. thus the dockerisation (intends to) start the application as a development environment. Not as a ready to use container.

## TODO

- Make `-threads-dpor` default.
- Make history available inside docker. 

## How to build (Dev)

Run by mounting the pwd in the docker container.  

## Docker debug commands

`docker run --rm -it -v "$PWD":/app -w /app slowbeastnodatarace:latest bash`

`docker compose exec slowbeast /bin/bash`

`docker compose run --service-ports --rm slowbeast /bin/bash`
