import geopandas as gpd
from geopandas import GeoDataFrame
from shapely import wkt
from shapely.geometry import LineString
import matplotlib.pyplot as plt
from matplotlib import axes
import pandas as pd


def plot(data: pd.DataFrame, ax: axes.Axes, attribute: str, secondary: str):
    print(f'Called Map: {attribute}, {secondary}')
    # print(data.head())
    # print(type(data.iloc[0]['state_boundary']))
    data['state_boundary'] = gpd.GeoSeries.from_wkt(data['state_boundary'])
    state_boundaries = GeoDataFrame(data, geometry=data['state_boundary'])
    data['county_boundary'] = gpd.GeoSeries.from_wkt(data['county_boundary'])
    county_boundaries = GeoDataFrame(data, geometry=data['county_boundary'])
    state_boundaries.plot(ax=ax, edgecolor='k', color='lightgray', zorder=1)
    # county_boundaries.plot(x=ax, edgecolor='k', color='lightgray', zorder=2)

    ax.set_aspect('auto')
    plt.ylim([23, 51])
    plt.xlim([-125, -65])


    # fig, ax = plt.subplots()
    # fig.set_size_inches(12, 5)
    # fig.set_dpi(125)
    # plt.show()
