import time
import json
import logging
import pandas as pd
import matplotlib.pyplot as plt


class SentiPlot:
    def __init__(self):
        self.logger = logging.getLogger('senti-plot')

    def month_avg(self, senti_sum: list) -> float:
        """
        Calculates the average monthly sentiment
        :param senti_sum: List of sentiment sums
        :return: The average sentiment
        """
        return sum(senti_sum)/len(senti_sum)

    def month_avg_nonneutral(self, senti_sum: list) -> float:
        """
        Calculates the average monthly sentiment excluding sentiment sums of 0
        :param senti_sum: List of sentiment sums
        :return: The average sentiment
        """
        senti_sum = [i for i in senti_sum if i != 0]
        return sum(senti_sum) / len(senti_sum)

    def draw(self, data: 'DataFrame', save: bool = False):
        """
        Draws a plot of the average sentiment for each year/month in the given data
        :param data: [year, month, sentiment]
        """
        self.logger.info('Calculating averages for each month')
        start = time.time()
        obs = {}  # Sentiment observations with 0s
        obs_nonneutral = {}  # Same, but excluding 0 sums
        # Extract unique years
        for year in data['year'].unique():
            # Calculate average sentiment for each month
            for month in data[data['year'] == year]['month'].unique():
            #for month in list(set(data[data['year'] == year]['month'].values)):
                avgs = data[(data['year'] == year) & (data['month'] == month)]['senti_avg'].values
                obs[f'{year}-{month:02d}'] = sum(avgs)/len(avgs)
                # self.month_avg(data[(data['year'] == year) & (data['month'] == month)]['s_sum'].values)
                # obs_nonneutral[f'{year}-{month:02d}'] = self.month_avg_nonneutral(data[(data['year'] == year)&(data['month'] == month)]['s_sum'].values)
        self.logger.info(f'Averages calculated, took {time.time()-start}s')
        # Save the result
        if save:
            self.save_stats(obs)
        # open('senti_avg.json', 'w').write(json.dumps(obs, indent=4))
        self.logger.info('Drawing the plot')
        # Creating the figure
        fig = plt.figure()
        ax = plt.subplot(111)
        # Adding sentiments to the plot
        obs_range = range(len(list(obs.keys())))
        # ax.bar(obs_range, list(obs_nonneutral.values()), color='darkgray', width=0.7, edgecolor='k', label='Non-neutral')
        ax.bar(obs_range, list(obs.values()), width=0.7, color='grey', edgecolor='k', label='All sentimets')
        # Adding ticks and labels
        plt.xticks(obs_range, list(obs.keys()), rotation=70)
        plt.ylabel('Average sentiment')
        plt.xlabel('Date')
        ax.legend()
        # Showing the plot
        plt.show()
        self.logger.info('Drawing complete')

    def save_stats(self, stats: dict):
        self.logger.info('Saving stats')
        start = time.time()
        keys = stats.keys()
        df = pd.DataFrame(columns=['year', 'month', 'avg'])
        for key in keys:
            year, month = key.split('-')
            df = df.append({'year': year, 'month': month, 'avg': stats[key]}, ignore_index=True)
        df.to_csv('senti_avg.csv')
        self.logger.info(f'Stats saved, took {time.time()-start}s')


if __name__ == '__main__':
    # Set logging format
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
    # Read the sentiment data
    data = pd.read_csv('sentiment-data.csv')
    # Draw the monthly plot
    SentiPlot().draw(data[['year', 'month', 'senti_avg']], True)

