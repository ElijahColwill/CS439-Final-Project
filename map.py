import geopandas
from shapely.geometry import LineString
import matplotlib.pyplot as plt
from matplotlib import axes
import pandas as pd


def plot(data: pd.DataFrame, ax: axes.Axes, attribute: str, secondary: str):
    print(f'Called Map: {attribute}, {secondary}')
