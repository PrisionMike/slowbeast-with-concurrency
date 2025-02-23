## Docker debug commands

`docker run --rm -it -v "$PWD":/app -w /app slowbeastnodatarace:latest bash`

`docker compose exec slowbeast /bin/bash`

`docker compose run --service-ports --rm slowbeast /bin/bash`