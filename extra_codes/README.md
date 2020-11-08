## Extra codes
Here you can find codes that were used to obtain the data the analysis uses

**NOTE**: Some of these will probably not work just without slight modifications, they have been taken out of the environment where they were previously ran.

* **combine_data.py**: Combines csvs
* **extract_topic**: Extract thread topics from the Suomi24 dataset
* **finnpos_label.py**: Extracts adjectives, verbs, and nouns from the threads. Uses FinnPos and SentiStrength
* **organize_finnpos_files.py**: Parses the output of finnpos_label.py, deletes everything except adjectives
* **preprocessing**: Pre-processing done to the threads
* **senti_score.py**: Old version of sentiment score calculation
* **senti_transition_plot.py**: Previously used to draw a transition plot in the GUi
* **tkinter_gui.py**: An abandoned attempt to make the GUI with TkInter
* **unique_words.py**: Extracts all unique words from the threads. Uses some memory magic. Was not used though...
* **vrt_extract**: Old way of extracting threads
* **vrt_extract2.py**: Current way to extract threads from the Suomi24 dataset
* **zip_extract.sh**: Script that automatically extracts .vrt files from the zip archive, uses vrt_extract2.py on them, and deletes the .vrt files 
 
  
These codes are more complicated, some take a long time to run (~3 hours for adjective extracting), so we do not recommend running these. 
In addition, some results have been manually edited, such as the adjective list. 
Mainly these codes produce the base data used for further analysis, and that data is provided to the user.
