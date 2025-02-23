# Slowbeast with concurrency

Tool used to detect data race in C programs. Uses symbolic execution and SDPOR algorithm for concurent analysis. Originally created by Marek Chalupa, in FORMELA, Faculty of Informatics, Masaryk University as a playground for symbolic execution. This fork allows for handling multi-threaded C programs. It's a work in progress, focussing on data race detection for now. But other tasks like reach safety and overflow detection should come for free with it. Soon :)  

## TODO

- Setup unit tests.
- Fix incorrect results.
- Identify atomic instructions
- Refactor for comprehension.
- Add an explainer doc for SDPOR, understanding trace, etc.
- Get going atomic.
- Add reference to thesis.
- Mark the specific files and classes to be used for understanding the work.

## Get Started

Run the `./get-started.sh` script. It builds the docker container and runs a container with the current directory mounted.

## How to use:

- Running the `./get-started.sh` creates a bash terminal inside the docker container (tagged: `slowbeastnodatarace:latest`). This is considered the default mode of operation. Files created outside the container can be edited from inside **but vice versa is not true**. Only create files from outside the container, which is also the more convenient option. The only files the container should create are the `program.ll` files which are the translation of the input program into llvm, that is then used for analysis.
- The `sb-main` is the main entrypoint of all the analysis. Simple `sb-main input-file.c` should default to using the right parameters. The line `Data Race Found: False` is the main value to be read. It will be printed regardless of the completion of analysis so the final result is only valid if there are no known states. (TODO: clearly indicate unknown result when that is the case)
- `benchexec-dir\slowbeast.py` is the main file that will evaluate the output of the `sb-main <input file>` command when running [benchexec](https://github.com/sosy-lab/benchexec). 


## Requirements

- While docker is not mandatory, it is advised for quick and easy deployment, even for development etc.
- Refer the Docker image file and the `install-llvmlite.sh` script for replicating a local build. The latter is the script run as soon as the image is built and the current drive is mounted.

## Docker debug commands

`docker run --rm -it -v "$PWD":/app -w /app slowbeastnodatarace:latest bash`

`docker compose exec slowbeast /bin/bash`

`docker compose run --service-ports --rm slowbeast /bin/bash`
