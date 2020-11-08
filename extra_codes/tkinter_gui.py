import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np

"""
Start for the abandoned TkInter GUI
"""

class GUI:
    def __init__(self):
        self.data = pd.read_csv('senti_avg.csv')

        self.root = tk.Tk()
        self.root.geometry('700x1000')
        self.root.wm_title('Sentiment24')
        self.text1 = tk.Label(self.root, text='Analysis:', font=('Helvetica', 18))
        self.text1.pack(side='top')
        self.analysis_frame = tk.Frame(self.root, width=300, height=300)
        self.analysis_frame.pack(side='top', expand=False)
        self.analysis_frame.grid_columnconfigure(0, weight=1)
        self.text2 = tk.Label(self.root, text='Visualization:', font=('Helvetica', 18))
        self.text2.pack(side='top')
        self.vis_frame = tk.Frame(self.root, width=300, height=300)
        self.vis_frame.pack(side='top', expand=False)
        self.vis_frame.grid_columnconfigure(0, weight=1)
        self.plt_frame = tk.Frame(self.root)


        self.obs = {}
        for year in self.data['year'].unique():
            for month in self.data[self.data['year'] == year]['month'].unique():
                self.obs[f'{year}-{month:02d}'] = avgs = self.data[(self.data['year'] == year) & (self.data['month'] == month)]['avg'].values
        self.fig = Figure(figsize=(2, 1), dpi=100)
        self.a = self.fig.add_subplot(111)
        obs_range = range(len(list(self.obs.keys())))
        self.a.plot(obs_range, list(self.obs.values()), color='blue', linewidth=4)
        labels = list(self.obs.keys())
        for i in range(1, len(labels), 2):
            labels[i] = ''
        self.a.set_title('Average sentiment scores on a monthly basis')
        self.a.set_xticks(range(len(labels)))
        self.a.set_xticklabels(labels, rotation=90, fontsize=7)
        self.a.set_xlabel('Date', fontsize=18)
        self.a.set_ylabel('Average sentiment', fontsize=18)
        #plt.title('Average sentiment scores on a monthly basis', fontsize=30)
        #plt.ylabel('Average sentiment', fontsize=18)
        #plt.xlabel('Date', fontsize=18)
        #self.ax.legend()
        #self.fig.add_subplot(111).plot(obs_range, list(self.obs.values()), color='blue', linewidth=4)
        #self.fig.set_xticks(obs_range, labels, rotation=70)
        """
        self.t = np.arange(0, 3, .01)
        self.fig.add_subplot(111).plot(self.t, 2*np.sin(2*np.pi*self.t))
        """
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # Background color?
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        self.add_btns()

    def add_btns(self):
        self.btn1 = tk.Button(master=self.analysis_frame, text='Calculate Sentiment\nScores')  # ,command=_createDB
        self.btn1.config(height=2, width=20)
        self.btn1.grid(row=0, column=0, sticky='ew', padx=10, pady=3)
        self.btn2 = tk.Button(master=self.analysis_frame, text='Calculate Sentiment\nTransitions')  # ,command=_createDB
        self.btn2.config(height=2, width=20)
        self.btn2.grid(row=0, column=1, sticky='ew', padx=10, pady=3)
        self.btn3 = tk.Button(master=self.analysis_frame, text='Categorize Threads')  # ,command=_createDB
        self.btn3.config(height=2, width=20)
        self.btn3.grid(row=1, column=0, sticky='ew', padx=10, pady=3)
        self.btn4 = tk.Button(master=self.analysis_frame, text='Calculate Category\nTransitions')  # ,command=_createDB
        self.btn4.config(height=2, width=20)
        self.btn4.grid(row=1, column=1, sticky='ew', padx=10, pady=3)
        self.btn5 = tk.Button(master=self.analysis_frame, text='Correlate With Index')  # ,command=_createDB
        self.btn5.config(height=2, width=20)
        self.btn5.grid(row=2, column=0, sticky='ew', padx=10, pady=3)

        self.text2 = tk.Label(self.root, text='Settings:', font=('Helvetica', 18))
        self.text2.place(relx=.83, rely=.005)
        self.setting_btn = tk.Button(master=self.root, text='Settings')  # ,command=_createDB
        self.setting_btn.config(height=2, width=10)
        self.setting_btn.place(relx=.9, rely=.059, anchor='c')

        self.btn6 = tk.Button(master=self.vis_frame, text='Sentiment Evolution')  # ,command=_createDB
        self.btn6.config(height=2, width=20)
        self.btn6.grid(row=0, column=0, sticky='ew', padx=10, pady=3)
        self.btn7 = tk.Button(master=self.vis_frame, text='Sentiment Transition')  # ,command=_createDB
        self.btn7.config(height=2, width=20)
        self.btn7.grid(row=0, column=1, sticky='ew', padx=10, pady=3)
        self.btn8 = tk.Button(master=self.vis_frame, text='Category Frequency')  # ,command=_createDB
        self.btn8.config(height=2, width=20)
        self.btn8.grid(row=1, column=0, sticky='ew', padx=10, pady=3)
        self.btn9 = tk.Button(master=self.vis_frame, text='Category Transitions')  # ,command=_createDB
        self.btn9.config(height=2, width=20)
        self.btn9.grid(row=1, column=1, sticky='ew', padx=10, pady=3)

    def start(self):
        tk.mainloop()


if __name__ == '__main__':
    GUI().start()
