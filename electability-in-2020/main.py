from config.flaskconfig import ProdConfig

import pandas as pd
from bokeh.layouts import row, column, widgetbox, Spacer
from bokeh.models import ColumnDataSource, HoverTool, Legend
from bokeh.plotting import figure, curdoc, show, output_file
from bokeh.palettes import Category10 as clr_palette
from bokeh.models.widgets import Div, PreText, DataTable, TableColumn
import redis
import pyarrow as pa

CUTOFF = 0.15  # minimum required contract price in democratic candidate market in order to show probability
YMAX_DEMS = 1.0
YMAX_PRES = 1.0
YMIN_PROB = 0.4
YMAX_PROB = 0.9
LOC_LEGEND = 220
PLOT_WIDTH = 1000
PLOT_HEIGHT = 420

r = redis.Redis(port=ProdConfig.REDIS_PORT)
context = pa.default_serialization_context()
dems_d = pa.deserialize(r.get('dems_d'))
pres_d = pa.deserialize(r.get('pres_d'))
prob_d = pa.deserialize(r.get('prob_d'))
r.close()
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

def gen_table():

    columns = [
        TableColumn(field='dems_d', title='Candidates'),
        TableColumn(field='pres_d', title='Prob{Nomination}'),
        TableColumn(field='prob_d')
    ]

    t = DataTable(source=source_dems, )
    return t

def gen_dems():

    p = figure(
        title='Probability of receiving Democratic Party nomination',
        x_axis_type="datetime",
        plot_width=PLOT_WIDTH,
        plot_height=PLOT_HEIGHT,
        y_range=(0, YMAX_DEMS),
        toolbar_location='above'
    )

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
                'tstamp': 'datetime'
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
        toolbar_location='above'
    )

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
                'tstamp': 'datetime'
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

textstyle = style={'font-size': '17px'}
textwidth = int(PLOT_WIDTH * 0.9)

text0 = Div(text='<u>What might betting markets tell us about electability?</u>', style={'font-size': '30px'})
text1 = Div(text='29-Jan-2020', style=textstyle)
text1_1 = Div(text='Text updated June 2020', style=textstyle)

text2 = Div(text="""By using data from a betting market for political events, we can get an estimate for the 
'electability' of candidates. On <a href="https://www.predictit.com">predictit.com</a>, 
users can bet on which candidates will win each major party's nomination, 
and on which candidates will win the general election. By dividing the price of the latter contracts by the 
price of the former, we get an estimate for the conditional probability 
that a candidate wins the general election given they were chosen as their party's nominee. 
This is the notion of electability. If nominated, what are the odds of beating your opponent in the general election? 
""", width=textwidth, style=textstyle)

text3 = Div(text="""The charts below show how major candidates' nomination probabilities and conditional probabilities 
have evolved through time.
""", width=textwidth, style=textstyle)

text4 = Div(text='<u>Technical details, caveats, and comments:</u>', style=textstyle)
text5 = Div(text="""
Betting market contract data is pulled every 5 minutes using the predictit API. Daily averages of 
contract values and their corresponding ratios are computed and rendered. To avoid spurious spikes in the chart due to 
division by small numbers, the conditional probability is only rendered when a candidate's probability of winning the 
party's nomination is above 15%. The conditional probability arises from Bayes' Theorem, which 
states   
""", width=textwidth, style=textstyle)
text6 = Div(text="P(Pres|Nom) = P(Nom|Pres) * P(Pres) / P(Nom)", width=textwidth, style=textstyle)
text7 = Div(text="""for the events Pres = {candidate wins Presidency} and Nom = {candidate wins party's nomination}. 
We are implicitly assuming that P(Nom|Pres) = 1, ie that there is no chance a candidate can win 
the presidency without having received their major party's nomination. 
""", width=textwidth, style=textstyle)
text8 = Div(text="""These numbers do not tell us about the states of the world in which 
a candidate is likely to be more or less successful. We have to make those inferences ourselves.
For instance, at the peak of her popularity Warren had a 52% probability of being nominated. 
"Squad" members AOC, Ilan Omar, and Rashida Tlaib endorsed Sanders shortly thereafter, 
and around the same time Warren began to waiver in her support for Medicare-for-All. 
These were blows to her credibility as a progressive candidate. 
Too timid in her willingness to enact institutional change for progressives, 
but still too harsh in her criticisms of those same institutions for establishment Democrats longing for a return to the Obama years, 
in the end she failed to arouse enthusiasm in either faction. 
Her nomination probability declined, as did her conditional probability of becoming president. 
A longer discussion around this topic is contained in 
<a href="http://users.nber.org/~jwolfers/Papers/Five%20Questions(NBER).pdf">Wolfers & Zitzewitz (2006)</a>, starting 
on p.14.
""", width=textwidth, style=textstyle)
text9 = Div(text="""
Finally, betting limits also prevent Predictit from being an ideal market. 
They limit the number of people who can be bothered to play the game, 
and they make it much easier to buy cheap shares than to sell them short. 
As two experts commented on Twitter,
""", width=textwidth, style=textstyle)
text10 = Div(text="<img src='electability-in-2020/static/twitter_natesilver.png'>")
text11 = Div(text="""
There are other interesting uses of this data. For instance, one could regress Trump's changes in 
election probability against changes in each Democratic candidate's nomination probability. This would again give us 
a sense of "electability", quantifying who has the highest impact on Trump's election odds. I may look at this in a later post. 
If you have comments or are interested in the underlying data, email me at josh.[my last name]@protonmail.com.
""", width=textwidth, style=textstyle)

dems = gen_dems()
prob = gen_prob(dems.x_range)
layout = row(Spacer(width=40),
column(
    Spacer(height=25),
    text0,
    text1,
    text1_1,
    text2,
    text3,
    Spacer(height=25),
    dems,
    Spacer(height=25),
    prob,
    text4,
    text5,
    text6,
    text7,
    text8,
    text9,
    text10,
    Spacer(height=120)
))
doc.add_root(layout)
doc.title = 'Estimating electability from betting markets'