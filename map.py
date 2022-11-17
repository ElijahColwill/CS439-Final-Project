import math

import geopandas as gpd
import numpy as np
from geopandas import GeoDataFrame
from matplotlib.lines import Line2D
from mplcursors import cursor
import matplotlib.pyplot as plt
from matplotlib import axes
import pandas as pd
import constants
from bokeh import palettes


def plot(data: pd.DataFrame, ax: axes.Axes, state_name: str, attribute: str, secondary: str):
    if state_name == 'Country View':
        country_view(data, ax, attribute)
    else:
        state_view(data, ax, state_name, attribute, secondary)


def country_view(data: pd.DataFrame, ax: axes.Axes, attribute: str):
    # Create state and county Geoframes
    color_key = constants.MAP_ATTRIBUTES[attribute]
    data.reset_index(inplace=True, drop=True)

    county_series = gpd.GeoSeries(data['county_boundary'])
    data['county_point'] = county_series.centroid

    county_boundaries = GeoDataFrame(data, geometry=data['county_boundary'])
    county_points = GeoDataFrame(data.copy(), geometry=data['county_point'].copy())

    # Create color map
    data['RANGES'] = pd.qcut(data[color_key], q=constants.BINS[attribute],
                             duplicates='drop', precision=2)
    data.sort_values(by='RANGES')

    intervals_array = data['RANGES'].unique().__array__()
    for idx, interval in enumerate(intervals_array):
        if isinstance(interval, float):
            if math.isnan(interval):
                intervals_array = np.delete(intervals_array, idx)

    intervals_array.sort()
    intervals = list(str(group) for group in intervals_array)

    colors = palettes.cividis(len(intervals))
    color_map = {str(intervals[i]): colors[i] for i in range(len(intervals))}
    color_map['nan'] = 'lightgray'

    # Plot
    county_boundaries.plot(ax=ax,
                           edgecolor=(0, 0, 0, 0.35),
                           color=[color_map[str(key)] for key in data['RANGES']])

    color_handles = [Line2D([0], [0], color=color_map[interval],
                            marker='o', linestyle='none') for interval in intervals]
    color_labels = [interval for interval in intervals]

    legend1 = plt.legend(handles=color_handles,
                         labels=color_labels,
                         title=attribute,
                         loc='lower right')

    for handle in legend1.legendHandles:
        handle._sizes = [50]

    ax.add_artist(legend1)

    plt.ylim([23, 50])
    plt.xlim([-125, -67])
    ax.set_aspect('auto')

    # Set axis settings
    plt.xlabel("Longitude", size=16)
    plt.ylabel("Latitude", size=16)


def state_view(data: pd.DataFrame, ax: axes.Axes, state_name: str, attribute: str, secondary: str):
    # Create state and county Geoframes
    data.reset_index(inplace=True, drop=True)

    county_series = gpd.GeoSeries(data['county_boundary'])
    data['county_point'] = county_series.centroid

    data_else = data.loc[data['state'] != state_name, :]
    data_state = data.loc[data['state'] == state_name, :]

    county_boundaries_else = GeoDataFrame(data_else, geometry=data_else['county_boundary'])
    county_boundaries_state = GeoDataFrame(data_state, geometry=data_state['county_boundary'])
    county_points = GeoDataFrame(data_state.copy(), geometry=data_state['county_point'].copy())

    # Plot
    county_boundaries_else.plot(ax=ax,
                                edgecolor=(0, 0, 0, 0.35),
                                color='lightgray')

    county_boundaries_state.plot(ax=ax,
                                 edgecolor=(0, 0, 0, 0.5),
                                 color='lightsteelblue')

    state_boundary = gpd.GeoSeries(data.loc[data['state'] == state_name, 'state_boundary'])
    minx, miny, maxx, maxy = state_boundary.total_bounds
    if state_name == 'Alaska':
        maxx = -130
    ax.set_xlim(minx - 2, maxx + 2)
    ax.set_ylim(miny - 2, maxy + 2)

    # Set axis settings
    plt.xlabel("Longitude", size=16)
    plt.ylabel("Latitude", size=16)
