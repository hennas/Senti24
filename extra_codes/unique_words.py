import time
import math
import logging
import argparse
import subprocess
import pandas as pd
from itertools import chain
from senti_score2 import SentiScore

"""
Memory magic with Python, extracts unique words from threads, adds FinnPos labels and sentiment scores
WAS NOT USED IN THE ANALYSIS
"""

class UniqueWords:
    def __init__(self, filename: str, save_to: str):
        self.logger = logging.getLogger('unique-words')
        self.senti = SentiScore('<ADD JAR HERE>', '<ADD SentiDataFI HERE>')
        self.filename = filename
        self.save_to = save_to
        self.db = None
        self.unique_word_result = 'unique-words.txt'
        self.finnPos_result = 'finnpos/labeled-unique'
        self.finnPos_parsed_path = 'finnpos/parsed-unique'
        self.sentiStr_result_path = 'senti-unique.txt'

    def load_database(self) -> pd.DataFrame:
        self.logger.info('Loading database')
        return pd.read_csv(self.filename)

    def create_word_list(self, from_start):
        if from_start:
            self.db = self.load_database()
            self.logger.info('Starting word list creation')
            # Get unique titles and texts
            titles, texts = self.get_unique()
            # Combine and parse
            unique_words = self.parse_unique(titles, texts)
            self.logger.info(f'Found {len(unique_words)} unique words')
            self.save_wordlist(unique_words)
        # FinnPos part
        self.run_FinnPos()
        #parsed_FinnPos = self.parse_FinnPos()
        #self.save_FinnPos_result(parsed_FinnPos)
        #senti_added = self.run_SentiStr(parsed_FinnPos)
        #self.save(senti_added)

    def get_unique(self) -> [str]:
        self.logger.info('Extracting unique titles and texts')
        titles = list(self.db['title'].unique())
        texts = list(self.db['text'].unique())
        self.logger.info('Title and text extraction done, removing DB from memory')
        self.db = None
        return titles, texts

    def parse_unique(self, titles: [str], texts: [str]) -> [str]:
        self.logger.info(f'Extracting unique words from {len(texts)} lines of text')
        # Each text/symbol in the database is separated with a space, so split with that
        title_splits = int(len(titles)/2)
        text_splits = int(len(texts)/2)

        self.logger.info('Splitting titles into two parts')
        titles1 = titles[0:title_splits]
        titles2 = titles[title_splits:]
        self.logger.info('Removing old title list from memory')
        titles = None
        self.logger.info('Splitting texts into two parts')
        texts1 = texts[0:text_splits]
        texts2 = texts[text_splits:]
        self.logger.info('Removing old texts list from memory')
        texts = None

        self.logger.info('Parsing 1st title split')
        titles1 = list(map(lambda x: list(set(x.split())), titles1))
        titles1 = list(set(chain.from_iterable(titles1)))
        self.logger.info('Parsing 2nd title split')
        titles2 = list(map(lambda x: list(set(x.split())), titles2))
        titles2 = list(set(chain.from_iterable(titles2)))
        self.logger.info('Combining titles and removing non uniques')
        titles = list(set(titles1 + titles2))
        titles1 = None
        titles2 = None

        self.logger.info('Parsing 1st text split')
        texts1 = list(map(lambda x: list(set(x.split())), texts1))
        texts1 = list(set(chain.from_iterable(texts1)))
        self.logger.info('Parsing 2nd text split')
        texts2 = list(map(lambda x: list(set(x.split())), texts2))
        texts2 = list(set(chain.from_iterable(texts2)))
        self.logger.info('Combining texts and removing non uniques')
        texts = list(set(texts1 + texts2))
        texts1 = None
        texts2 = None
        self.logger.info('Done splitting into unique words')

        self.logger.info('Removing duplicates from combination of titles and texts')
        return list(set(titles + texts))

    def save_wordlist(self, words: [str]):
        self.logger.info('Saving the unique words to unique-words.txt')
        f = open(self.unique_word_result, 'w')
        for word in words:
            f.write(word+'\n')
        f.close()

    def run_FinnPos(self):
        """
        self.logger.info('Running FinnPos labeling on the unique words')
        cmd = f'cat {self.unique_word_result} | ftb-label > {self.finnPos_result}'
        self.logger.info(f'Using command: {cmd}')
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        process.wait()
        self.logger.info('FinnPos process complete')
        """
        loop_round = 1
        line_num = sum(1 for line in open('unique-words.txt'))
        for i in range(0, int(math.ceil(line_num / 10000)) * 10000 + 1, 10000):
            cmd = f'cat {self.unique_word_result} | ftb-label > {self.finnPos_result}-{loop_round}.txt'
            self.logger.info(f'Using command: {cmd}')
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            process.wait()
            loop_round += 1
        self.logger.info('FinnPos process complete')

    def parse_FinnPos(self) -> pd.DataFrame:
        self.logger.info('Parsing FinnPos results')
        result = []
        file = open(self.finnPos_result, 'r')
        for line in file:
            line = line.split()
            if len(line) > 0:
                word = line[0]
                pos = line[3].split('|')[0].replace('[POS=', '').replace(']', '')
                result.append([word, pos])
                #result.append(' '.join([word, pos]))  # '\t' join would be better
        file.close()
        self.logger.info('Done parsing FinnPos results')
        return pd.DataFrame(result, columns=['word', 'pos'])

    def save_FinnPos_result(self, result: [str]):
        self.logger.info('Saving parsed FinnPos results')
        file = open(self.finnPos_parsed_path, 'w')
        for line in result:
            file.write(line+'\n')
        file.close()
        self.logger.info(f'Parsed FinnPos saved to {self.finnPos_parsed_path}')

    def run_SentiStr(self, finnPos_results: pd.DataFrame):
        words = finnPos_results['word'].values
        sentiments = self.senti.array_sentiment(words)
        finnPos_results['s_pos'] = sentiments[0]
        finnPos_results['s_neg'] = sentiments[1]
        return finnPos_results

    def save(self, result: pd.DataFrame):
        result.to_csv(self.sentiStr_result_path, index=False)


if __name__ == '__main__':
    # Set logging format
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S', filename='logs/unique.log', filemode='a')
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', default='data_combined_preprocessed.csv', type=str, help='Name of the database file')
    parser.add_argument('-s', '--save', type=str, default='unique/', help='Directory where results will be stored')
    args = parser.parse_args()
    # Start the process
    UniqueWords(args.file, args.save).create_word_list(from_start=False)

    # Word | forms | positive | negative
