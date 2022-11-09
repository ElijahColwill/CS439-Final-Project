import math
import warnings

import numpy as np
import pandas as pd
from bokeh import palettes
from matplotlib import pyplot as plt
from matplotlib import axes
from matplotlib.lines import Line2D

from matplotlib import colors as mplcolors
from mplcursors import cursor


def plot(data: pd.DataFrame, ax: axes.Axes, size_attribute: str,
         svi_min_threshold: float, svi_max_threshold: float,
         population_threshold: float) -> None:

    warnings.filterwarnings('ignore')
    data = data.loc[(data['SVI'] >= svi_min_threshold) & (data['SVI'] <= svi_max_threshold)]
    data = data.loc[data['county_population'] >= population_threshold]
    data = data.dropna()

    if size_attribute == 'SVI':
        data['normalized'] = data[size_attribute]
    else:
        max_value = data[size_attribute].max()
        min_value = data[size_attribute].min()
        data['normalized'] = (data[size_attribute] - min_value) \
                             / max_value - min_value

    data.reset_index(inplace=True)

    level_categories = ['Low', 'Medium', 'High']
    colors = palettes.cividis(len(level_categories))
    color_map = {str(level_categories[i]): colors[i] for i in range(len(level_categories))}

    ax.scatter(data['percent_strongly_hesitant'] + data['percent_hesitant'],
                   1 - data['percent_vaccinated'],
                   s=data['normalized'] * 150,
                   c=[color_map[str(key)] for key in data['community_level']],
                   alpha=0.7)

    color_handles = [Line2D([0], [0], color=color_map[level],
                           marker='o', linestyle='none') for level in level_categories]
    color_labels = [level for level in level_categories]

    legend1 = ax.legend(handles=color_handles,
                        labels=color_labels,
                        title='Community Level',
                        loc='upper right')

    for handle in legend1.legendHandles:
        handle._sizes = [50]

    median = math.floor(len(data[size_attribute]) / 2)
    label_sizes = [round(data[size_attribute].max() * 100, 2),
                   round(sorted(data[size_attribute])[median] * 100, 2),
                   round(max(data[size_attribute].min() * 100, 1), 2)]

    size_handles = [Line2D([0], [0], color='gray',
                            marker='o', markersize=np.sqrt(size), linestyle='none') for size in label_sizes]
    legend2 = plt.legend(handles=size_handles,
                         labels=label_sizes,
                         title=size_attribute,
                         loc='lower right',
                         labelspacing=2)
    for idx, handle in enumerate(legend2.legendHandles):
        handle._sizes = [max(label_sizes[idx], 1)]

    plt.xlabel("Percentage of Adults Hesitant/Strongly Hesitant", size=16)
    plt.ylabel("Percentage of Adults Unvaccinated", size=16)
    plt.title("Percentage of County Hesitant vs. Unvaccinated", size=18)

    ax.add_artist(legend1)
    ax.add_artist(legend2)
    ax.set_ylim(0.2, 0.8)

    cr = cursor(ax, hover=2, highlight=True)

    @cr.connect('add')
    def cr_hover(sel):
        selected = data.iloc[sel.index, :]
        annotation_dict = {
            'County Name': f'{selected["county"]}',
            'State': f'{selected["state"]}',
            'Population': f'{selected["county_population"]}',
            'Percent Hesitant + Percent Strongly Hesitant':
                f'{str(math.floor((selected["percent_strongly_hesitant"] + selected["percent_hesitant"]) * 100))}%',
            'Percent Unvaccinated': f'{str(math.floor((1 - selected["percent_vaccinated"]) * 100))}%',
            'Community Level': f'{str(selected["community_level"])}',
            'Cases per 100k People': f'{str(selected["cases_100k"])}',
            f'{size_attribute}': f'{str(math.floor(selected[size_attribute] * 100))}'
        }
        sel.annotation.set_text('\n'.join([f'{k}: {v}' for k, v in annotation_dict.items()]))
        sel.annotation.set(bbox=dict(facecolor=mplcolors.to_rgba('yellow')[:-1] + (1.0,)))
