import pickle

from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Legend
from bokeh.plotting import figure, curdoc, show, output_file
from bokeh.palettes import Category10

# upon requesting the bokeh document, we should
# (1) read in a serialized dataframe, which is kept up to date in a separate process
# (2) continue to append to this dataframe using callbacks specific to the bokeh session
# (3) stream the dataframe updates to the ColumnDataSources

with open('./data/pres.p', 'rb') as handle:
    ts_dem, ts_pres, ts_cond = pickle.load(handle)

# store in columndatasource format
source_dems = ColumnDataSource(ts_dem)
source_pres = ColumnDataSource(ts_pres)
source_cond = ColumnDataSource(ts_cond)

y_max = 0.4
p = figure(
    x_axis_type="datetime",
    plot_width=1200,
    plot_height=500,
    y_range=(0, y_max)
    )

kw_legend = dict(
    click_policy='hide',
    label_text_font='helvetica',
    background_fill_alpha=0,
    border_line_alpha=0
)

kw_lines = dict(
    line_width=2,
    alpha=1,
    muted_alpha=0.1
)

palette = Category10[10]
legend_list = []
for i in range(len(ts_dem.columns)):
    name = ts_dem.columns[i]
    g = p.line(
        x='tstamp',
        y=name,
        source=source_dems,
        line_color=palette[i],
        muted_color=palette[i],
        name=name,
        **kw_lines
    )
    i += 1
    legend_list.append((name, [g]))

legend = Legend(items=legend_list, location=(0, 100), **kw_legend)
p.add_layout(legend, 'right')
p.toolbar.logo = None

layout = column(
    p
)
curdoc().add_root(layout)
curdoc().title = "Politics!"