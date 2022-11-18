import math

import matplotlib.pyplot as plt
from matplotlib import axes
import pandas as pd
import numpy as np
import constants


def plot(community_data: pd.DataFrame, attribute: str, ax: axes.Axes):
    label_dict = {}
    column = constants.STREAM_ATTRIBUTES[attribute]

    if attribute == 'Community Level':
        label_dict = {
            'Low': list(),
            'Medium': list(),
            'High': list()
        }

        for date in constants.REPORT_DATES:
            date_data = community_data.loc[community_data['date_updated'] == date, column]
            label_dict['Low'].append(len(date_data[date_data == 'Low']))
            label_dict['Medium'].append(len(date_data[date_data == 'Medium']))
            label_dict['High'].append(len(date_data[date_data == 'High']))
    else:
        community_data['RANGES'] = pd.qcut(community_data[column], q=6,
                                           duplicates='drop', precision=2)
        community_data.sort_values(by='RANGES', inplace=True)

        intervals_array = community_data['RANGES'].unique().__array__()
        for idx, interval in enumerate(intervals_array):
            if isinstance(interval, float):
                if math.isnan(interval):
                    intervals_array = np.delete(intervals_array, idx)

        intervals_array.sort()
        intervals = list(str(group) for group in intervals_array)

        label_dict = {interval: list() for interval in intervals}

        for date in constants.REPORT_DATES:
            date_data = community_data.loc[community_data['date_updated'] == date, 'RANGES']
            for interval in intervals_array:
                label_dict[str(interval)].append(len(date_data[date_data == interval]))

    ax.stackplot(constants.REPORT_DATES, label_dict.values(),
                 labels=label_dict.keys(), alpha=0.8)

    ax.legend(loc='upper left')
    ax.set_xlabel('Report Date')
    ax.set_ylabel(f'Number of Counties for each range of: {attribute}')

    plt.xticks(rotation=90)
    plt.tight_layout()
