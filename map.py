import math

import geopandas as gpd
import numpy as np
from geopandas import GeoDataFrame
from matplotlib.lines import Line2D
from shapely import wkt
from shapely.geometry import LineString
import matplotlib.pyplot as plt
from matplotlib import axes
import pandas as pd
import constants
from bokeh import palettes


def plot(data: pd.DataFrame, ax: axes.Axes, attribute: str, secondary: str):
    # Create state and county Geoframes
    color_key = constants.MAP_ATTRIBUTES[attribute]
    data.reset_index(inplace=True, drop=True)
    county_boundaries = GeoDataFrame(data, geometry=data['county_boundary'])

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
    county_boundaries.plot(ax=ax, edgecolor='k', color=[color_map[str(key)] for key in data['RANGES']])

    color_handles = [Line2D([0], [0], color=color_map[interval],
                           marker='o', linestyle='none') for interval in intervals]
    color_labels = [interval for interval in intervals]

    legend1 = plt.legend(handles=color_handles,
                         labels=color_labels,
                         title=attribute, loc='lower right')

    for handle in legend1.legendHandles:
        handle._sizes = [50]

    ax.add_artist(legend1)

    # Set axis settings
    ax.set_aspect('auto')
    plt.ylim([23, 50])
    plt.xlim([-125, -67])
    plt.xlabel("Longitude", size=16)
    plt.ylabel("Latitude", size=16)
