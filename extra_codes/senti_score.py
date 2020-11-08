import json
import time
import logging
import argparse
import pandas as pd
from db_loader import DBLoader
from sentistrength import PySentiStr

"""
Old version of the sentiment calculation, use senti_score2.py instead
"""


""" THE OLD HTTP BASED SENTISTRENGTH 
class SentiStrengh:
    def __init__(self):
        self.url = 'http://sentistrength.wlv.ac.uk/results.php?text=$&submit=Detect+Sentiment+in+Finnish'
        self.regex = re.compile('\[sentence: (.*?)]')

    def get_sentiment(self, text: str):
        r = requests.get(self.url.replace('$', text).encode('utf-8'))
        sentiment = self.regex.search(r.text).group(1).split(',')
        return sentiment
"""

class SentiStrngth:
    def __init__(self, jar_loc: str, data_loc: str):
        self.logger = logging.getLogger('senti_logger')
        self.senti = PySentiStr()
        self.senti.setSentiStrengthPath(jar_loc)
        self.senti.setSentiStrengthLanguageFolderPath(data_loc)

    def sentiment(self, text: str or list) -> list:
        """
        Determine the sentiment of a given text
        :param text: Text to analyze
        :return: [Positive score, Negative score]
        """
        return self.senti.getSentiment(text, score='dual')

    def test(self, txt: str):
        print(self.senti.getSentiment(txt, score='scale'))

    def array_sentiment(self, arr: list) -> list:
        """
        Calculate the positive, negative, the sum of both sentiments for each str in the given array
        :param arr: Array of text
        :return: Sentiment [positive, negative, sum]
        """
        self.logger.info(f'Starting sentiment calculation for {len(arr)} strings')
        start = time.time()
        sentiments = self.sentiment(arr)
        self.logger.info(f'Sentiment calculation done, took: {time.time()-start}s')
        self.logger.info('Parsing sentiments')
        s_pos, s_neg, s_sum = ([] for i in range(3))
        start = time.time()
        for s in sentiments:
            s_pos.append(s[0])
            s_neg.append(s[1])
            s_sum.append(s[0]+s[1])
        self.logger.info(f'Sentiments parsed, took {time.time()-start}s')
        return [s_pos, s_neg, s_sum]


if __name__ == '__main__':
    # Set logging format
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('jar', type=str, help='Absolute path to SentiStrength.jar')
    parser.add_argument('data', type=str, help='Absolute path to SentiStrength_DataFi')
    args = parser.parse_args()
    # Start SentiStrength
    senti = SentiStrngth(args.jar, args.data)
    # Load the preprocessed data for sentiment analysis, drop NaN titles
    data = pd.read_csv('data/data_combined_preprocessed.csv').dropna(subset=['title'])
    # Calculate sentiments. Surprisingly the whole dataset can be given to SentiStrength as a single array just fine
    sentiments = senti.array_sentiment(data['title'].values)
    # Add sentiment to the data
    data['s_pos'] = sentiments[0]
    data['s_neg'] = sentiments[1]
    data['s_sum'] = sentiments[2]
    # Finally save the result
    data.to_csv('data_sentiment.csv')

