# Build container image.
echo "Buidling docker image.."
docker build --pull=false -t slowbeastnodatarace:latest -f Dockerfile .

# docker compose run (Mounts pwd and enters into docker shell)
echo "Docker (compose) Run.."
docker compose run --rm slowbeast /bin/bash