#!/bin/sh

if [ ! -d "/app/llvmlite" ]; then
    echo "llvmlite not found, cloning..."
    git clone https://github.com/mchalupa/llvmlite /app/llvmlite
else
    echo "llvmlite directory found."
fi

echo "Attempting installation..."
python /app/llvmlite/setup.py build

while [ ! -f /app/sb ]; do
    echo "Waiting for /app/sb..."
    sleep 1
done

exec python sb "$@"
