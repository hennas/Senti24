import io
import random
import logging
from os import path
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, request, render_template, redirect, Response
# OUR FILES
from Senti24.senti_score2 import SentiScore
from Senti24.senti_transition import SentiTransition
from Senti24.senti_correlation import SentiCorrelation
from Senti24.senti_plot import SentiPlot
from Senti24.senti_transition_plot import SentiTransitionPlot

app = Flask(__name__, template_folder='templates')
# PATHS
senti_jar_path = ''
senti_data_path = ''
db_path = ''
# DATA
db = None
# What To Do
what_to_do = ''
# LOGGING
logger = logging.getLogger('gui')


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    The main page
    :return: Index.html
    """
    global senti_jar_path, senti_data_path, db_path, db, what_to_do, logger
    if senti_data_path == '' or senti_jar_path == '' or db_path == '':
        logger.info('Prompt user to update the settings')
        return render_template('settings.html', jar=senti_jar_path, data=senti_data_path, db=db_path,
                               display_jar='none', display_data='none', display_db='none')
    else:
        try:
            # This is where we decide what the program should do
            # Currently only effects the plot
            what_to_do = request.form.to_dict()['subject']
        except:
            pass
        logger.info(f'What to do: {what_to_do}')

        # ANALYSIS before render
        if what_to_do == 'correlate':
            what_to_do = ''
            return redirect('/correlation')
        result = determine_analysis(what_to_do)
        return render_template('index.html', display_analysis_msg=result[0], analysis_msg=result[1],
                               display_visualize_msg=result[2], visualize_msg=result[3])

@app.route('/settings', methods=['GET', 'POST'])
def update_settings():
    """
    Page for updating the settings
    :return: The Settings page or redirects to the main page
    """
    global senti_jar_path, senti_data_path, db_path, what_to_do, logger
    global senti_jar_path, senti_data_path, db_path, what_to_do, logger
    if request.method == 'POST':
        logger.info('New settings received, updating...')
        new_settings = request.form
        senti_jar_path = new_settings['jar_path']
        senti_data_path = new_settings['data_path']
        db_path = new_settings['db_path']
        logger.info(f'User set the following: jar-path {senti_jar_path}, data-path: {senti_data_path}, db-path: {db_path}')

        result = load_settings()
        if 'block' in result:
            return render_template('settings.html', jar=senti_jar_path, data=senti_data_path, db=db_path,
                                   display_jar=result[0], display_data=result[1], display_db=result[2])
        else:
            logger.info('Settings updated, redirecting to "/"')
            what_to_do = ''
            return redirect('/')

    if request.method == 'GET':
        logger.info('User is accessing the settings page')
        what_to_do = ''
        return render_template('settings.html', jar=senti_jar_path, data=senti_data_path, db=db_path,
                               display_jar='none', display_data='none', display_db='none')

def determine_analysis(what: str):
    """
    Decide if we should do analysis based on user input.
    :param what: What to do
    :return: What to display to the user
    """
    global senti_jar_path, senti_jar_path, db
    if db is None:
        return ['block', 'Please load the database into memory using the /Settings page', 'none', '']
    # Sentiment calculation
    if what == 'sentiScore':
        # Create the SentiScore object
        senti = SentiScore(senti_jar_path, senti_data_path)
        # Update the database with sentiments, and save result
        db = senti.add_sentiment(db)
        return ['block', 'Sentiment Scores added! You can view the result from the file data/sentiment-scores.csv', 'none', '']
    # Sentiment transition calculation
    elif what == 'sentiTransition':
        # Check memory
        if 'senti_avg' in db:
            logger.info('Sentiment scores found in memory, using those values')
            SentiTransition().calculate_transitions(db['senti_avg'].values)
            return ['block', 'Number of sentiment transitions calculated. You can check the result from data/sentiment-transitions.csv', 'none', '']
        # Check data/
        elif path.exists('data/sentiment-scores.csv'):
            logger.info('Sentiment scores not in memory, using data/sentiment-scores.csv')
            data = pd.read_csv('data/sentiment-scores.csv')
            SentiTransition().calculate_transitions(data['senti_avg'].values)
            data = None
            return ['block', 'Number of sentiment transitions calculated. You can check the result from data/sentiment-transitions.csv', 'none', '']
        # Sentiment scores not found
        else:
            return ['block', 'Please calculate the sentiment scores first', 'none', '']
    return ['none', '', 'none', '']


def load_settings() -> [str]:
    """
    Attempts to load the settings provided by the user. Returns an array that decides if the GUI should display an error message
    :return: What the GUI should display
    """
    global db, senti_jar_path, senti_data_path, db_path, logger
    logger.info('Reading database into memory')
    result = ['none', 'none', 'none']
    if not path.exists(senti_jar_path):
        logger.info('Could not find SentiStrength.jar')
        result[0] = 'block'
    if not path.exists(senti_data_path):
        logger.info('Could not find Finnish data for SentiStrength')
        result[1] = 'block'
    try:
        db = pd.read_csv(db_path, engine='python')
        logger.info(f'Databased loaded, contains {len(db)} lines')
    except FileNotFoundError:
        logger.info('Failed to load database from the given location')
        result[2] = 'block'
    return result

@app.route('/correlation')
def display_correlation():
    """
    This page calculates the correlation between sentiment and different indexes and displays it to the user ina table
    :return: The correlation page with a possible error message
    """
    global db, logger
    logger.info('User accessing /correlation')
    if db is not None and 'senti_avg' in db:
        logger.info('Sentiment scores found in memory, using those values')
        corr = SentiCorrelation(db[['year', 'senti_avg']]).correlation()
        return render_template('correlation.html', correlations=corr, len=len(corr), display='none', msg='')
    elif path.exists('data/sentiment-scores.csv'):
        logger.info('Sentiment scores not in memory, using data/sentiment-scores.csv')
        data = pd.read_csv('data/sentiment-scores.csv')[['year', 'senti_avg']]
        corr = SentiCorrelation(data).correlation()
        return render_template('correlation.html', correlations=corr, len=len(corr), display='none', msg='')
    else:
        return render_template('correlation.html', correlations=[], len=0, display='block',
                               msg='Could not calculate correlation, as no sentiment data was found')

@app.route('/plot.png')
def plot():
    """
    Adds a plot to the GUI
    :return: The plot for the browser
    """
    global logger
    # Create figure based on selected command
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    logger.info('Returning the plot.png')
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    """
    Determines which image the GUI should display and starts drawing that
    :return: The figure
    """
    global what_to_do, db, logger
    fig = None
    if what_to_do == 'visSenti':
        if db is not None and 'senti_avg' in db:
            fig = SentiPlot().draw_to_gui(db[['year', 'month', 'senti_avg']])
        elif path.exists('data/sentiment-scores.csv'):
            data = pd.read_csv('data/sentiment-scores.csv')[['year', 'month', 'senti_avg']]
            fig = SentiPlot().draw_to_gui(data)
    elif what_to_do == 'visSentiTranstition' and path.exists('data/sentiment-transitions.csv'):
        data = pd.read_csv('data/sentiment-transitions.csv')
        fig = SentiTransitionPlot().draw_for_gui(data)
    else:
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.set_title('No Data')
    return fig


if __name__ == '__main__':
    # Stop Flask from writing to the log
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    # Set up logging
    logging.basicConfig(format='%(asctime)s %(module)s: %(message)s', level=logging.INFO,
                        datefmt='%H:%M:%S', filename='logs/gui.log', filemode='w')
    # Run the Flask Application
    app.run(host='0.0.0.0', port=8000)
