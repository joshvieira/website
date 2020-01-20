from app import app
from flask import render_template
from bokeh.embed import server_document


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/electability-in-2020')
def index():
    bokeh_url = 'http://localhost:' + str(app.config.get('BOKEH_PORT')) + '/main'
    bokeh_script = server_document(url=bokeh_url)
    return render_template('charts.html', bokeh_script=bokeh_script)