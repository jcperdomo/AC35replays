import data_access
from bokeh.models import Line

print data_access.get_race_data("170530", 1)['events']
