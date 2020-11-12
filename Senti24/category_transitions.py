import logging
import pandas as pd
from time import time


class CategoryTransitions:
    def __init__(self, data: pd.DataFrame, save_to: str):
        self.logger = logging.getLogger('category-transitions')
        self.data = data
        self.save_to = save_to

    def calculate_category_transitions(self, categories):
        """
        Calculates all category transitions. Assumes that the given column of categories is
        in the right order, i.e., the threads are organized in an ascending order by datetime.
        Return dictionary where keys are transition pairs, e.g. (Question, Announcement), and
        values are the number of occurrences for each transition pair
        """
        unique_cats = categories.unique()
        transition_counts = {}

        for c1 in unique_cats:
            for c2 in unique_cats:
                transition_counts[(c1, c2)] = 0

        for i in range(len(categories) - 1):
            transition_counts[(categories[i], categories[i + 1])] += 1

        return transition_counts

    def cross_table(self, unique_cats, transitions):
        """
        Forms a cross table for transition counts, and saves it as a csv file
        """
        table = pd.DataFrame(columns=unique_cats, index=unique_cats)
        for k, v in transitions.items():
            table.loc[k[0], k[1]] = v
        table.to_csv(f'{self.save_to}')

    def get_transitions(self):
        """
        Goes through the transition calculation process
        :return: Nothing
        """
        start = time()
        self.logger.info('Starting transition calculation')
        t_counts = self.calculate_category_transitions(self.data)
        self.logger.info(f'Done calculating transitions, took {time()-start}s')
        self.logger.info(f'Saving result to {self.save_to}')
        self.cross_table(self.data.unique(), t_counts)
        self.logger.info('Results saved!')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(module)s: %(message)s', level=logging.INFO,
                        datefmt='%H:%M:%S', filename='logs/category-transitions.log', filemode='w')
    data = pd.read_csv('data/database.csv')
    ct = CategoryTransitions(data.simple_heuristic_cat, 'data/simple_transitions.csv')
    ct.get_transitions()

    # t_counts = ct.calculate_category_transitions(data.simple_heuristic_cat)
    # ct.cross_table(data.simple_heuristic_cat.unique(), t_counts)
