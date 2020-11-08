import logging
from time import time
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
import warnings
from random import sample, seed
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

try:
    from Senti24.zipfs_law import ZipfsLaw
    from Senti24.category_transitions import CategoryTransitions
except:
    from zipfs_law import ZipfsLaw
    from category_transitions import CategoryTransitions

"""
K-Means categorization of the threads
"""


class KmeansCategorization:
    def __init__(self):
        self.logger = logging.getLogger('kmeans')
        self.logger.info('Reading data/sentiment-data+features.csv')
        self.data = pd.read_csv('data/sentiment-data+features.csv')
        self.ids_by_year = self.load_thread_ids()
        self.features = [  # 'title_s_sum','text_s_sum',
            'senti_avg',  # 'title_length', 'text_length',
            'n_of_words_title', 'n_of_words_text',
            'n_of_question_marks', 'n_of_exclamation_marks',
            'n_of_question_words', 'n_of_swear_words',
            'n_of_negatives', 'n_of_neg_adjectives', 'n_of_pos_adjectives',
            # 'neg_adj_avg_sentiment', 'pos_adj_avg_sentiment'
        ]

    def load_thread_ids(self) -> [int]:
        """
        Reads the ids of threads from which adjectives were extracted
        :return: List of ids
        """
        self.logger.info('Loading thread ids')
        ids_files = [r'data/20{:02}_ids.txt'.format(i + 1) for i in range(8, 17)]
        ids_by_year = []
        for fname in ids_files:
            with open(fname, 'r') as f:
                ids_by_year.append([x.rstrip() for x in f.readlines()])
        self.logger.info('Thread ids loaded')
        return ids_by_year

    def elbow_method(self):
        """
        Tests k in range(2,10), and plots inertia for each k
        """
        self.logger.info('Using the elbow method')
        inertias = []

        k_vals = range(2, 10)
        for k in k_vals:
            km = KMeans(n_clusters=k)
            km.fit(self.scaler.transform(self.train_data[self.features]))
            inertias.append(km.inertia_)

        plt.figure(figsize=(12, 6))
        plt.plot(k_vals, inertias, 'bx-')
        plt.xlabel('Clusters')
        plt.ylabel('Inertia')
        plt.title('The Elbow Method to find the optimal n of clusters')
        self.logger.info('Done elbowing')
        plt.show()

    # def silhouette_method(self):
    # Takes TOO LONG to run
    # silhouette_avgs = {}
    # k_vals = range(2,10)
    # for k in k_vals:
    #   km = KMeans(n_clusters=k, random_state=10)
    #  km.fit(self.scaler.transform(self.train_data[self.features]))
    # silhouette_avgs[k] = silhouette_score(self.scaler.transform(self.train_data[self.features]), km.labels_)
    # return silhouette_avgs

    def plot_feature_distributions_by_cluster(self):
        """
        Used to observe feature distributions inside clusters. (Helps in determining the 'name' of a cluster)
        """
        for f in self.features:
            for i in range(0, self.km_final.n_clusters):
                self.all_data[self.all_data.labels == i][f].plot.hist(bins=40)
                plt.title(', '.join([f, f"cluster %s" % str(i)]))
                plt.show()
            input('Press enter to continue')

    def plot_feature_distributions(self):
        """
        Used to plot feature distributions in the training data
        """
        for f in self.features:
            self.train_data[f].plot.hist(bins=40)
            plt.title(f)
            plt.show()
            input('Press enter to continue')

    def kmeans_main(self):
        """
        Main function for K-means categorization:
            + Extracts training data
            + Standardizes the data
            + Trains K-means with half of the data, n of clusters decided with elbow mehod
            + Uses trained model to predict the class for the rest of the data
            + Categories, which have been manually determined, are added to the data
        Final data frame is in the variable 'all_data'
        """
        self.logger.info('Starting K-means')
        start = time()
        warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
        seed(10)
        train_ids = []
        all_ids = []
        for l in self.ids_by_year:
            train_ids.extend(sample(l, 50000))
            all_ids.extend(l)

        ids_data = self.data[self.data['thread_id'].isin(all_ids)]
        self.train_data = ids_data[ids_data['thread_id'].isin(train_ids)]
        self.test_data = ids_data[~ids_data['thread_id'].isin(train_ids)]
        # print(len(ids_data), len(self.train_data), len(self.test_data))

        self.scaler = StandardScaler().fit(ids_data[self.features])
        # self.plot_feature_distributions(self.train_data)
        # self.elbow_method()

        k = 6
        self.km_final = KMeans(n_clusters=k, random_state=10)
        self.km_final.fit(self.scaler.transform(self.train_data[self.features]))

        test_predict = self.km_final.predict(self.scaler.transform(self.test_data[self.features]))
        all_labels = pd.Series([*self.km_final.labels_, *test_predict])
        self.all_data = pd.concat([self.train_data, self.test_data], ignore_index=True)

        categories = all_labels.replace([0, 1, 2, 3, 4, 5],
                                        ['Short Text', 'Question', 'Question/Descriptive', 'Negative text',
                                         'Announcement', 'Rant'])

        self.all_data['labels'] = all_labels
        self.all_data['kmeans_cat'] = categories
        self.all_data = self.all_data.sort_values('datetime')

        self.logger.info(f'K-means done, took {time()-start}s')

        # print(len(all_labels), len(self.all_data))
        # for i in range(0,k):
        #   print(len(self.train_data[self.km_final.labels_ == i]))
        # for i in range(0,k):
        #   print(len(self.all_data[all_labels == i]))


if __name__ == '__main__':
    # Initialize logging into the file "logs/kmeans.log"
    logging.basicConfig(filename="logs/kmeans.log",
                        filemode='w',
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    # ids_files = [r"data\20{:02}_ids.txt".format(i + 1) for i in range(8, 17)] # Doesn't work properly on Linux
    #ids_files = [r'data/20{:02}_ids.txt'.format(i+1) for i in range(8, 17)]
    #ids_by_year = []
    #for fname in ids_files:
    #    with open(fname, 'r') as f:
    #        ids_by_year.append([x.rstrip() for x in f.readlines()])

    #data = pd.read_csv('data/sentiment-data+features.csv')
    km_obj = KmeansCategorization()
    km_obj.kmeans_main()

    # for i in range(0,6):
    #   print(km_obj.all_data[km_obj.all_data.labels == i].groupby('simple_heuristic_cat').count())

    # Fit Zipf's law
    fig = ZipfsLaw(km_obj.all_data.kmeans_cat).fit_zipfs_law()
    fig.savefig('zipf_kmeans.png', format="png")

    # Calculate category transitions
    CategoryTransitions(km_obj.all_data.kmeans_cat).get_transitions()
