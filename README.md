# Slowbeast

Playground for symbolic execution. Originally created by Marek Chalupa, in FORMELA, Faculty of Informatics, Masaryk University. This fork allows for handling multi-threaded C programs. It's a work in progress, focussing on data race detection for now. But other tasks like reach safety and overflow detection should come for free with it. Soon ;)  

It is intended to be developed further. thus the dockerisation (intends to) start the application as a development environment. Not as a ready to use container.

## TODO

- Make `-threads-dpor` default.
- Make history available inside docker. 
- Setup unit tests.

## Get Started

Run the `./get-started.sh` script. It builds the docker container and runs a container with the current directory mounted.

## Requirements

- While docker is not mandatory, it is advised for quick and easy deployment, even for development etc.
- Refer the Docker image file and the `install-llvmlite.sh` script for replicating a local build. The latter is the script run as soon as the image is built and the current drive is mounted.

## Docker debug commands

`docker run --rm -it -v "$PWD":/app -w /app slowbeastnodatarace:latest bash`

`docker compose exec slowbeast /bin/bash`

`docker compose run --service-ports --rm slowbeast /bin/bash`
