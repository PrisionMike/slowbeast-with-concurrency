#!/bin/bash

set -e # Exit on error.

echo "Run this script as the root user"

GROUP_NAME="docker-shared"
GROUP_ID=5678
USER_NAME="strider" # Modify for your own user.
DOCKER_USER="appuser"
TARGET_DIR=$(pwd)

# Create an ouptut directory.
mkdir -p sb-out

# Clone and llvmlite if required.
if [ ! -d "./llvmlite" ]; then
    echo "llvmlite not found, cloning..."
    git clone https://github.com/mchalupa/llvmlite /app/llvmlite
else
    echo "llvmlite directory found."
fi

# Creating a common group for docker and host user. Because I am being principled and avoiding root inside container.
echo "Creating $GROUP_NAME ($GROUP_ID)..."
if ! getent group "$GROUP_NAME" >/dev/null; then
    groupadd -g "$GROUP_ID" "$GROUP_NAME"
else
    echo "Group $GROUP_NAME already exists."
fi

echo "Adding $USER_NAME to $GROUP_NAME..."
if ! id -nG "$USER_NAME" | grep -qw "$GROUP_NAME"; then
    usermod -aG "$GROUP_NAME" "$USER_NAME"
else
    echo "$USER_NAME is already in $GROUP_NAME."
fi

echo "Adding $DOCKER_USER to $GROUP_NAME..."
if id "$DOCKER_USER" &>/dev/null && ! id -nG "$DOCKER_USER" | grep -qw "$GROUP_NAME"; then
    usermod -aG "$GROUP_NAME" "$DOCKER_USER"
else
    echo "$DOCKER_USER already in $GROUP_NAME or does not exist."
fi

echo "Setting group ownership for $TARGET_DIR..."
chown -R :"$GROUP_NAME" "$TARGET_DIR"
chmod -R g+rwX "$TARGET_DIR"

echo "Switching to $GROUP_NAME"

sg "$GROUP_NAME" <<EOF

# Build container image.
echo "Buidling docker image.."
docker --version
docker build --pull=false -t slowbeastnodatarace:latest -f Dockerfile .

# docker compose run (Mounts pwd and enters into docker shell)
echo "Docker compose run.."
docker --version
docker compose run --rm slowbeast /bin/bash

EOF