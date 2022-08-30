this is the directory for the bokeh application. it should follow the guidelines from "running a bokeh server" page:

myapp
   |
   +---data
   |    +---things.csv
   |
   +---helpers.py
   +---main.py
   |---models
   |    +---custom.js
   |
   +---server_lifecycle.py
   +---static
   |    +---css
   |    |    +---special.css
   |    |
   |    +---images
   |    |    +---foo.png
   |    |    +---bar.png
   |    |
   |    +---js
   |        +---special.js
   |
   |---templates
   |    +---index.html
   |
   +---theme.yaml


In this case you might have code similar to:

from os.path import dirname, join
from helpers import load_data

load_data(join(dirname(__file__), 'data', 'things.csv'))
