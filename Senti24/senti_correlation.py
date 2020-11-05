import time
import logging
import pandas as pd
from scipy.stats import pearsonr


class SentiCorrelation:
    def __init__(self, db: pd.DataFrame):
        self.logger = logging.getLogger('senti-correlation')
        #self.df = self.read_csv()
        self.db = db

        # Happy Planet Index well-being score for 2009, 2012, and 2016
        # -> Have to use well-being instead of total HPI score, since in 2016 they changed how the score is calculated
        self.fi_hpi = [8.0, 7.4, 7.4]
        # Scores for the years 2013, 2014, 2015, 2016, 2017
        self.better_life_health = [69, 69, 65, 65, 70]
        self.better_life_satisfaction = [7.4, 7.4, 7.4, 7.4, 7.5]
        self.better_life_murder = [2.2, 1.8, 1.4, 1.5, 1.4]
        self.better_life_freetime = [14.89, 14.89, 14.89, 15.17, 15.17]
        self.better_life_unemployment = [1.75, 1.65, 1.73, 1.97, 2.33]
        # Scores for the years 2015, 2016, 2017
        self.world_happiness = [7.406, 7.413, 7.528]

    def read_csv(self):
        self.logger.info('Loading dataset')
        start = time.time()
        data = pd.read_csv('senti_avg.csv')
        self.logger.info(f'Done loading, took {time.time()-start}s')
        return data

    def get_year_average2(self, year: int) -> float:
        year_vals = self.df[self.df['year'] == year]['avg'].values
        return sum(year_vals)/len(year_vals)

    def get_year_average(self, data: pd.DataFrame, year: int) -> float:
        averages = data[data['year'] == year]['senti_avg'].values
        return sum(averages)/len(averages)

    def correlation(self) -> [str, float, int]:
        """
        Calculates the correlation between sentiment data and predefined index scores
        :return: [Index, Correlation, Data points]
        """
        hpi_year_averages = [self.get_year_average(self.db, year) for year in [2009, 2012, 2016]]
        better_life_averages = [self.get_year_average(self.db, year) for year in [2013, 2014, 2015, 2016, 2017]]
        world_happiness_averages = [self.get_year_average(self.db, year) for year in [2015, 2016, 2017]]
        result = []

        # HPI
        self.logger.info(f'Pearson\'s Correlation for HPI is {pearsonr(self.fi_hpi, hpi_year_averages)[0]}')
        result.append(['Happy Planet Index - Well-Being', round(pearsonr(self.fi_hpi, hpi_year_averages)[0], 3), len(hpi_year_averages)])

        # World Happiness
        self.logger.info(f'Pearson\'s Correlation for World Happiness is {pearsonr(self.world_happiness, world_happiness_averages)[0]}')
        result.append(['World Happiness Report - Happiness', round(pearsonr(self.world_happiness, world_happiness_averages)[0], 3), len(world_happiness_averages)])

        # Better Life Index
        self.logger.info(f'Pearson\'s Correlation for BL health is {pearsonr(self.better_life_health, better_life_averages)[0]}')
        result.append(['Better Life Index - Health', round(pearsonr(self.better_life_health, better_life_averages)[0], 3), len(better_life_averages)])

        self.logger.info(f'Pearson\'s Correlation for BL satisfaction is {pearsonr(self.better_life_satisfaction, better_life_averages)[0]}')
        result.append(['Better Life Index - Life Satisfaction', round(pearsonr(self.better_life_satisfaction, better_life_averages)[0], 3), len(better_life_averages)])

        self.logger.info(f'Pearson\'s Correlation for BL murder is {pearsonr(self.better_life_murder, better_life_averages)[0]}')
        result.append(['Better Life Index - Homicide rate', round(pearsonr(self.better_life_murder, better_life_averages)[0], 3), len(better_life_averages)])

        self.logger.info(f'Pearson\'s Correlation for BL free time is {pearsonr(self.better_life_freetime, better_life_averages)[0]}')
        result.append(['Better Life Index - Free time', round(pearsonr(self.better_life_freetime, better_life_averages)[0], 3), len(better_life_averages)])

        self.logger.info(f'Pearson\'s Correlation for BL unemployment is {pearsonr(self.better_life_unemployment, better_life_averages)[0]}')
        result.append(['Better Life Index - Unemployment', round(pearsonr(self.better_life_unemployment, better_life_averages)[0], 3), len(better_life_averages)])

        return result


    def hpi_correlation(self):
        """
        Calculates the Pearson correlation between HPI well-being score and the yearly average sentiment
        :return: None
        """
        self.logger.info('Calculating correlation with HPI well-being score')
        year_avgs = [self.get_year_average(self.sb, year) for year in [2009, 2012, 2016]]
        correlation, _ = pearsonr(self.fi_hpi, year_avgs)
        self.logger.info(f'The correlation is {correlation}')



if __name__ == '__main__':
    # Set logging format
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
    SentiCorrelation().correlation()
