#!/bin/bash

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

# echo "Verify PATH please..."
# echo $PATH

# ---------

# This script tests if specific environment variables in your devcontainer
# are set correctly and, where applicable, function as expected.
#
# The tested variables include:
#   - PYTHONUNBUFFERED: Should be set (typically "1").
#   - PYTHONIOENCODING: Should be set (usually "utf-8").
#   - PYTHONDONTWRITEBYTECODE: Should be set ("1" to disable writing .pyc files).
#   - PYTHONPATH: Checks that the paths listed here appear in sys.path.
#   - HISTFILE: Checks that it's set and writable.
#
# Note: PS1 isn't tested because its behavior is visible on container startup.
#
error=0

function check_var() {
    local var_name="$1"
    if [[ -z "${!var_name}" ]]; then
        echo "FAIL: $var_name is not set!"
        ((error++))
    else
        echo "PASS: $var_name is set to '${!var_name}'."
    fi
}

echo "Checking environment variables..."

# Check that each variable is set.
check_var PYTHONUNBUFFERED
check_var PYTHONIOENCODING
check_var PYTHONDONTWRITEBYTECODE
check_var PYTHONPATH
check_var HISTFILE

# Test if HISTFILE is writable.
if [[ -n "$HISTFILE" ]]; then
    touch "$HISTFILE" 2>/dev/null
    if [[ $? -ne 0 ]]; then
        echo "FAIL: HISTFILE ($HISTFILE) is not writable!"
        ((error++))
    else
        echo "PASS: HISTFILE ($HISTFILE) is writable."
    fi
fi

# Test the functionality of PYTHONPATH:
# Run a short Python snippet to print sys.path, then confirm that each
# directory in your PYTHONPATH is present.
if [[ -n "$PYTHONPATH" ]]; then
    python_sys_path=$(python -c 'import sys; print(":".join(sys.path))')
    # Split PYTHONPATH into an array by colon delimiter.
    IFS=':' read -r -a py_paths <<< "$PYTHONPATH"
    for p in "${py_paths[@]}"; do
        # Using grep -q to quietly check if the path is in sys.path.
        if echo "$python_sys_path" | grep -qF "$p"; then
            echo "PASS: '$p' found in Python sys.path."
        else
            echo "FAIL: '$p' not found in Python sys.path."
            ((error++))
        fi
    done
fi

# You can add additional tests below if needed, for example, testing 'PATH' modifications.
# A basic test could simply print it:
echo "INFO: PATH is set to: $PATH"

# Final outcome based on error flag.
if [[ $error -ne 0 ]]; then
    echo "Some tests failed. $error errors. Please review the errors above."
else
    echo "All tests passed!"
fi

exit $error

echo "Present working directory:"
pwd
