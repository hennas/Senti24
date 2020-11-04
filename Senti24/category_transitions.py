import pandas as pd

def calculate_category_transitions(categories):
    """
    Calculates all category transitions. Assumes that the given column of categories is 
    in the right order, i.e., the threads are organized in an ascending order by datetime.
    Return dictionary where keys are transition pairs, e.g. (Question, Announcement), and 
    values are the number of occurences for each transition pair
    """
    unique_cats = categories.unique()
    transition_counts = {}
    
    for c1 in unique_cats:
        for c2 in unique_cats:
            transition_counts[(c1,c2)] = 0
            
    for i in range(len(categories)-1):
        transition_counts[(categories[i], categories[i+1])] += 1
    
    return transition_counts

def cross_table(unique_cats, transitions):
    """
    Forms a cross table for transition counts, and saves it as a csv file
    """
    table = pd.DataFrame(columns=unique_cats, index=unique_cats)
    for k,v in transitions.items():
        table.loc[k[0],k[1]] = v
    table.to_csv('category_transitions.csv')
    
if __name__ == '__main__':
    data = pd.read_csv('sentiment-data+features.csv')
    t_counts = calculate_category_transitions(data.simple_heuristic_cat)
    cross_table(data.simple_heuristic_cat.unique(), t_counts)