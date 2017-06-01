import pandas as pd
import os
import re
import graphics_help as graph
import numpy as np

MARKS = ['SL1', 'SL2', 'FL1', 'FL2', 'M1', 'LG1', 'LG2', 'WG1', 'WG2']

AC_schedule = {"170527": [["USA", "FRA"], ["SWE", "JPN"], ["NZL", "FRA"], ["SWE", "GBR"], ["USA", "NZL"], ["JPN", "GBR"],],
     "170528": [["SWE", "FRA"], ["USA", "GBR"], ["NZL", "JPN"], ["USA", "SWE"], ["NZL", "GBR"], ["USA", "JPN"],],
     "170529": [["FRA", "GBR"], ["SWE", "NZL"], ["JPN", "FRA"]],
     "170530": [["SWE", "NZL"], ["USA", "FRA"], ["SWE", "GBR"]],
     "170601": [["JPN", "FRA"], ["GBR", "NZL"], ["USA", "JPN"], ["FRA", "GBR"]]}

def get_recording_times(date):

    # eventually will add functionality to check if the relevant files have been downloaded
    # right now just assume that they have indeed been downloaded

    file_names = os.listdir(os.getcwd()+"/{}/csv".format(date))
    s = set([])
    for i in file_names:
        s.add(re.search('^[0-9]+', i).group())
    return sorted(list(s))

def get_competitors(date, race_number):
    return AC_schedule[date][race_number-1]

def get_race_data(date, race_number):
    """
    date = string of the form "YYMMDD"
    race_number = int, race number within the day

    returns: [marks, boat1, boat2], list of pandas dataframes
    """
    rec_times = get_recording_times(date)
    boats = get_competitors(date, race_number)
    filetime = rec_times[race_number - 1]

    res = []

    script_dir = os.getcwd()
    res = {}
    for val in boats + MARKS:
        rel_path = "/{}/csv/{}-NAV-{}.csv".format(date, filetime, val)
        path = script_dir + rel_path
        res[val] = pd.read_csv(path)

    event_path = script_dir + "/{}/csv/{}_events.csv".format(date,filetime)
    res["events"] = pd.read_csv(event_path)

    # get rid of floating point errors later on
    for key in res.keys():
          res[key]['Secs'] = res[key]['Secs'].apply(lambda x: round(x, 1))

    return res

def get_start_time(data):
    # returns start time (the gun) in s from midnight
    events_frame = data['events']
    return events_frame.loc[events_frame['Event'] == 'RaceStarted']['Secs'].iloc[0]

def get_mark_data(data):
    # returns positions of the marks at start time
    mark_data = pd.concat([data[m] for m in MARKS])
    start_time = get_start_time(data)
    return mark_data.loc[abs(mark_data['Secs'] - start_time) < .5]

def get_boat_data(data, boat_name, interval, freq):

    boat_data = data[boat_name]
    # normalize times to the start time
    boat_data['Secs'] = boat_data['Secs'] - get_start_time(data)

    # extract data from the relevant interval
    lb, ub = interval
    boat_data = boat_data.loc[boat_data['Secs'].between(lb, ub, inclusive=True)]

    lats = []
    lons = []
    for _, row in boat_data.iterrows():
        coords = gen_outline_coords(row)
        lats.append(coords[0])
        lons.append(coords[1])
    boat_data['Lats'] = lats
    boat_data['Lons'] = lons
    return boat_data.iloc[::freq,:]

def gen_outline_coords(row):
    heading = row["Hdg"]
    pos = [row['Lat'], row['Lon']]
    # return np array (2, num_vertices)
    return np.array(graph.draw_boat(pos, np.radians(heading))).transpose()