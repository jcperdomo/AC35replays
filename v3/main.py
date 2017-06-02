from bokeh.io import curdoc
from bokeh.plotting import save
import bokeh.models as models
from bokeh.layouts import row, widgetbox
from bokeh.models.widgets import Slider, Select
import pandas as pd
from data_access import *

# import relevant data
DATE = "170601"
RACE_NUMBER = 2
START = -30
END = 10
FREQ = 25

map_options = models.GMapOptions(lat=32.307660, lng=-64.848481,
                                 map_type="terrain", zoom=15)

plot = models.GMapPlot(x_range=models.DataRange1d(), y_range=models.DataRange1d(),
                       map_options=map_options, plot_width=600, plot_height=600)

plot.api_key = "AIzaSyBTnh7EZA33ChReBm449xwYxno1kE4w3EE"

# add widgets
frequency_slider = Slider(title="Frequency", value=25, start=5, end=100, step=5)
date_select = Select(title='Date', value='170527', options=AC_schedule.keys())
start_slider = Slider(title="Start", value=-30, start=-500, end=-10, step=10)
end_slider = Slider(title="End", value=30, start=10, end=500, step=10)

race_select = Select(title="Race Number", value='1', options=get_race_options(date_select.value))
event_select = Select(title="Event", value="RaceStarted",
                      options=get_event_options(date_select.value,
                                                extract_race_number(race_select.value)))

plot.title.text = "Bermuda {} Race {}".format(date_select.value, race_select.value)

# plot mark data
mark_source = models.ColumnDataSource(get_mark_data(date_select.value, RACE_NUMBER))
circle = models.Circle(x="Lon", y="Lat", size=7, fill_color="magenta",
                       fill_alpha=0.4, line_color=None)
plot.add_glyph(mark_source, circle)

# plot boat data
boat_source = models.ColumnDataSource(get_boat_data(date_select.value, RACE_NUMBER, (START, END), frequency_slider.value))
boat_glyph = models.Patches(xs='Lons', ys='Lats', fill_color='Color',
                             fill_alpha=0.7, line_color=None)
plot.add_glyph(boat_source, boat_glyph)

hover = models.HoverTool()
hover.tooltips = [('ID', '@Boat'), ('Time', '@Secs'),
                  ('Wind Direction', '@CourseWindDirection'),
                  ('Wind Speed', '@CourseWindSpeed'), ('COG', '@COG'),
                  ('SOG', '@SOG'), ('Heading', '@Hdg')]
plot.add_tools(models.PanTool(), models.WheelZoomTool(), models.ResetTool(),
               hover)

def update():
    # start = start_slider.value
    # end = end_slider.value
    freq = frequency_slider.value
    date = date_select.value
    race_number = extract_race_number(race_select.value)
    start = start_slider.value
    end = end_slider.value

    plot.title.text = "Bermuda {} Race {}".format(date, race_number)
    new_boat_source = models.ColumnDataSource(get_boat_data(date, race_number, (start, end), freq))
    boat_source.data = new_boat_source.data

    new_mark_source = models.ColumnDataSource(get_mark_data(date, RACE_NUMBER))
    mark_source.data = new_mark_source.data

def update_date():
    date = date_select.value
    race_number = 1
    freq = frequency_slider.value
    start = start_slider.value
    end = end_slider.value

    race_select.options = get_race_options(date)

    plot.title.text = "Bermuda {} Race {}".format(date, race_number)
    new_boat_source = models.ColumnDataSource(get_boat_data(date, race_number, (start, end), freq))
    boat_source.data = new_boat_source.data

    new_mark_source = models.ColumnDataSource(get_mark_data(date, RACE_NUMBER))
    mark_source.data = new_mark_source.data


controls = [frequency_slider, start_slider, end_slider, race_select, event_select]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

date_select.on_change('value', lambda attr, old, new: update_date())

controls.append(date_select)
inputs = widgetbox(*controls)
layout = row(inputs, plot, width=1000)
curdoc().add_root(layout)
curdoc().title = "AC35"
