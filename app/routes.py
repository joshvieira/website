from app import app
from flask import render_template
from bokeh.embed import server_document
import socket

@app.route('/')
def home():
    index = 'http://' + socket.gethostname() + ':' + str(app.config.get('BOKEH_PORT')) + '/polstream'
    #index = 'localhost:' + str(app.config.get('BOKEH_PORT')) + '/polstream'
    script = server_document(url=index)
    return render_template('home.html', bokeh_script=script)


#@app.route('/electability-in-2020')
#def electability():
#    index = 'http://' + socket.gethostname() + ':' + str(app.config.get('BOKEH_PORT')) + '/polstream'
#    script = server_document(url=index)
#    return render_template('charts.html', bokeh_script=script)