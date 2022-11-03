import math

import pandas as pd
from bokeh import palettes
from matplotlib import pyplot as plt
from matplotlib import axes


def plot(data: pd.DataFrame, ax: axes.Axes, size_attriubte: str) -> None:

    data = data.loc[data['county_population'] >= 25000]
    data = data.dropna()

    level_categories = data['community_level'].unique()
    colors = palettes.cividis(len(level_categories))
    color_map = {str(level_categories[i]): colors[i] for i in range(len(level_categories))}

    for level in level_categories:
        df_category = data.loc[data['community_level'] == level]
        ax.scatter(df_category['percent_strongly_hesitant'] + df_category['percent_hesitant'],
                    1 - df_category['percent_vaccinated'],
                    s=df_category[size_attriubte] * 150,
                    c=color_map[str(level)],
                    label=str(level),
                    alpha=0.7)

    color_handles, color_labels = ax.get_legend_handles_labels()
    legend1 = plt.legend(color_handles, color_labels, title='Community Level', loc='upper right')

    median = math.floor(len(data[size_attriubte]) / 2)
    label_sizes = [data[size_attriubte].max() * 100,
                   sorted(data[size_attriubte])[median] * 100,
                   data[size_attriubte].min() * 100]

    for handle in legend1.legendHandles:
        handle._sizes = [50]

    legend2 = plt.legend(labels=label_sizes,
                         title=size_attriubte,
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
