from bokeh.io import curdoc
from bokeh.plotting import save, figure
import bokeh.models as models
from bokeh.layouts import row, widgetbox, layout
from bokeh.models.widgets import Slider, Select
import pandas as pd
from data_access import *

# import relevant data

PLOT_WIDTH = 850
PLOT_HEIGHT = 400

map_options = models.GMapOptions(lat=32.307660, lng=-64.848481,
                                 map_type="terrain", zoom=15)

race_map = models.GMapPlot(x_range=models.DataRange1d(), y_range=models.DataRange1d(),
                           map_options=map_options, plot_width=PLOT_WIDTH,
                           plot_height=PLOT_HEIGHT)

race_map.api_key = "AIzaSyBTnh7EZA33ChReBm449xwYxno1kE4w3EE"

# add widgets
frequency_slider = Slider(title="Frequency", value=25, start=5, end=100, step=5)
date_select = Select(title='Date', value='170527', options=AC_schedule.keys())
start_slider = Slider(title="Start", value=-30, start=-500, end=-10, step=10)
end_slider = Slider(title="End", value=30, start=10, end=500, step=10)

race_select = Select(title="Race Number", value='1', options=get_race_options(date_select.value))
event_select = Select(title="Event", value="RaceStarted",
                      options=get_event_options(date_select.value,
                                                extract_race_number(race_select.value)))
field_select = Select(title="Data Field", value='SOG', options=["SOG", "Pitch", "Heel"])

race_map.title.text = "Bermuda {} Race {}, {}".format(date_select.value,
                                                race_select.value,
                                                event_select.value)

data_plot = figure(plot_height=PLOT_HEIGHT, plot_width=PLOT_WIDTH,
                   title=field_select.value,
                   tools="reset, save, pan, wheel_zoom")

lines_source = models.ColumnDataSource(get_plot_data(date_select.value, extract_race_number(race_select.value),
                                                     field_select.value, event_select.value,
                                                     (start_slider.value, end_slider.value)))
lines = models.MultiLine(xs='Secs', ys=field_select.value, line_color='Colors')
data_plot.add_glyph(lines_source, lines)

# plot mark data
mark_source = models.ColumnDataSource(get_mark_data(date_select.value,
                                                    extract_race_number(race_select.value)))

circle = models.Circle(x="Lon", y="Lat", size=7, fill_color="magenta",
                       fill_alpha=0.4, line_color=None)
race_map.add_glyph(mark_source, circle)

# plot boat data
boat_source = models.ColumnDataSource(get_boat_data(date_select.value,
                                                    extract_race_number(race_select.value),
                                                    event_select.value,
                                                    (start_slider.value, end_slider.value),
                                                    frequency_slider.value))

boat_glyph = models.Patches(xs='Lons', ys='Lats', fill_color='Color',
                             fill_alpha=0.7, line_color=None)
race_map.add_glyph(boat_source, boat_glyph)

hover = models.HoverTool()
hover.tooltips = [('ID', '@Boat'), ('Time', '@Secs'),
                  ('Wind Direction', '@CourseWindDirection'),
                  ('Wind Speed', '@CourseWindSpeed'), ('COG', '@COG'),
                  ('SOG', '@SOG'), ('Heading', '@Hdg')]
race_map.add_tools(models.PanTool(), models.WheelZoomTool(), models.ResetTool(),
               hover)

def update_plot(date, race_number, field, event, interval):
    lines.ys = field
    data_plot.title.text = field
    new_lines_source = models.ColumnDataSource(get_plot_data(date, race_number,
                                                         field, event,
                                                         interval))
    lines_source.data = new_lines_source.data



def update():
    # start = start_slider.value
    # end = end_slider.value
    freq = frequency_slider.value
    date = date_select.value
    race_number = extract_race_number(race_select.value)
    start = start_slider.value
    end = end_slider.value
    event = event_select.value
    field = field_select.value

    race_map.title.text = "Bermuda {} Race {}, {}".format(date, race_number, event)
    new_boat_source = models.ColumnDataSource(get_boat_data(date, race_number, event, (start, end), freq))
    boat_source.data = new_boat_source.data

    new_mark_source = models.ColumnDataSource(get_mark_data(date, race_number))
    mark_source.data = new_mark_source.data

    update_plot(date, race_number, field, event, (start, end))

def update_date_select():
    date = date_select.value
    race_number = 1
    event = "RaceStarted"
    freq = frequency_slider.value
    start = start_slider.value
    end = end_slider.value
    field = field_select.value

    race_select.options = get_race_options(date)
    race_select.value = race_select.options[0]

    race_map.title.text = "Bermuda {} Race {}, {}".format(date, race_number, event)
    new_boat_source = models.ColumnDataSource(get_boat_data(date, race_number, event,
                                                            (start, end), freq))
    boat_source.data = new_boat_source.data

    new_mark_source = models.ColumnDataSource(get_mark_data(date, race_number))
    mark_source.data = new_mark_source.data

    update_plot(date, race_number, field, event, (start, end))

def update_race_select():
    date = date_select.value
    race_number = extract_race_number(race_select.value)
    freq = frequency_slider.value
    start = start_slider.value
    end = end_slider.value
    event = "RaceStarted"
    field = field_select.value

    # update event options for the new race
    event_select.options = get_event_options(date, race_number)
    event_select.value = event
    race_map.title.text = "Bermuda {} Race {}, {}".format(date, race_number, "RaceStarted")

    # Set the default event upon a new race to be the start
    new_boat_source = models.ColumnDataSource(get_boat_data(date, race_number, "RaceStarted",
                                                            (start, end), freq))
    boat_source.data = new_boat_source.data

    new_mark_source = models.ColumnDataSource(get_mark_data(date, race_number))
    mark_source.data = new_mark_source.data

    update_plot(date, race_number, field, event, (start, end))

controls = [frequency_slider, start_slider, end_slider, event_select, field_select]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

race_select.on_change('value', lambda attr, old, new: update_race_select())
date_select.on_change('value', lambda attr, old, new: update_date_select())

# controls = controls + [race_select, date_select]
inputs_map = widgetbox([date_select, race_select, event_select, frequency_slider,
                    start_slider, end_slider],width=200)
inputs_data = widgetbox([field_select], width=200)
l = layout([[inputs_map, race_map], [inputs_data, data_plot]])
curdoc().add_root(l)
curdoc().title = "AC35"
