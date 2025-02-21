FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install apt packages. Mostly to get llvmlite running
RUN apt update && apt install -y --no-install-recommends \
    llvm \
    llvm-14 \
    llvm-14-dev \
    make \
    build-essential \
    clang-14 \
    && rm -rf /var/lib/apt/lists/*

# Install python modules
COPY requirements.txt /app/requirements.txt
RUN python -m pip install -r requirements.txt

# Entrypoint script. Clones llvmlite if not existing previously.
# COPY install-llvmlite.sh /app/install-llvmlite.sh
# RUN chmod +x /app/install-llvmlite.sh

# RUN groupadd -g 5678 docker-shared && \
#     useradd -u 5678 -g docker-shared --no-create-home appuser && \
#     chown -R appuser:docker-shared /app && \
#     chmod -R g+rwx /app

# USER appuser

# ENTRYPOINT ["/app/install-llvmlite.sh"]
