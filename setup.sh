#!/bin/bash

# Just used by docker inside the container

set -e

# Ouptut directory.
mkdir -p sb-out

# SHOULD BE DOCKERIZED

apt update
apt install -y \
    --no-install-recommends \
    llvm \
    llvm-14 \
    llvm-14-dev \
    make \
    build-essential \
    clang-14 \

rm -rf /var/lib/apt/lists/*

pip3 install --user -r requirements.txt

# Post creation commands

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

echo "Running Unit tests..."
pytest tests/unit-tests/

echo "Verify PATH please..."
echo $PATH
