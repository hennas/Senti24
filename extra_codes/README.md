## Extra codes
Here you can find codes that were used to obtain the data that the analysis uses.

**NOTE**: Some of these will probably not work directly without slight modifications, as they have been taken out of the environment where they were previously ran.

* **combine_data.py**: Combines .csv files
* **extract_topic**: Extracts thread topics from the Suomi24 dataset
* **finnpos_label.py**: Extracts adjectives, verbs, and nouns from the threads. Uses FinnPos and SentiStrength
* **organize_finnpos_files.py**: Parses the output of finnpos_label.py, deletes everything except positive and negative adjectives
* **preprocessing**: Pre-processing done to the threads
* **senti_score.py**: Old version of sentiment score calculation
* **senti_transition_plot.py**: Previously used to draw a transition plot in the GUi
* **tkinter_gui.py**: An abandoned attempt to make the GUI with TkInter
* **unique_words.py**: Extracts all unique words from the threads. Uses some memory magic. Was not used though...
* **vrt_extract**: Old way of extracting threads
* **vrt_extract2.py**: Current way to extract threads from the Suomi24 dataset
* **yearly_evolution_of_categories.py**: Used to plot the yearly evolution of the number of threads inside categories; Not added to GUI due to lack of time
* **zip_extract.sh**: Script that automatically extracts .vrt files from the zip archive, uses vrt_extract2.py on them, and deletes the .vrt files 
 
  
These codes are more complicated, some take a long time to run (~3 hours for adjective extracting), **so we do not recommend running these**. 
In addition, some results have been manually edited, such as the adjective list. 
Mainly these codes produce the base data used for further analysis, and that data is provided to the user.
Note also that we do not provide the data needed to run some of the codes because of the enormous size of those files.
