import data_access
from bokeh.io import output_file, show
from bokeh.plotting import save
import bokeh.models as models
from bokeh.layouts import column
from bokeh.models import CustomJS
import pandas as pd
from data_access import *

# import relevant data
DATE = "170601"
RACE_NUMBER = 2
START = -30
END = 10
FREQ = 25

data = get_race_data(DATE, RACE_NUMBER)

map_options = models.GMapOptions(lat=32.307660, lng=-64.848481,
                                 map_type="terrain", zoom=15)

plot = models.GMapPlot(x_range=models.DataRange1d(), y_range=models.DataRange1d(),
                       map_options=map_options, plot_width=600, plot_height=600)

plot.title.text = "Bermuda"
plot.api_key = "AIzaSyBTnh7EZA33ChReBm449xwYxno1kE4w3EE"

# plot mark data
mark_source = models.ColumnDataSource(get_mark_data(data))
circle = models.Circle(x="Lon", y="Lat", size=7, fill_color="magenta",
                       fill_alpha=0.4, line_color=None)
plot.add_glyph(mark_source, circle)

competitors = get_competitors(DATE, RACE_NUMBER)
comp_colors = ['red', 'black']

# plot boat 1
for competitor, color in zip(competitors, comp_colors):
    boat_source = models.ColumnDataSource(get_boat_data(data, competitor, (START, END), FREQ))
    boat_glyph = models.Patches(xs='Lons', ys='Lats', fill_color=color,
                                 fill_alpha=0.7, line_color=None)
    plot.add_glyph(boat_source, boat_glyph)

hover = models.HoverTool()
hover.tooltips = [('ID', '@Boat'), ('Time', '@Secs'),
                  ('Wind Direction', '@CourseWindDirection'),
                  ('Wind Speed', '@CourseWindSpeed'), ('COG', '@COG'),
                  ('SOG', '@SOG'), ('Heading', '@Hdg')]
plot.add_tools(models.PanTool(), models.WheelZoomTool(), models.ResetTool(),
               hover)
output_file("gmap_plot.html")
save(plot)
