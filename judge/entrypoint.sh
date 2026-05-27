#!/bin/sh
set -e
python -c "
import docker
client = docker.from_env()
client.images.pull('python:3.13-slim')
print('python:3.13-slim is ready')
"
exec "$@"
