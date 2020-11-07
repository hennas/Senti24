import logging
import pandas as pd
from matplotlib.figure import Figure


class SentiTransitionPlot:
    def __init__(self):
        self.logger = logging.getLogger('senti-transition-plot')

    def draw_for_gui(self, data: pd.DataFrame) -> Figure:
        """
        Draws a plot of sentiment transitions for the GUI
        :param data: The transition data from data/sentiment-transitions.csv
        :return: The plot
        """
        self.logger.info('Drawing figure for the GUI')
        fig = Figure(dpi=300)
        axis = fig.add_subplot(1, 1, 1)
        values = [data['pos'][0], data['pos'][1], data['pos'][2],
                  data['neg'][0], data['neg'][1], data['neg'][2],
                  data['neu'][0], data['neu'][1], data['neu'][2]]
        labels = ['Pos->Pos', 'Pos->Neg', 'Pos->Neu',
                  'Neg->Pos', 'Neg->Neg', 'Neg-Neu',
                  'Neu->Pos', 'Neu->Neg', 'Neu->Neu']
        axis.bar(labels, values)
        axis.set_title('Sentiment transitions')
        axis.set_xticks(range(len(labels)))
        axis.set_xticklabels(labels, rotation=0, fontsize=7)
        axis.set_ylabel('Number of transitions', fontsize=18)
        axis.set_xlabel('Transition type')

        return fig
