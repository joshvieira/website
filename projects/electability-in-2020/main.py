import pandas as pd
from bokeh.layouts import row, column, widgetbox, Spacer
from bokeh.models import ColumnDataSource, HoverTool, Legend
from bokeh.plotting import figure, curdoc, show, output_file
from bokeh.palettes import Category10 as clr_palette
import redis
import pickle

from cfg.config import get_redis_host_and_port


CUTOFF = 0.15  # minimum required contract price in democratic candidate market in order to show probability
YMAX_DEMS = 1.0
YMAX_PRES = 1.0
YMIN_PROB = 0.4
YMAX_PROB = 0.9
LOC_LEGEND = 220
PLOT_WIDTH = 1000
PLOT_HEIGHT = 420

with redis.Redis(**get_redis_host_and_port()) as r:
    dems_d = pickle.loads(r.get('dems_d'))
    pres_d = pickle.loads(r.get('pres_d'))
    prob_d = pickle.loads(r.get('prob_d'))

tmp = prob_d.pop('Donald Trump')
prob_d = prob_d.mask(dems_d < CUTOFF)
prob_d = pd.concat([prob_d, tmp], axis=1)

keep = ['Joe Biden', 'Bernie Sanders', 'Elizabeth Warren', 'Pete Buttigieg', 'Michael Bloomberg']
dems_d = dems_d[keep]
pres_d = pres_d[keep]
prob_d = prob_d[keep + ['Donald Trump']]

doc = curdoc()

# store in columndatasource format
source_dems = ColumnDataSource(dems_d)
source_pres = ColumnDataSource(pres_d)
source_prob = ColumnDataSource(prob_d)


legend_options = dict(
    click_policy='hide',
    label_text_font='helvetica',
    background_fill_alpha=0,
    border_line_alpha=0
)

line_options = dict(
    line_width=3,
    alpha=1,
    muted_alpha=0.1
)


def gen_dems():

    p = figure(
        title='Probability of receiving Democratic Party nomination',
        x_axis_type="datetime",
        plot_width=PLOT_WIDTH,
        plot_height=PLOT_HEIGHT,
        y_range=(0, YMAX_DEMS),
        toolbar_location='above',
        name='dems'
    )

    palette = clr_palette[10]
    legend_list = []
    for i in range(len(dems_d.columns)):
        name = dems_d.columns[i]
        g = p.line(
            x='tstamp',
            y=name,
            source=source_dems,
            line_color=palette[i],
            muted_color=palette[i],
            name=name,
            **line_options
        )

        p.add_tools(HoverTool(

            tooltips=[
                ('date', '@tstamp{%F}'),
                ('name', '@{}'.format(name).split(' ')[-1]),
                ('value', '$y{0.2f}')
            ],

            formatters={
                '@tstamp': 'datetime'
            },

            renderers=[g],

            mode='mouse',

            toggleable=False
        ))

        i += 1
        legend_list.append((name, [g]))

    legend = Legend(
        items=legend_list,
        location=(0, LOC_LEGEND),
        **legend_options
    )

    p.add_layout(legend, 'right')
    p.toolbar.logo = None

    return p


def gen_prob(x_range):

    p = figure(
        title="Probability of winning presidency if chosen as nominee",
        x_axis_type="datetime",
        x_range=x_range,
        plot_width=PLOT_WIDTH,
        plot_height=PLOT_HEIGHT,
        y_range=(YMIN_PROB, YMAX_PROB),
        toolbar_location='above',
        name='prob'
    )

    palette = clr_palette[10]
    legend_list = []
    for i in range(len(prob_d.columns)):
        name = prob_d.columns[i]
        g = p.line(
            x='tstamp',
            y=name,
            source=source_prob,
            line_color=palette[i],
            muted_color=palette[i],
            name=name,
            **line_options
        )

        p.add_tools(HoverTool(

            tooltips=[
                ('date', '@tstamp{%F}'),
                ('name', '@{}'.format(name).split(' ')[-1]),
                ('value', '$y{0.2f}')
            ],

            formatters={
                '@tstamp': 'datetime'
            },

            renderers=[g],

            mode='mouse',

            toggleable=False
        ))

        i += 1
        legend_list.append((name, [g]))

    legend = Legend(
        items=legend_list,
        location=(0, LOC_LEGEND),
        **legend_options
    )

    p.add_layout(legend, 'right')
    p.toolbar.logo = None

    return p


dems = gen_dems()
prob = gen_prob(dems.x_range)
doc.add_root(
    column(
        dems,
        Spacer(height=25),
        prob,
        name='cols'
    )
)
doc.title = 'Estimating electability from betting markets'
