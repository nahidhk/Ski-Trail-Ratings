from math import degrees, atan2
from typing import Tuple
from typing import List
import matplotlib.pyplot as plt
import pandas as pd

import helper


def get_label_placement(df: pd.DataFrame, length: int, flip_lat_lon: bool) -> Tuple[float, float]:
    """
    Accepts a point dataframe, length of trail/lift name, and orientation and 
    returns the best placement and rotation for a label.

    #### Arguments:

    - df - trail/lift point_df
    - length - name length
    - flip_lat_lon - bool

    #### Returns:

    - (point, angle) - tuple with the location and angle for the label
    """
    point_count = len(df.coordinates)
    point_gap = sum(helper.calculate_dist(df.coordinates)[1:])/point_count
    letter_size = 10 / point_gap
    label_length = point_gap * length * letter_size
    label_length_in_points = int(label_length / point_gap)
    point = int(len(df.coordinates)/2)
    angle_list = []
    valid_list = []
    for i, _ in enumerate(df.coordinates):
        valid = False
        if helper.get_trail_length(df.coordinates[0:i]) > label_length / 2:
            if helper.get_trail_length(df.coordinates[i:-1]) > label_length / 2:
                valid = True
        if i == 0:
            ang = 0
        else:
            dx = (df.lat[i])-(df.lat[i-1])
            dy = (df.lon[i])-(df.lon[i-1])
            ang = degrees(atan2(dx, dy))
        angle_list.append(ang)
        valid_list.append(valid)
    frac_correct = (1, 0, 0)
    for i, _ in enumerate(angle_list):
        if valid_list[i]:
            slice = angle_list[i-int(label_length_in_points / 2):i +
                               int(label_length_in_points / 2)]
            if len(slice) == 0:
                continue
            expected = sum(slice) / len(slice)
            frac_correct_current = 0
            correct = 0
            for value in slice:
                if abs(value-expected) < 5:
                    correct += 1
            frac_correct_current = correct / len(slice)
            if frac_correct_current > frac_correct[1]:
                frac_correct = (i, frac_correct_current, 0)
    if frac_correct[1] != 0:
        point = frac_correct[0]
    if point == 0:
        dx = 0
        dy = 0
    else:
        dx = (df.lat[point])-(df.lat[point-1])
        dy = (df.lon[point])-(df.lon[point-1])
        if point > 1 and dx == 0 and dy == 0:
            dx = (df.lat[point])-(df.lat[point-2])
            dy = (df.lon[point])-(df.lon[point-2])
    ang = degrees(atan2(dx, dy))
    if flip_lat_lon:
        if ang < -90:
            ang -= 180
        if ang > 90:
            ang -= 180
        return(point, ang)
    ang -= 90
    if ang < -90:
        ang += 180
    return(point, ang)


def find_map_size(trails: List[dict], lifts: List[dict]) -> Tuple[float, float]:
    """
    Calculates the size of the map

    #### Arguments:

    - trails - list of trail dicts
    - lifts - list of lift dicts

    #### Returns:

    - (x_length, y_length) - floats for the size (in km of the ski area)
    """
    mountain_max_lat = -90
    mountain_min_lat = 90
    mountain_max_lon = -180
    mountain_min_lon = 180
    for categeory in [trails, lifts]:
        for entry in categeory:
            trail_max_lat = entry['points_df']['lat'].max()
            trail_min_lat = entry['points_df']['lat'].min()
            if trail_max_lat > mountain_max_lat:
                mountain_max_lat = trail_max_lat
            if trail_min_lat < mountain_min_lat:
                mountain_min_lat = trail_min_lat
            trail_max_lon = entry['points_df']['lon'].max()
            trail_min_lon = entry['points_df']['lon'].min()
            if trail_max_lon > mountain_max_lon:
                mountain_max_lon = trail_max_lon
            if trail_min_lon < mountain_min_lon:
                mountain_min_lon = trail_min_lon
    top_corner = (mountain_max_lat, mountain_max_lon)
    bottom_corner = (mountain_min_lat, mountain_max_lon)
    bottom_corner_alt = (mountain_min_lat, mountain_min_lon)
    x_length = helper.calculate_dist([top_corner, bottom_corner])[1] / 1000
    y_length = helper.calculate_dist(
        [bottom_corner, bottom_corner_alt])[1] / 1000
    return(x_length, y_length)


def format_map_template(trails: List[dict], lifts: List[dict], mountain: str, direction: str) -> None:
    """
    Create the base template for the map

    #### Arguments:

    - trails - list of trail dicts
    - lifts - list of trail dicts
    - mountain - name of mountain
    - direction - what way the mountain faces

    #### Returns:

    - Void
    """
    x_length, y_length = find_map_size(trails, lifts)

    if 's' in direction or 'n' in direction:
        temp = x_length
        x_length = y_length
        y_length = temp

    if mountain != '':
        mountain = helper.format_name(mountain)
        size = int(x_length*10)
        if size > 25:
            size = 25
        if size < 5:
            size = 5
    else:
        size = 0
    plt.subplots(figsize=(x_length*2, ((y_length*2) + size * .04)))

    top_loc = (y_length*2) / ((y_length*2) + size * .02)
    bottom_loc = 1 - top_loc
    plt.title(mountain, fontsize=size, y=1, pad=size * .5)

    plt.subplots_adjust(left=0, bottom=bottom_loc, right=1,
                        top=top_loc, wspace=0, hspace=0)
    plt.axis('off')
    plt.xticks([])
    plt.yticks([])

    if size > 16:
        size = 16
    plt.gcf().text(0.5, 0, 'Sources: USGS and OpenStreetMaps',
                   fontsize=size/2.3, ha='center', va='bottom')
    add_legend(trails[0], direction, size / 2, bottom_loc)


def place_object(object_dict: dict) -> None:
    """
    Places objects on the map.

    #### Arguments:

    - object_dict - dict {
            'points_df' (dataframe),
            'name' (str),
            'is_area' (bool),
            'difficulty_modifier' (float,)
            'direction' (char),
            'color' (str)
            }

    #### Returns:

    - Void
    """
    lat_mirror = 1
    lon_mirror = -1
    flip_lat_lon = False
    if 'e' in object_dict['direction'] or 'E' in object_dict['direction']:
        lat_mirror = -1
        lon_mirror = 1
    if 's' in object_dict['direction'] or 'S' in object_dict['direction']:
        lon_mirror = 1
        flip_lat_lon = True
    if 'n' in object_dict['direction'] or 'N' in object_dict['direction']:
        lat_mirror = -1
        flip_lat_lon = True

    point, ang = get_label_placement(
        object_dict['points_df'][['lat', 'lon', 'coordinates']], len(object_dict['name']), flip_lat_lon)

    if not flip_lat_lon:
        X = object_dict['points_df'].lat
        Y = object_dict['points_df'].lon
    if flip_lat_lon:
        X = object_dict['points_df'].lon
        Y = object_dict['points_df'].lat
        temp = lat_mirror
        lat_mirror = lon_mirror
        lon_mirror = temp
    if not object_dict['is_area']:
        if object_dict['difficulty_modifier'] == 0:
            plt.plot(X * lat_mirror, Y * lon_mirror, c=object_dict['color'])
        if object_dict['difficulty_modifier'] > 0:
            plt.plot(X * lat_mirror, Y * lon_mirror,
                     c=object_dict['color'], linestyle='dashed')
    if object_dict['is_area']:
        if object_dict['difficulty_modifier'] == 0:
            plt.fill(X * lat_mirror, Y * lon_mirror,
                     alpha=.1, fc=object_dict['color'])
            plt.fill(X * lat_mirror, Y * lon_mirror,
                     ec=object_dict['color'], fc='none')
        if object_dict['difficulty_modifier'] > 0:
            plt.fill(X * lat_mirror, Y * lon_mirror,
                     alpha=.1, fc=object_dict['color'])
            plt.fill(X * lat_mirror, Y * lon_mirror,
                     ec=object_dict['color'], fc='none', linestyle='dashed')
    if object_dict['color'] == 'gold':
        object_dict['color'] = 'black'
    if helper.get_trail_length(object_dict['points_df'].coordinates) > 200:
        plt.text(X[point] * lat_mirror, Y[point] * lon_mirror, object_dict['name'], {
            'color': object_dict['color'], 'size': 2, 'rotation': ang}, ha='center',
            backgroundcolor='white', va='center', bbox=dict(boxstyle='square,pad=0.01',
                                                            fc='white', ec='none'))


def add_legend(trail: dict, direction: str, size: float, legend_offset: float) -> None:
    """
    Adds the legend box to the map template.

    #### Arguments:

    - trail - single trail dict
    - direction - what direction the mountain faces
    - size - font size to use
    - legend_offset - amount of negative offset to line the legend up vertically 

    #### Returns:

    - Void
    """
    if size > 8:
        size = 8
    if size <= 2.5:
        return
    lat_mirror = 1
    lon_mirror = -1
    flip_lat_lon = False
    if 'e' in direction or 'E' in direction:
        lat_mirror = -1
        lon_mirror = 1
    if 's' in direction or 'S' in direction:
        lon_mirror = 1
        flip_lat_lon = True
    if 'n' in direction or 'N' in direction:
        lat_mirror = -1
        flip_lat_lon = True

    if flip_lat_lon:
        y = trail['points_df'].lat.to_list()[0]
        x = trail['points_df'].lon.to_list()[0]
        temp = lat_mirror
        lat_mirror = lon_mirror
        lon_mirror = temp
    else:
        x = trail['points_df'].lat.to_list()[0]
        y = trail['points_df'].lon.to_list()[0]

    x *= lat_mirror
    y *= lon_mirror
    plt.plot(x, y, c='green', label='Easy')
    plt.plot(x, y, c='royalblue', label='Intermediate')
    plt.plot(x, y, c='black', label='Advanced')
    plt.plot(x, y, c='red', label='Expert')
    plt.plot(x, y, c='gold', label='Extreme')
    plt.plot(x, y, c='black', linestyle='dotted', label='Gladed')
    plt.legend(fontsize=size, loc='lower center', bbox_to_anchor=(
        0.5, - legend_offset), frameon=False, ncol=3)
