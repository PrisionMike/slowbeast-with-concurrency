# Slowbeast

Playground for symbolic execution. Originally created by Marek Chalupa, in FORMELA, Faculty of Informatics, Masaryk University. This fork allows for handling multi-threaded C programs. It's a work in progress, focussing on data race detection for now. But other tasks like reach safety and overflow detection should come for free with it. Soon ;)
Best way to use it is to build via docker and then run the files inside. This aids in quick deployment.

# How to build (Dev)

Clone https://github.com/mchalupa/llvmlite
Run by mounting the pwd in the docker container.

# Container In Progress

apt install make
apt install build-essential
Just install llvm
for llvm-config command
so far I have also installed llvm

setuptools > requirements.txt

apt install -y llvm-14 llvm-14-dev < done so far. 

also install llvmlite locally cloned.

## TODO

- Setup unit tests.
- Add safe cloning of llvmlite instead of copying from host.
