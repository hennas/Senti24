import pandas as pd
from preprocessing import PreProcessor

with open('finnishST.txt', 'r', encoding='utf-8') as f:
    stopwords = [x.rstrip() for x in f.readlines()]

word_files = [r"finnpos\labeled_20{:02}.csv".format(i+1) for i in range(8,17)]

# Combine data frames
data = pd.DataFrame()
for fname in word_files:
    word_data = pd.read_csv(fname) 
    data = pd.concat([data, word_data], ignore_index=True)
    
# Preprocess: drop duplicates, take only non neutral adjectives, preprocess the words
data.drop_duplicates('word', inplace=True)
data = data[data['pos'] == 'ADJECTIVE']
data['sentiment'] = data['s_pos'] + data['s_neg']
data = data[data['sentiment'] != 0]
data.drop(columns=['pos', 's_pos', 's_neg'], inplace=True)
data = data[~data['word'].str.contains('http')]
data['word'] = PreProcessor(data, stopwords).filter_sentences(data.word)

# Save adjectives and their sentiments to a csv file
data.to_csv('adjectives_and_sentiments.csv', index=False)
# The saved file has been further edited manually