import pandas as pd
import os
import re
import graphics_help as graph
import numpy as np
import itertools

MARKS = ['SL1', 'SL2', 'FL1', 'FL2', 'M1', 'LG1', 'LG2', 'WG1', 'WG2']

AC_schedule = {"170527": [["USA", "FRA"], ["SWE", "JPN"], ["NZL", "FRA"], ["SWE", "GBR"], ["USA", "NZL"], ["JPN", "GBR"],],
     "170528": [["SWE", "FRA"], ["USA", "GBR"], ["NZL", "JPN"], ["USA", "SWE"], ["NZL", "GBR"], ["USA", "JPN"],],
     "170529": [["FRA", "GBR"], ["SWE", "NZL"], ["JPN", "FRA"]],
     "170530": [["SWE", "NZL"], ["USA", "FRA"], ["SWE", "GBR"]],
     "170601": [["JPN", "FRA"], ["GBR", "NZL"], ["USA", "JPN"], ["FRA", "GBR"]],
     "170602": [["NZL", "JPN"], ["SWE", "USA"], ["NZL", "FRA"], ["JPN", "SWE"]]}

def get_recording_times(date):

    # eventually will add functionality to check if the relevant files have been downloaded
    # right now just assume that they have indeed been downloaded
    file_names = os.listdir(os.getcwd()+"/v3/{}/csv".format(date))
    s = set([])
    for i in file_names:
        s.add(re.search('^[0-9]+', i).group())
    return sorted(list(s))

def get_competitors(date, race_number):
    return AC_schedule[date][race_number - 1]

def get_race_data(date, race_number):
    """
    date = string of the form "YYMMDD"
    race_number = int, race number within the day

    returns: [marks, boat1, boat2], list of pandas dataframes
    """
    rec_times = get_recording_times(date)
    boats = get_competitors(date, race_number)
    filetime = rec_times[race_number - 1]

    script_dir = os.getcwd() +"/v3"
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

def extract_race_number(value):
    return int(value[0])

def get_race_options(date):
    lst = [",".join(pair) for pair in AC_schedule[date]]
    return [str(i+1)+"-"+val for i, val in enumerate(lst)]

def get_start_time(data):
    # returns start time (the gun) in s from midnight
    events_frame = data['events']
    return events_frame.loc[events_frame['Event'] == 'RaceStarted']['Secs'].iloc[0]

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def get_event_options(date, race_number):
    data = get_race_data(date, race_number)['events']
    mark_vals = [int(i) for i in data['Opt1'].unique() if is_int(i)]
    marks_rounded = [str(i) for i in range(1, max(mark_vals) + 1)]
    competitors = get_competitors(date, race_number)

    roundings = itertools.product(competitors, ["MarkRounding"], marks_rounded)
    roundings = ["-".join(triple) for triple in roundings]

    finishes = itertools.product(competitors, ["CrossedFinish"])
    finishes = ["-".join(pair) for pair in finishes]
    return ["RaceStarted"] + roundings + finishes

def parse_event(event):
    if event == 'RaceStarted':
        res = (1, event)
    elif event[4] == 'C':
        res = (2, event[:3]) # e.g (2, 'FRA')
    else:
        res = (3, [event[:3], event[-1:]]) # (3, 'FRA', 3.0)
    return res

def get_event_time(date, race_number, event):
    data = get_race_data(date, race_number)
    events_frame = data['events']
    event_type, parts = parse_event(event)
    if event_type == 1:
        test = events_frame['Event'] == 'RaceStarted'
    elif event_type == 2:
        test = ((events_frame['Event'] == 'CrossedFinish') &
                (events_frame['Boat'] == parts))
    else:
        test = ((events_frame['Event'] == 'MarkRounding') &
                (events_frame['Boat'] == parts[0]) &
                (events_frame['Opt1'].isin((int(parts[-1]), parts[-1]))))
    # fix: picked the last one in case there are multiple "RaceStarted" events
    return events_frame.loc[test]['Secs'].iloc[-1]

def get_mark_data(date, race_number):
    data = get_race_data(date, race_number)
    # returns positions of the marks at start time
    mark_data = pd.concat([data[m] for m in MARKS])
    start_time = get_event_time(date, race_number, "RaceStarted")
    return mark_data.loc[abs(mark_data['Secs'] - start_time) < .5]

def get_boat_color(boat_name):
    colors = {"USA": "black", "NZL": "red", "GBR": "purple", "FRA": "green",
              "GBR": "orange", "SWE": "yellow", "JPN": "white"}
    return colors[boat_name]

def get_boat_data(date, race_number, event, interval, freq):
    data = get_race_data(date, race_number)
    competitors = get_competitors(date, race_number)
    res = []
    for boat_name in competitors:
        boat_data = data[boat_name]

        # normalize times to the start time
        boat_data['Secs'] = boat_data['Secs'] - get_event_time(date, race_number, event)

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
        boat_data['Color'] = get_boat_color(boat_name)
        res.append(boat_data.iloc[::freq,:])
    return pd.concat(res)

def gen_outline_coords(row):
    heading = row["Hdg"]
    pos = [row['Lat'], row['Lon']]
    # return np array (2, num_vertices)
    return np.array(graph.draw_boat(pos, np.radians(heading))).transpose()
