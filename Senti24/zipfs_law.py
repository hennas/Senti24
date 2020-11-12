import logging
import pandas as pd
import numpy as np
from time import time
import scipy.stats as ss
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


class ZipfsLaw:
    def __init__(self, data: pd.DataFrame):
        self.logger = logging.getLogger('zips-law')
        self.cats = data

    def get_category_freqs(self, cats):
        """
        Calculates the frequency of each category in the given column of categories (Pandas series).
        Return a dictionary where the keys are categories and the values are the frequencies.
        """
        freqs = cats.value_counts()
        return freqs.to_dict()


    def get_category_ranks(self, val_dictionary):
        """
        Ranks the category frequencies from biggest to smallest.
        Parameter 'val_dictionary' is a dictionary where the keys are categories and the values are the frequencies.
        Returns a list of ranks.
        """
        return ss.rankdata([-1 * v for k, v in val_dictionary.items()])


    def power_law(self, x, a, b):
        """
        Calculates a*x^b
        """
        return a * np.power(x, b)


    def fit_zipfs_law(self):
        """
        First takes the logarithm of the frequencies and ranks and fits a linear line onto the points,
        as well as draws a plot of it.
        Then fits a power law curve onto the points and draws a plot of it.
        """
        self.logger.info("Starting to draw plot with Zipf's law")
        start = time()
        freqs = self.get_category_freqs(self.cats)
        ranks = self.get_category_ranks(freqs)
        freqs_ranks = sorted(list(zip(freqs.keys(), freqs.values(), ranks)), key=lambda x: x[2])
        log_freqs = [np.log(v[1]) for v in freqs_ranks]
        log_ranks = [np.log(v[2]) for v in freqs_ranks]
        a, b = np.polyfit(log_ranks, log_freqs, 1)

        freqs_sorted = [v[1] for v in freqs_ranks]
        ranks_sorted = [v[2] for v in freqs_ranks]
        params, cov = curve_fit(self.power_law, ranks_sorted, freqs_sorted)
        expected_zipf_freq = [freqs_sorted[0]/ i for i in range(1,len(ranks_sorted)+1)]
        # print(params)

        fig = plt.figure(figsize=(20, 8))
        ax1, ax2 = fig.subplots(1, 2)
        ax1.plot(ranks_sorted, freqs_sorted, 'bo', markersize=8, label="Data points")
        ax1.plot(ranks_sorted, self.power_law(np.array(ranks_sorted), *params), 'r--', linewidth=2, label="Power Law Fit")
        ax1.plot(ranks_sorted, expected_zipf_freq, 'b--', linewidth=2, label="Expected freq for Zipf's law")
        ax1.legend(loc="best")
        ax1.set_ylabel('frequency', fontsize=18)
        ax1.set_xlabel('rank', fontsize=18)
        ax1.set_title('Plot of category frequencies and ranks', fontsize=19)

        ax2.plot(log_ranks, log_freqs, 'bo', markersize=8, label="Data points")
        ax2.plot(log_ranks, a*np.array(log_ranks)+b, 'r--', linewidth=2, label="Linear Fit")
        ax2.legend(loc="best")
        ax2.set_ylabel('log(frequency)', fontsize=18)
        ax2.set_xlabel('log(rank)', fontsize=18)
        ax2.set_title('Log-log plot of category frequencies and ranks', fontsize=19)

        self.logger.info(f'Plot done, took {time()-start}')
        return fig


if __name__ == '__main__':
    data = pd.read_csv('data/database.csv')
    fig = ZipfsLaw(data.simple_heuristic_cat).fit_zipfs_law()
    fig.savefig('zipf.png', format="png")
