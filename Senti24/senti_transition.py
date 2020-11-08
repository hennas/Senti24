import time
import logging
import pandas as pd
"""
The created dataframe is:
    to  to  to
from
from
from
"""


class SentiTransition:
    def __init__(self):
        # Set up logger
        self.logger = logging.getLogger('senti-transition')
        self.logger.info('Initializing SentiTranstitions')
        # Sentiment classes
        self.classes = ['pos', 'neg', 'neu']
        self.transitions = {
            'pos_pos': 0, 'pos_neg': 0, 'pos_neu': 0,
            'neg_pos': 0, 'neg_neg': 0, 'neg_neu': 0,
            'neu_pos': 0, 'neu_neg': 0, 'neu_neu': 0
        }
        # Initialize result DataFrame
        self.df = pd.DataFrame([[0, 0, 0] for i in range(3)], self.classes, self.classes)

    def get_class(self, val):
        """
        Use advanced logic to determine if the sentiment of a title is positive, negative, or neutral ([-0.5,0.5])
        :param val: Sentiment score
        :return: Neutral, negative, or neutral classification
        """
        if val > 0.5:
            return 'pos'
        elif val < -0.5:
            return 'neg'
        return 'neu'

    def calculate_transitions(self, data):
        """
        Calculate the sentiment transitions for the given data. Also saves the result
        :param data: Thread data with sentiment scores
        :return: Nothing
        """
        self.logger.info('Starting transition calculations')
        start = time.time()
        for i in range(len(data)-1):
            self.transitions['_'.join([self.get_class(data[i]), self.get_class(data[i+1])])] += 1
        self.logger.info(f'Transitions calculated, process took {time.time()-start}s')
        self.save_transitions()

    def save_transitions(self):
        """
        Saves the sentiment transitions to data/sentiment-transitions.csv
        :return: Nothing
        """
        self.logger.info('Saving results')
        start = time.time()
        for key in self.transitions.keys():
            frm, to = key.split('_')
            self.df.loc[[frm], [to]] = self.transitions[key]
        self.df.to_csv('data/sentiment-transitions.csv')
        self.logger.info(f'Results saved, took {time.time()-start}s')
        self.logger.info(f'The result is:\n{self.df}')


if __name__ == '__main__':
    # Set logging format
    logging.basicConfig(format='%(asctime)s %(module)s: %(message)s', level=logging.INFO,
                        datefmt='%H:%M:%S', filename='logs/senti-transitions.log', filemode='w')
    # Read the sentiment dat
    data = pd.read_csv('sentiment-data.csv')
    # Create the SentiTransition object
    st = SentiTransition()
    # Get a list of sentiment averages
    s_average = data['senti_avg'].values
    # Calculate the number of different transitions, and save result as csv
    st.calculate_transitions(s_average)
    # Save the result as .csv
    # st.save_transitions()
