import data_access
from bokeh.io import output_file, show
from bokeh.plotting import save
import bokeh.models as models
import pandas as pd
from data_access import *

# import relevant data
DATE = "170601"
RACE_NUMBER = 2
data = get_race_data(DATE, RACE_NUMBER)

map_options = models.GMapOptions(lat=32.314684, lng=-64.834079,
                                 map_type="terrain", zoom=13)

plot = models.GMapPlot(x_range=models.DataRange1d(), y_range=models.DataRange1d(),
                       map_options=map_options, plot_width=800, plot_height=800)

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
    boat_source = models.ColumnDataSource(get_boat_data(data, competitor, (-30, 200.0), 25))
    boat_glyph = models.Patches(xs='Lons', ys='Lats', fill_color=color,
                                 fill_alpha=0.9, line_color=None)
    plot.add_glyph(boat_source, boat_glyph)

hover = models.HoverTool()
hover.tooltips = [('ID', '@Boat'), ('Time', '@Secs'),('Wind Direction', '@CourseWindDirection'),
                  ('Wind Speed', '@CourseWindSpeed'), ('COG', '@COG'),
                  ('SOG', '@SOG'), ('Heading', '@Hdg')]
plot.add_tools(models.PanTool(), models.WheelZoomTool(), models.ResetTool(), hover)

output_file("gmap_plot.html")
save(plot)
