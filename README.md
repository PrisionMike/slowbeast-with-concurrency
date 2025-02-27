# Slowbeast with concurrency

- Python SAST checker to detect possible data races in multi-threaded C programs.Uses [Partial order reduction](https://www.researchgate.net/publication/262352623_Optimal_Dynamic_Partial_Order_Reduction) in Symbolic execution. [Mgr. thesis project by Suyash Shandilya.](https://is.muni.cz/th/n9ib3/)

- [Originally](https://gitlab.com/mchalupa/slowbeast) created by Marek Chalupa at FORMELA, Faculty of Informatics, Masaryk University, as a playground for symbolic execution, this fork extends support for multi-threaded C programs. Currently a work in progress, it focuses on **data race detection**, with additional properties like **reachability analysis** and **overflow detection** expected to follow soon. 🙂
  

## Get Started

- Run the `./get-started.sh` script. It builds the docker container and runs a container with the current directory mounted.

## How to use:

- Running the `./get-started.sh` creates a bash terminal inside the docker container (tagged: `slowbeastnodatarace:latest`). This is considered the default mode of operation. 
- The `sb-main` is the main entrypoint of all the analysis. Simple `sb-main <input-file>` should default to using the right parameters. The line `Data Race Found: False` is the main value to be read. It will be printed regardless of the completion of analysis so the final result is only valid if there are no KILLED paths.
- TDD Friendly project. Refer to the [testing doc](docs/Testing.md) to get started.
<!-- - `benchexec-dir\slowbeast.py` is the main file that will evaluate the output of the `sb-main <input file>` command when running [benchexec](https://github.com/sosy-lab/benchexec).  -->


## Requirements

- While docker is not mandatory, it is recommended for convenience.
- Refer the Docker image file (Dockerfile) and the `install-llvmlite.sh` script for replicating a local build. The latter is the script run as soon as the image is built and the current drive is mounted.
