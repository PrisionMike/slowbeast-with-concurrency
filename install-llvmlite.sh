#!/bin/bash

# Just used by docker inside the container

set -e

# Ouptut directory.
mkdir -p sb-out

# Clone and llvmlite if required.
if [ ! -d "./llvmlite" ]; then
    echo "llvmlite not found, cloning..."
    git clone https://github.com/mchalupa/llvmlite /app/llvmlite
else
    echo "llvmlite directory found."
fi

echo "Attempting installation..."

cd llvmlite
python setup.py build
cd ..

echo "Testing llvm installation.."
python ./tests/test-z3-installation.py

echo "Adding python site packages to path..."
export PATH=/root/.local/bin:$PATH

echo "Verify PATH please..."
echo $PATH
