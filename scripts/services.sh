#!/bin/bash
# this script is executed as entrypoint to the website-services-1 Docker container
# to examine the services run:  docker exec -it website-services-1 tmux a -t services

PYTHON_WEB=/opt/conda/envs/webenv/bin/python

# Cache predictit data in Redis within tmux session
tmux new-session -d -s "services"
tmux send-keys -t services "$PYTHON_WEB data_access_layer/predictit/cache.py" Enter
tmux rename-window "cache-predictit"

# keep the container alive
tail -f /dev/null