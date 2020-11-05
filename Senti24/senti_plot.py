import time
import logging
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


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

    def draw(self, data: 'DataFrame', save: bool = False):
        """
        Draws a plot of the average sentiment for each year/month in the given data
        :param data: [year, month, sentiment]
        """
        self.logger.info('Calculating averages for each month')
        start = time.time()
        obs = {}  # Sentiment observations
        # Extract unique years
        for year in data['year'].unique():
            # Calculate average sentiment for each month
            for month in data[data['year'] == year]['month'].unique():
                avgs = data[(data['year'] == year) & (data['month'] == month)]['senti_avg'].values
                obs[f'{year}-{month:02d}'] = sum(avgs)/len(avgs)
        self.logger.info(f'Averages calculated, took {time.time()-start}s')
        # Save the result
        if save:
            self.save_stats(obs)
        self.logger.info('Drawing the plot')
        # Creating the figure
        fig = plt.figure()
        ax = plt.subplot(111)
        # Adding sentiments to the plot
        obs_range = range(len(list(obs.keys())))
        ax.plot(obs_range, list(obs.values()), color='blue', linewidth=4)
        # Adding ticks and labels
        labels = list(obs.keys())
        for i in range(1, len(labels), 2):
            labels[i] = ''
        plt.xticks(obs_range, labels, rotation=50)
        plt.title('Average sentiment scores on a monthly basis', fontsize=20)
        plt.ylabel('Average sentiment', fontsize=10)
        plt.xlabel('Date', fontsize=10)
        ax.legend()
        # Showing the plot
        plt.show()
        self.logger.info('Drawing complete')

    def calculate_averages(self, db: pd.DataFrame) -> dict:
        # Extract unique years
        obs = {}
        for year in db['year'].unique():
            # Calculate average sentiment for each month
            for month in db[db['year'] == year]['month'].unique():
                avgs = db[(db['year'] == year) & (db['month'] == month)]['senti_avg'].values
                obs[f'{year}-{month:02d}'] = sum(avgs) / len(avgs)
        return obs

    def draw_to_gui(self, db: pd.DataFrame):
        self.logger.info('Drawing figure for the GUI')
        obs = self.calculate_averages(db)  # Sentiment observations
        fig = Figure(dpi=300)
        axis = fig.add_subplot(1, 1, 1)
        obs_range = range(len(list(obs.keys())))
        axis.plot(obs_range, list(obs.values()), color='blue', linewidth=2.5)
        labels = list(obs.keys())
        for i in range(1, len(labels), 2):
            labels[i] = ''
        axis.set_title('Average sentiment scores on a monthly basis')
        axis.set_xticks(range(len(labels)))
        axis.set_xticklabels(labels, rotation=90, fontsize=7)
        axis.set_xlabel('Date', fontsize=18)
        axis.set_ylabel('Average sentiment', fontsize=18)
        self.logger.info('Done drawing')
        return fig

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

