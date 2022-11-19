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

from matplotlib import colors as mplcolors
import matplotlib.collections as collections


def plot(data: pd.DataFrame, ax: axes.Axes, state_name: str,
         attribute: str, secondary: str, view: str):
    data.reset_index(inplace=True, drop=True)
    if state_name == 'Country View':
        country_view(data, ax, attribute, view)
    else:
        state_view(data, ax, state_name, attribute, secondary)


def country_view(data: pd.DataFrame, ax: axes.Axes, attribute: str, view: str):
    # Create state and county Geoframes
    color_key = constants.MAP_ATTRIBUTES[attribute]

    county_series = gpd.GeoSeries(data['county_boundary'])
    data['county_point'] = county_series.centroid

    county_boundaries = GeoDataFrame(data, geometry=data['county_boundary'])
    if view == 'State':
        data['KEY'] = data[color_key].groupby(data['state']).transform('mean')
    else:
        data['KEY'] = data[color_key]

    # Create color map
    data['RANGES'] = pd.qcut(data['KEY'], q=constants.BINS[attribute],
                             duplicates='drop', precision=2)

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
    color_labels[0] = '(0, ' + color_labels[0][color_labels[0].index(',') + 1:]

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
    # Create state and county Geoframes, set up data
    color_key = constants.MAP_ATTRIBUTES[attribute]

    county_series = gpd.GeoSeries(data['county_boundary'])
    data['county_point'] = county_series.centroid

    data_else = data.loc[data['state'] != state_name, :]
    data_state = data.loc[data['state'] == state_name, :]
    data_state.reset_index(inplace=True, drop=True)
    data_counties = data_state.copy()

    county_boundaries_else = GeoDataFrame(data_else, geometry=data_else['county_boundary'])
    county_boundaries_state = GeoDataFrame(data_state, geometry=data_state['county_boundary'])
    county_points = GeoDataFrame(data_counties, geometry=data_counties['county_point'])

    # Create color map
    data_state['RANGES'] = pd.qcut(data_state[color_key], q=constants.BINS[attribute] - 1,
                                   duplicates='drop', precision=2)
    data_state.sort_values(by='RANGES', inplace=True)

    intervals_array = data_state['RANGES'].unique().__array__()
    for idx, interval in enumerate(intervals_array):
        if isinstance(interval, float):
            if math.isnan(interval):
                intervals_array = np.delete(intervals_array, idx)

    intervals_array.sort()
    intervals = list(str(group) for group in intervals_array)

    colors = palettes.cividis(len(intervals))
    color_map = {str(intervals[i]): colors[i] for i in range(len(intervals))}
    color_map['nan'] = 'lightgray'

    # Plot Boundaries
    county_boundaries_else.plot(ax=ax,
                                edgecolor=(0, 0, 0, 0.35),
                                color='lightgray')

    county_boundaries_state.plot(ax=ax,
                                 edgecolor=(0, 0, 0, 0.5),
                                 color='lightsteelblue')

    # Plot Points and Process Size Attribute
    size = 65
    secondary_attribute = constants.SECONDARY_MAP_ATTRIBUTES[secondary]
    if secondary != 'None':
        data_state[secondary_attribute].fillna(0, inplace=True)
        size_unscaled = data_state[secondary_attribute]

        # Configure Scaling
        s_min = size_unscaled.min()
        s_max = size_unscaled.max()
        size = ((size_unscaled - s_min) / (s_max - s_min)) * 100
        size[size < 5] = 5

    county_points.plot(ax=ax,
                       markersize=size,
                       color=[color_map[str(key)] for key in data_state['RANGES']])

    # Legends
    color_handles = [Line2D([0], [0], color=color_map[interval],
                            marker='o', linestyle='none') for interval in intervals]
    color_labels = [interval for interval in intervals]
    color_labels[0] = '(0, ' + color_labels[0][color_labels[0].index(',') + 1:]

    legend1 = plt.legend(handles=color_handles,
                         labels=color_labels,
                         title=attribute,
                         loc='upper right',
                         borderaxespad=0)

    for handle in legend1.legendHandles:
        handle._sizes = [50]

    ax.add_artist(legend1)

    if secondary != 'None':
        size_unscaled = data_state[secondary_attribute]
        size_unscaled.fillna(0)
        s_min = size_unscaled.min()
        s_max = size_unscaled.max()

        median = math.floor(len(data_state[secondary_attribute]) / 2)
        label_sizes = np.array([round(data_state[secondary_attribute].max(), 2),
                                round(sorted(data_state[secondary_attribute])[median], 2),
                                round(max(data_state[secondary_attribute].min(), 0.01), 2)])

        label_sizes_scales = ((label_sizes - s_min) / (s_max - s_min)) * 100

        size_handles = [Line2D([0], [0], color='gray',
                               marker='o', markersize=np.sqrt(size), linestyle='none') for size in label_sizes_scales]

        legend2 = plt.legend(handles=size_handles,
                             labels=list(label_sizes),
                             title=secondary,
                             loc='lower right',
                             labelspacing=2,
                             borderaxespad=0)

        for idx, handle in enumerate(legend2.legendHandles):
            handle._sizes = [max(label_sizes_scales[idx], 0.01)]

        ax.add_artist(legend2)

    # State zoom setup
    state_boundary = gpd.GeoSeries(data.loc[data['state'] == state_name, 'state_boundary'])
    minx, miny, maxx, maxy = state_boundary.total_bounds

    if state_name == 'Alaska':
        maxx = -130
    ax.set_xlim(minx - 2, maxx + 2)
    ax.set_ylim(miny - 2, maxy + 2)

    # Set axis settings
    plt.xlabel("Longitude", size=16)
    plt.ylabel("Latitude", size=16)

    # Set up cursor
    cr = cursor(ax, hover=2, highlight=True)

    @cr.connect('add')
    def cr_hover(sel):
        if not isinstance(sel.artist, collections.PathCollection):
            cr.remove_selection(sel)
            return

        selected = data_counties.iloc[sel.index, :]
        annotation_dict = {
            'County Name': f'{selected["county"]}',
            'State': f'{selected["state"]}',
            'Population': f'{selected["county_population"]}',
            'Percent Hesitant + Percent Strongly Hesitant':
                f'{str(math.floor((selected["percent_strongly_hesitant"] + selected["percent_hesitant"]) * 100))}%',
            'Percent Unvaccinated': f'{str(math.floor((1 - selected["percent_vaccinated"]) * 100))}%',
            'Community Level': f'{str(selected["community_level"])}',
            'Cases per 100k People': f'{str(selected["cases_100k"])}',
        }
        if secondary != 'None':
            annotation_dict[str(secondary)] = f'{str(selected[secondary_attribute])}'

        sel.annotation.set_text('\n'.join([f'{k}: {v}' for k, v in annotation_dict.items()]))
        sel.annotation.set(bbox=dict(facecolor=mplcolors.to_rgba('yellow')[:-1] + (1.0,)))
