import time
import logging
import argparse
import pandas as pd
from sentistrength import PySentiStr


class SentiScore:
    def __init__(self, jar_loc: str, data_loc: str):
        self.logger = logging.getLogger('senti-score')
        self.senti = PySentiStr()
        self.senti.setSentiStrengthPath(jar_loc)
        self.senti.setSentiStrengthLanguageFolderPath(data_loc)

    def get_sentiment(self, text: str or list) -> list:
        """
        Determine the sentiment of a given text
        :param text: Text to analyze
        :return: [Positive score, Negative score]
        """
        return self.senti.getSentiment(text, score='dual')

    def array_sentiment(self, arr: list) -> list:
        """
        Calculate the positive, negative, the sum of both sentiments for each str in the given array
        :param arr: Array of text
        :return: Sentiment [positive, negative, sum]
        """
        self.logger.info(f'Starting sentiment calculation for {len(arr)} strings')
        start = time.time()
        sentiments = self.get_sentiment(arr)
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

    def add_sentiment(self, db) -> pd.DataFrame:
        """
        Adds sentiment scores to the preprocessed data. Saves result to data/sentiment_scores.csv
        :param db: The preprocessed data
        :return: The modified database
        """
        process_start = time()
        # Extract texts and titles from the DB
        titles = db['title'].values
        texts = db['text'].values
        # Calculate sentiments
        title_sentiment = self.array_sentiment(titles)
        text_sentiment = self.array_sentiment(texts)
        # Add the sentiments to the DB
        self.logger.info('Adding sentiments to the database')
        db['title_s_pos'] = title_sentiment[0]
        db['title_s_neg'] = title_sentiment[1]
        db['title_s_sum'] = title_sentiment[2]
        db['text_s_pos'] = text_sentiment[0]
        db['text_s_neg'] = text_sentiment[1]
        db['text_s_sum'] = text_sentiment[2]
        db['senti_avg'] = (db['title_s_sum'] + db['text_s_sum']) / 2
        self.logger.info(f'Whole sentiment analysis done, took {process_start-time()}')
        self.logger.info('Saving result to data/sentiment-scores.csv')
        # Save the result
        db.to_csv('data/sentiment-scores.csv', index=False)
        return db


if __name__ == '__main__':
    # Set logging format
    logging.basicConfig(format='%(asctime)s %(module)s: %(message)s', level=logging.INFO,
                        datefmt='%H:%M:%S', filename='logs/senti-score.log', filemode='w')
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', type=str, help='Absolute path to SentiStrength.jar')
    parser.add_argument('-d', type=str, help='Absolute path to SentiStrength_DataFi')
    args = parser.parse_args()
    # Start SentiStrength
    senti = SentiScore(args.j, args.d)
    # Load the preprocessed data for sentiment analysis
    data = pd.read_csv('data/data_combined_preprocessed.csv')

    # Extract titles and text from the data
    titles = data['title'].values
    texts = data['text'].values
    # Calculate sentiments for titles and texts
    title_sentiment = senti.array_sentiment(titles)
    text_sentiment = senti.array_sentiment(texts)
    # Add sentiment to the data
    data['title_s_pos'] = title_sentiment[0]
    data['title_s_neg'] = title_sentiment[1]
    data['title_s_sum'] = title_sentiment[2]
    data['text_s_pos'] = text_sentiment[0]
    data['text_s_neg'] = text_sentiment[1]
    data['text_s_sum'] = text_sentiment[2]
    data['senti_avg'] = (data['title_s_sum'] + data['text_s_sum']) / 2
    # Save the result
    data.to_csv('sentiment-data-testrun.csv', index=False)

