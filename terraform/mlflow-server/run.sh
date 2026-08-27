#!/bin/bash
# Rebuilds and (re)starts the MLflow tracking server container, reading its
# configuration from .env in this same folder (see .env.example for the
# required variables and where each one comes from).
#
# This is the reproducible replacement for the one-off `docker run -e ...`
# command used to first start the server -- run this script instead of
# retyping/remembering those values.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "Missing .env -- copy .env.example to .env and fill in real values first." >&2
  exit 1
fi

docker build -t mlflow-tracking-server:local .

docker rm -f mlflow-server 2>/dev/null || true

docker run -d --name mlflow-server \
  -p 5000:5000 \
  --env-file .env \
  mlflow-tracking-server:local

echo "MLflow tracking server starting -- http://localhost:5000"
