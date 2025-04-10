# Saves the command history of the usage inside the container
touch .command-history-docker

# Build container image
echo "Building docker image.."
docker build --pull=false -t slowbeastnodatarace:latest -f Dockerfile .

# docker compose run (mounts pwd and enters into docker shell)
echo "Docker (compose) Run.."
docker compose run --rm slowbeast /bin/bash