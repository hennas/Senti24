import pandas as pd
import logging
from nltk import word_tokenize
"""
Categorizing the thread titles with the simple heuristic
"""

class Categorizer:
    def __init__(self, data, sentiadjs, questions, negations, swears):
        self.logger = logging.getLogger('Categorizer')
        self.data = data
        self.sentiadjs = sentiadjs
        self.questions = questions
        self.negations = negations
        self.swears = swears
        self.features = ['title_length', 'text_length', 'n_of_words_title', 'n_of_words_text',
                         'n_of_question_marks', 'n_of_exclamation_marks', 'n_of_question_words', 
                         'n_of_swear_words', 'n_of_negatives', 'n_of_neg_adjectives', 
                         'n_of_pos_adjectives', 'neg_adj_avg_sentiment', 'pos_adj_avg_sentiment'
                         ]
        self.feature_val_dict = {k: [] for k in self.features}
        
        
    def extract_features(self, texts, titles):
        """
        Extracts the features from thread titles and texts to use them in categorization.
        Features to extract:
            + Number of characters in title
            + Number of characters in text
            + Number of words in title (excluding chars ! and ?)
            + Number of words in text (excluding chars ! and ?)
            + Number of question marks in title and text (total)
            + Number of exclamation marks in title and text (total)
            + Number of question words in title and text (total)
            + Number of swear words in title and text (total)
            + Number of negations (such as 'no') in title and text (total)
            + Number of positive adjectives in title and text (total)
            + Number of negative adjectives in title and text (total)
            + Average of the sentiments of the positive adjectives
            + Average of the sentiments of the negative adjectives
        """
        for i, text in enumerate(texts):
            if i % 100000 == 0:
                self.logger.info(f"Feature extraction in process for thread number %s" % str(i+1))
            title = titles[i]
            self.feature_val_dict['title_length'].append(len(title))
            self.feature_val_dict['text_length'].append(len(text))
            
            text_tokens = word_tokenize(text)
            title_tokens = word_tokenize(title)
            
            self.feature_val_dict['n_of_words_title'].append(len([t for t in title_tokens if t != '?' and t != '!']))
            self.feature_val_dict['n_of_words_text'].append(len([t for t in text_tokens if t != '?' and t != '!']))
            
            all_tokens = [*text_tokens, *title_tokens]
            n_of_qmarks = 0
            n_of_emarks = 0
            n_of_qwords = 0
            n_of_swords = 0
            n_of_negatives = 0
            n_of_neg_adj = 0
            n_of_pos_adj = 0
            neg_adj_s_sum = 0
            pos_adj_s_sum = 0
            
            for t in all_tokens:
                if t == '?':
                    n_of_qmarks += 1
                elif t == '!':
                    n_of_emarks += 1
                elif self.negations.get(t,0) != 0:
                    n_of_negatives += 1
                elif self.questions.get(t,0) != 0:
                    n_of_qwords += 1
                elif self.swears.get(t,0) != 0:
                    n_of_swords += 1
                else:
                    adj_s = self.sentiadjs.get(t,0)
                    if adj_s > 0:
                        n_of_pos_adj += 1
                        pos_adj_s_sum += adj_s
                    elif adj_s < 0:
                        n_of_neg_adj += 1
                        neg_adj_s_sum += adj_s
            
            
            self.feature_val_dict['n_of_question_marks'].append(n_of_qmarks)
            self.feature_val_dict['n_of_exclamation_marks'].append(n_of_emarks)
            self.feature_val_dict['n_of_question_words'].append(n_of_qwords)
            self.feature_val_dict['n_of_swear_words'].append(n_of_swords)
            self.feature_val_dict['n_of_negatives'].append(n_of_negatives)
            self.feature_val_dict['n_of_neg_adjectives'].append(n_of_neg_adj)
            self.feature_val_dict['n_of_pos_adjectives'].append(n_of_pos_adj)
            
            self.feature_val_dict['neg_adj_avg_sentiment'].append(neg_adj_s_sum / n_of_neg_adj if neg_adj_s_sum != 0 else 0)
            self.feature_val_dict['pos_adj_avg_sentiment'].append(pos_adj_s_sum / n_of_pos_adj if pos_adj_s_sum != 0 else 0)

    def categorize_with_simple_heuristic(self):
        """
        Decides the main category of each thread with simple if else rules
        """
        categories = []
        for i in range(len(self.data)):
            thread = self.data.iloc[i]
            if thread.n_of_words_text > 300:
                if thread.text_s_sum < -2 or thread.n_of_swear_words > 20 or (thread.n_of_neg_adjectives > 10 and thread.n_of_neg_adjectives > thread.n_of_pos_adjectives):
                    categories.append('Negative Narration')
                elif thread.text_s_sum > 2 or (thread.n_of_pos_adjectives > 10 and thread.n_of_pos_adjectives > thread.n_of_neg_adjectives):
                    categories.append('Positive Narration')
                else:
                    categories.append('Narration')
            elif thread.n_of_question_words > 0 and thread.n_of_question_marks > 0 and thread.n_of_words_text < 40:
                categories.append('Question')
            elif thread.pos_adj_avg_sentiment >= 1.5 or thread.text_s_sum >= 3 or (thread.n_of_pos_adjectives > 10 and thread.n_of_pos_adjectives > thread.n_of_neg_adjectives):
                categories.append('Appreciation')
            elif thread.neg_adj_avg_sentiment <= -1.5 or thread.text_s_sum <= -3 or thread.n_of_swear_words > 10 or (thread.n_of_neg_adjectives > 10 and thread.n_of_neg_adjectives > thread.n_of_pos_adjectives):
                categories.append('Negative Reaction')
            else:
                categories.append('Announcement')
        return categories
            
    def categorize_main(self):
        """
        Main function for categorizing
        """
        self.logger.info("Starting to extract features")
        self.extract_features(self.data.text, self.data.title)
        
        self.logger.info("Adding the extracted features to the data frame")
        for feat in self.features:
            self.data[feat] = self.feature_val_dict[feat]
        
        self.logger.info("Starting simple categorization")
        self.data['simple_heuristic_cat'] = self.categorize_with_simple_heuristic()
        
        self.logger.info("Categories added to the data frame, and now saving the data frame")
        self.data.to_csv('sentiment-data+features.csv', index=False)

if __name__ == '__main__':
    # Initialize logging into the file "categorization.log"
    logging.basicConfig(filename="categorization.log",
                            filemode='a',
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
    
    data = pd.read_csv("data_combined_preprocessed.csv")
    
    sentiadjs = pd.read_csv("adjectives_and_sentiments.csv")
    sentiadjs.drop_duplicates('word', inplace=True)
    sentiadjs = sentiadjs.set_index('word').T.to_dict('records')[0]
    
    swears = {}
    question_words = {}
    negation_words = {}
    
    with open('swearing.txt', 'r', encoding='utf-8') as f:
        for line in f:
            x = line.rstrip()
            swears[x] = 1
            
    with open('q_words.txt', 'r', encoding='utf-8') as f:
        for line in f:
            x = line.rstrip()
            question_words[x] = 1
            
    with open('neg_words.txt', 'r', encoding='utf-8') as f:
        for line in f:
            x = line.rstrip()
            negation_words[x] = 1
            
    Categorizer(data, sentiadjs, question_words, negation_words, swears).categorize_main()