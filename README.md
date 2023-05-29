## Hello
This is the repo for the code that runs my website of personal projects.  
Several applications run in Docker containers:
1. Flask - web server / routing (runs behind Nginx)
2. Bokeh server - web application for interactive plots
3. Postgres - stores Predictit political betting market data
4. Redis - caches data for Bokeh application 

If you wish to view the code related to any of the projects, please see the "projects" directory.  
For example, the Kelly criterion project has code located at "projects/kellycriterion/kelly.py"

## Setup
With Docker installed and `.env` file in the home directory, run:
```bash
sudo docker compose -f docker-compose-dev.yml up --build
```
