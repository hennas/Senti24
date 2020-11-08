# Senti24

Database: (ADD LINK HERE)

## Setup
The full environment required for the GUI to work, can be downloaded from here: (ADD DROPBOX LINK)

You can install the required Python libraries with:
```bash
$ pip3 install -r requirements.txt
```
Getting word_tokenize() from the NTLK library working, might require some extra steps.

## Running the GUI
After completing the setup, you can run the GUI with the following command:
```bash
$ python3 flask_gui.py
```
Then you can access the web GUI by going to **localhost:8000** with your browser

## Running codes separately
If you want to run parts of the analysis separately, you must take into account that each of them require different files to be present in the **data/** directory.

You should go into this projects repository, and run them, e.g. like this:
```bash
$ python3 Senti24/senti_score2.py
```
That way, the file can access **data/**