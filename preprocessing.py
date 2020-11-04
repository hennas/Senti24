import pandas as pd
import logging
import re
from nltk import word_tokenize

"""
Preprocessing the thread titles
"""

class PreProcessor:
    def __init__(self, data, stopwords):
        self.logger = logging.getLogger('PreProcessor')
        self.data = data
        self.stopwords = stopwords
        self.regex = re.compile("[a-z åäö\-_!?]")
        self.replace_with_space_chars = ["-","_"]

    def duplicate_removal(self, columns):
        """
        Removes duplicate rows from a dataframe (in place), matching based on the given column names.
        """
        self.data.drop_duplicates(columns, inplace=True)
        
    def stopword_removal(self, text):
        """
        Removes stopwords from the given text string, and retuns the cleaned result.
        """
        text_tokens = word_tokenize(text)
        tokens_without_sw = [word for word in text_tokens if not word in self.stopwords]
        return (" ").join(tokens_without_sw)

    def extra_char_removal(self, text):
        """
        Removes all other characters from the given text string except the following: a-z åäö-_!?;:() 
        (Note the space that is retained as well)
        """
        return "".join(self.regex.findall(text))
        
    def replace_with_space(self, text):
        """
        Replaces specified characters from the given text with space
        """
        for char in self.replace_with_space_chars:
            text = text.replace(char, " ")
        return text
        
    def extra_space_removal(self, text):
        """
        Removes extra spaces from the given text
        """
        return " ".join(text.split())
        
    def filter_sentences(self, sentences):
        """
        Takes a list of sentences, and filters them
        """
        filtered_sentences = []
        for t in sentences:
            try:
                t = str(t)
                t = t.lower()
                t = self.extra_char_removal(t)
                t = self.stopword_removal(t)
                t = self.replace_with_space(t)
                t = self.extra_space_removal(t)
                filtered_sentences.append(t)
            except Exception as e:
                print(e)
                filtered_sentences.append(t)
        return filtered_sentences
        
    def preprocess(self):
        """
        Main preprocessing function, does the following for the specified dataframe:
            - Duplicate removal (in place)
            - Title and text filtering: (in place)
                + Lowercasing
                + Removing extra characters
                + Removing stopwords
                + Replacing specified characters with space
                + Removing extra spaces
            - Removes rows where the title or text corresponds to nan or null after filtering, 
            as well as rows where length of title or text is less than or equal to 3 (Produces a copy)
            - Returns the cleaned dataframe (copy of the original)
        """
        self.logger.info("Starting duplicate removal")
        self.duplicate_removal(['title', 'datetime'])
        
        self.logger.info("Duplicate removal ended, starting filtering titles")
        self.data['title'] = self.filter_sentences(self.data.title)
        self.logger.info("Title filtering ended, starting filtering texts")
        self.data['text'] = self.filter_sentences(self.data.text)
        self.logger.info("Filtering finished")
        
        nans_titles = len(self.data[(self.data['title'] == 'nan') | (self.data['title'] == 'null')]) # There's titles like NAN1 and nan**, which become nan after cleaning
        nans_texts = len(self.data[(self.data['text'] == 'nan') | (self.data['text'] == 'null')])
        empty_strings_titles = len(self.data[[len(t) <= 3 for t in self.data['title']]])
        empty_strings_texts = len(self.data[[len(t) <= 3 for t in self.data['text']]])
        
        self.logger.info(f"Deleting %s rows, returning cleaned data frame" % str(empty_strings_titles + empty_strings_texts + nans_titles + nans_texts))
        
        self.data = self.data[(self.data['title'] != 'nan') & (self.data['title'] != 'null')]
        self.data = self.data[(self.data['text'] != 'nan') & (self.data['text'] != 'null')]
        self.data = self.data[[len(t) > 3 for t in self.data['title']]]
        return self.data[[len(t) > 3 for t in self.data['text']]]

if __name__ == '__main__':
    # Initialize logging into the file "preprocessing.log"
    logging.basicConfig(filename="preprocessing.log",
                            filemode='a',
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
    
    # Read Finnish stopwords into an array
    with open('finnishST.txt', 'r', encoding='utf-8') as f:
        stopwords = [x.rstrip() for x in f.readlines()]
        
    # Read data
    data_comb = pd.read_csv('data_combined.csv')
    # Delete NaNs
    data_comb = data_comb[~data_comb.title.isnull()]
    data_comb = data_comb[~data_comb.text.isnull()]
    
    data_f = PreProcessor(data_comb, stopwords).preprocess()
    data_f.to_csv("data_combined_preprocessed.csv", index = False)
    