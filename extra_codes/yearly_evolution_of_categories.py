import pandas as pd
import matplotlib.pyplot as plt
from random import random

def yearly_category_evolution(data, cat_col, plot_only_cats = []):
    """
    Calculates and plots the number of threads inside each unique category, 
    as well as the overall number of threads on yearly basis.
    If only certain categories are desired to plot, they must be given inside a list
    to the parameter plot_only_cats
    """
    yearly_cats = data.groupby(['year',cat_col]).count().thread_id.reset_index()
    yearly_counts = data.groupby(['year']).count().thread_id.reset_index()
    unique_cats = data[cat_col].unique()
    
    if len(plot_only_cats) == 0:
        fig = plt.figure(figsize=(10, 30))
        ax = fig.subplots(len(unique_cats)+1)
    
        ax[0].plot(yearly_counts.year, yearly_counts.thread_id, linewidth=2, label='Total threads', c='blue')
        ax[0].legend(loc="best")
        ax[0].set_ylabel('N of threads', fontsize=15)
        ax[0].set_xlabel('Year', fontsize=15)
    
        for i, uc in enumerate(unique_cats):
            cat_data = yearly_cats[yearly_cats[cat_col] == uc]
            r = random()
            g = random()
            b = random()
            ax[i+1].plot(cat_data.year, cat_data.thread_id, linewidth=2, label=uc, c=(r,g,b))
            ax[i+1].legend(loc="best")
            ax[i+1].set_ylabel('N of threads', fontsize=15)
            ax[i+1].set_xlabel('Year', fontsize=15)
    else:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.subplots(len(plot_only_cats))
        
        for i, uc in enumerate(plot_only_cats):
            cat_data = yearly_cats[yearly_cats[cat_col] == uc]
            r = random()
            g = random()
            b = random()
            ax[i].plot(cat_data.year, cat_data.thread_id, linewidth=2, label=uc, c=(r,g,b))
            ax[i].legend(loc="best")
            ax[i].set_ylabel('N of threads', fontsize=15)
            ax[i].set_xlabel('Year', fontsize=15)
            
    fig.suptitle('Yearly evolution of number of threads inside categories', fontsize=20)
    fig.tight_layout(rect=[0,0.03,1,0.95])
    
    return fig
    
if __name__ == '__main__':
    data = pd.read_csv('data/database.csv')
    fig = yearly_category_evolution(data, 'simple_heuristic_cat', ['Negative Reaction','Negative Narration'])
    fig.savefig('negative_cats.png', format="png")
