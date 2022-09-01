#!/bin/bash
# this script is executed in the services Docker container
# to examine the services run:  docker exec -it web-services-1 tmux a -t predictit

PYTHON_WEB=/opt/conda/envs/webenv/bin/python

# Cache predictit data in Redis within tmux session
tmux new-session -d -s "predictit"
tmux send-keys -t predictit "$PYTHON_WEB data_access_layer/predictit/cache.py" Enter

tail -f /dev/null