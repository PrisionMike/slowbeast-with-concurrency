FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HISTFILE=/app/.command-history-docker

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
