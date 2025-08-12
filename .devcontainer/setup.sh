#!/bin/bash

# Ouptut directory.
mkdir -p sb-out

# SHOULD BE DOCKERIZED

apt update
apt install -y --no-install-recommends \
  llvm llvm-14 llvm-14-dev make build-essential clang-14

rm -rf /var/lib/apt/lists/*

python3 -m pip install --no-cache-dir -r requirements.txt

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
# python3 -m pip install -e ./llvmlite
cd ..

echo "Testing llvm installation.."
python ./tests/test-z3-installation.py

echo "Running Unit tests..."
pytest tests/unit-tests/

error=0

# Function to check and optionally set environment variables.
function check_and_set_var() {
    local var_name="$1"
    local default_value="$2"
    if [[ -z "${!var_name}" ]]; then
        echo "WARN: $var_name is not set. Setting it to default value: '$default_value'."
        echo "$var_name was overridden."
        overridden_vars+=("$var_name")
        ((overrides++))
    else
        echo "PASS: $var_name is set to '${!var_name}'."
    fi
}

echo "Checking and setting environment variables..."

# Initialize override counter and list of overridden variables.
overrides=0
overridden_vars=()

# Check and set each variable with a default value if not set.
check_and_set_var PYTHONUNBUFFERED "1"
check_and_set_var PYTHONIOENCODING "utf-8"
check_and_set_var PYTHONDONTWRITEBYTECODE "1"
check_and_set_var PYTHONPATH "/usr/local/lib/python3.8/site-packages"
check_and_set_var HISTFILE "/workspaces/slowbeast-no-data-race/.devcontainer/.command-history-docker"

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
if [[ -n "$PYTHONPATH" ]]; then
    python_sys_path=$(python -c 'import sys; print(":".join(sys.path))')
    IFS=':' read -r -a py_paths <<< "$PYTHONPATH"
    for p in "${py_paths[@]}"; do
        if echo "$python_sys_path" | grep -qF "$p"; then
            echo "PASS: '$p' found in Python sys.path."
        else
            echo "FAIL: '$p' not found in Python sys.path."
            ((error++))
        fi
    done
fi

# Report overrides.
if [[ $overrides -ne 0 ]]; then
    echo "INFO: $overrides environment variables were overridden with default values."
    echo "Overridden variables: ${overridden_vars[*]}"
else
    echo "INFO: No environment variables required overriding."
fi

# Final outcome based on error flag.
if [[ $error -ne 0 ]]; then
    echo "Some tests failed. $error errors. Please review the errors above."
else
    echo "All tests passed!"
fi

# exit $error

# Persist prompt + HOME for root
if ! grep -q "DEVSPACE START" /root/.bashrc 2>/dev/null; then
  cat >> /root/.bashrc <<'RC'
# --- DEVSPACE START ---
# Make workspace behave like ~ for root
export HOME="/workspaces/slowbeast-no-data-race"
cd "$HOME" 2>/dev/null || true

# Prompt: root@devspace:/path$
export PS1='\u@devspace:\w\$ '
# Trim long paths in the prompt (optional)
export PROMPT_DIRTRIM=3

# Keep history inside the repo (optional; matches your script)
export HISTFILE="$HOME/.devcontainer/.command-history-docker"
mkdir -p "$(dirname "$HISTFILE")"; touch "$HISTFILE"
# --- DEVSPACE END ---
RC
fi


echo "Path variable"
echo $PATH

echo "Present working directory:"
pwd

