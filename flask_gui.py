import io
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
from Senti24.categorization import Categorizer
from Senti24.category_transitions import CategoryTransitions
from Senti24.zipfs_law import ZipfsLaw
from Senti24.kmeans_categorization import KmeansCategorization

app = Flask(__name__, template_folder='templates')
# PATHS
senti_jar_path = ''
senti_data_path = ''
# DATA
db = None
kmeans_cat = None
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
    global senti_jar_path, senti_data_path, db, what_to_do, logger
    if senti_data_path == '' or senti_jar_path == '':
        logger.info('Prompt user to update the settings')
        return render_template('settings.html', jar=senti_jar_path, data=senti_data_path,
                               display_jar='none', display_data='none')
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
        # Display sentiment and category transitions
        elif what_to_do == 'visSentiTransitions' or what_to_do == 'visCategoryTransition' or what_to_do == 'visKmeansCategoryTransition':
            return redirect('/transitions')
        result = determine_analysis(what_to_do)
        return render_template('index.html', display_analysis_msg=result[0], analysis_msg=result[1],
                               display_visualize_msg=result[2], visualize_msg=result[3])

@app.route('/settings', methods=['GET', 'POST'])
def update_settings():
    """
    Page for updating the settings
    :return: The Settings page or redirects to the main page
    """
    global senti_jar_path, senti_data_path, what_to_do, logger
    if request.method == 'POST':
        logger.info('New settings received, updating...')
        new_settings = request.form
        senti_jar_path = new_settings['jar_path']
        senti_data_path = new_settings['data_path']
        logger.info(f'User set the following: jar-path {senti_jar_path}, data-path: {senti_data_path}')

        result = load_settings()
        if 'block' in result:
            return render_template('settings.html', jar=senti_jar_path, data=senti_data_path,
                                   display_jar=result[0], display_data=result[1])
        else:
            logger.info('Settings updated, redirecting to "/"')
            what_to_do = ''
            return redirect('/')

    if request.method == 'GET':
        logger.info('User is accessing the settings page')
        what_to_do = ''
        return render_template('settings.html', jar=senti_jar_path, data=senti_data_path,
                               display_jar='none', display_data='none')

def determine_analysis(what: str):
    """
    Decide if we should do analysis based on user input.
    :param what: What to do
    :return: What to display to the user
    """
    global senti_jar_path, senti_jar_path, db, kmeans_cat, logger
    # Sentiment calculation
    if what == 'sentiScore':
        if not path.exists('data/data_combined_preprocessed.csv'):
            return ['block', 'Could not find the pre-processed data data/data_combined_preprocessed.csv', 'none', '']
        # Create the SentiScore object
        senti = SentiScore(senti_jar_path, senti_data_path)
        # Update the database with sentiments, and save result
        db = senti.add_sentiment(pd.read_csv('data/data_combined_preprocessed.csv'))
        return ['block', 'Sentiment Scores added! You can view the result in the file data/database.csv', 'none', '']
    # Sentiment transition calculation
    elif what == 'sentiTransition':
        # Check memory
        if db is not None and 'senti_avg' in db:
            logger.info('Sentiment scores found in memory, using those values')
            SentiTransition().calculate_transitions(db['senti_avg'].values)
            return ['block', 'Number of sentiment transitions calculated. You can check the result from data/sentiment-transitions.csv', 'none', '']
        # Check data/
        elif db is None and path.exists('data/database.csv'):
            logger.info('Sentiment scores not in memory, loading data/database.csv')
            db = pd.read_csv('data/database.csv')
            if 'senti_avg' in db:
                SentiTransition().calculate_transitions(db['senti_avg'].values)
                data = None
                return ['block', 'Number of sentiment transitions calculated. You can check the result from data/sentiment-transitions.csv', 'none', '']
            else:
                return ['block', 'Please calculate sentiment scores first', 'none', '']
        # Sentiment scores not found
        else:
            return ['block', 'Please calculate the sentiment scores first', 'none', '']
    # Simple Thread categorization
    elif what == 'categorize':
        # Check memory
        if db is not None and 'senti_avg' in db:
            logger.info('Sentiment scores found in memory, using those values')
            # Create the categorized object and start categorization
            Categorizer(db).categorize_main()
            return ['block', 'Threads Categorized! You can view the result in the file data/database.csv', 'none', '']
        # Check data/
        elif db is None and path.exists('data/database.csv'):
            logger.info('Sentiment scores not in memory, loading data/database.csv')
            db = pd.read_csv('data/database.csv')
            if 'senti_avg' in db:
                Categorizer(db).categorize_main()
                data = None  # Remove this from memory
                return ['block', 'Threads Categorized! You can view the result in the file data/database.csv', 'none', '']
            else:
                return ['block', 'Please calculate sentiment scores first', 'none', '']
        # Sentiment scores not found
        else:
            return ['block', 'Please calculate the sentiment scores first', 'none', '']
    # Category Transitions
    elif what == 'categoryTransition':
        if db is not None and 'simple_heuristic_cat' in db:
            CategoryTransitions(db.simple_heuristic_cat, 'data/simple_transitions.csv').get_transitions()
            return ['block',
                    'Category Transitions calculated! You can view the results from data/category_transitions.csv',
                    'none', '']
        elif db is None and path.exists('data/database.csv'):
            logger.info('Loading data/database.csv')
            db = pd.read_csv('data/database.csv')
            if 'simple_heuristic_cat' in db:
                CategoryTransitions(db.simple_heuristic_cat, 'data/simple_transitions.csv').get_transitions()
                return ['block',
                        'Category Transitions calculated! You can view the results from data/category_transitions.csv',
                        'none', '']
            else:
                return ['block', 'Please complete thread categorization first', 'none', '']
        else:
            return ['block', 'Please complete thread categorization first', 'none', '']
    # K-Means Thread categorization
    elif what == 'kmeans-categorize':
        # Check memory
        if db is not None and 'simple_heuristic_cat' in db:
            km_obj = KmeansCategorization(db)
            km_obj.kmeans_main()
            kmeans_cat = km_obj.all_data.kmeans_cat
            kmeans_cat.to_csv('data/kmeans_categorization.csv', index=False)
            km_obj = None  # Conserve memory
            return ['block',
                    "K-Means categorization done! Get more results with category transitions or K-means Zipf's Law",
                    'none', '']
        elif db is None and path.exists('data/database.csv'):
            db = pd.read_csv('data/database.csv')
            if 'simple_heuristic_cat' in db:
                km_obj = KmeansCategorization(db)
                km_obj.kmeans_main()
                kmeans_cat = km_obj.all_data.kmeans_cat
                kmeans_cat.to_csv('data/kmeans_categorization.csv', index=False)
                km_obj = None  # Conserve memory
                return ['block',
                        "K-Means categorization done! Get more results with category transitions or K-means Zipf's Law",
                        'none', '']
            else:
                logger.info('Simple heuristic has not been ran yet, k-means requires the result from it')
                return ['block', 'Run simple categorization first!', 'none', '']
        else:
            logger.info('Simple heuristic has not been ran yet, k-means requires the result from it')
            return ['block', 'Run simple categorization first!', 'none', '']
    # K-Means Category transitions
    elif what_to_do == 'kmeans-categoryTransition':
        if kmeans_cat is None and not path.exists('data/kmeans_categorization.csv'):
            return ['block', 'Complete K-Means categorization first!', 'none', '']
        if kmeans_cat is None:
            logger.info('Reading data/kmeans_categorization.csv')
            kmeans_cat = pd.read_csv('data/kmeans_categorization.csv').kmeans_cat
        CategoryTransitions(kmeans_cat, 'data/kmeans_transitions.csv').get_transitions()
        return ['block', 'Category Transitions calculated for K-Means! See results by visualizing Transitions', 'none', '']

    # No match. This should only happen when the user first loads /
    return ['none', '', 'none', '']


def load_settings() -> [str]:
    """
    Attempts to load the settings provided by the user. Returns an array that decides if the GUI should display an error message
    :return: What the GUI should display
    """
    global db, senti_jar_path, senti_data_path, logger
    result = ['none', 'none', 'none']
    if not path.exists(senti_jar_path) or not senti_jar_path.endswith('.jar'):
        logger.info('Could not find SentiStrength.jar')
        result[0] = 'block'
    if not path.exists(senti_data_path):
        logger.info('Could not find Finnish data for SentiStrength')
        result[1] = 'block'
    return result

@app.route('/transitions')
def display_transitions():
    """
    This page displays the sentiment and category transitions inside a dynamically created table
    :return: The transitions page
    """
    global what_to_do, logger
    logger.info('User accessing /transitions')
    if what_to_do == 'visSentiTransitions':
        what_to_do = ''
        if not path.exists('data/sentiment-transitions.csv'):
            logger.info('No sentiment transitions data found')
            return render_template('transitions.html', display='block', msg='No sentiment transition data found', data=[], len_rows=0, len_cols=0)
        data = pd.read_csv('data/sentiment-transitions.csv')
        data = data.values.tolist()
        data[:0] = [['FROM/TO', 'pos', 'neg', 'neu']]
        return render_template('transitions.html', display='none', msg='', data=data, len_rows=len(data), len_cols=len(data[0]))
    elif what_to_do == 'visCategoryTransition':
        what_to_do = ''
        if not path.exists('data/simple_transitions.csv'):
            logger.info('No simple category transitions data found')
            return render_template('transitions.html', display='block', msg='No category transition data found', data=[], len_rows=0, len_cols=0)
        data = pd.read_csv('data/simple_transitions.csv')
        cols = data.columns.values.tolist()
        data = data.values.tolist()
        cols[0] = 'FROM/TO'
        data[:0] = [cols]
        return render_template('transitions.html', display='none', msg='', data=data, len_rows=len(data),
                               len_cols=len(data[0]))
    elif what_to_do == 'visKmeansCategoryTransition':
        what_to_do = ''
        if not path.exists('data/kmeans_transitions.csv'):
            logger.info('No K-means category transition data found')
            return render_template('transitions.html', display='block', msg='No category transition data found', data=[], len_rows=0, len_cols=0)
        data = pd.read_csv('data/kmeans_transitions.csv')
        cols = data.columns.values.tolist()
        data = data.values.tolist()
        cols[0] = 'FROM/TO'
        data[:0] = [cols]
        return render_template('transitions.html', display='none', msg='', data=data, len_rows=len(data),
                               len_cols=len(data[0]))
    else:
        what_to_do = ''
        return render_template('transitions.html', display='block', msg='Something went wrong', data=[], len_rows=0, len_cols=0)

@app.route('/correlation')
def display_correlation():
    """
    This page calculates the correlation between sentiment and different indexes and displays it to the user ina table
    :return: The correlation page with a possible error message
    """
    global db, logger
    logger.info('User accessing /correlation')
    if db is not None and 'senti_avg' in db and len(db.year.unique().tolist()) >= 9:
        logger.info('Sentiment scores found in memory, using those values')
        corr = SentiCorrelation(db[['year', 'senti_avg']]).correlation()
        return render_template('correlation.html', correlations=corr, len=len(corr), display='none', msg='')
    elif db is None and path.exists('data/database.csv'):
        logger.info('Sentiment scores not in memory, loading data/database.csv')
        db = pd.read_csv('data/database.csv')
        if 'senti_avg' in db and len(db.year.unique().tolist()) >= 9:
            corr = SentiCorrelation(db[['year', 'senti_avg']]).correlation()
            return render_template('correlation.html', correlations=corr, len=len(corr), display='none', msg='')
        else:
            return render_template('correlation.html', correlations=[], len=0, display='block',
                                   msg='Could not calculate correlation, as no sentiment data was found for all required years')
    else:
        return render_template('correlation.html', correlations=[], len=0, display='block',
                               msg='Could not calculate correlation, as no sentiment data was found for all required years')

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
    global what_to_do, db, kmeans_cat, logger
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title('No Data')
    # Sentiment Evolution
    if what_to_do == 'visSenti':
        if db is not None and 'senti_avg' in db:
            fig = SentiPlot().draw_to_gui(db[['year', 'month', 'senti_avg']])
        elif db is None and path.exists('data/database.csv'):
            db = pd.read_csv('data/database.csv')
            if 'senti_avg' in db:
                fig = SentiPlot().draw_to_gui(db[['year', 'month', 'senti_avg']])
            else:
                axis.set_title('No Data, please run the corresponding analysis')
        else:
            axis.set_title('No Data, please run the corresponding analysis')
    # Zipf's Law for Simple heuristic
    elif what_to_do == 'zipf':
        if db is not None and 'simple_heuristic_cat' in db:
            fig = ZipfsLaw(db.simple_heuristic_cat).fit_zipfs_law()
        elif db is None and path.exists('data/database.csv'):
            logger.info('Loading data/database.csv')
            db = pd.read_csv('data/database.csv')
            if 'simple_heuristic_cat' in db:
                fig = ZipfsLaw(db.simple_heuristic_cat).fit_zipfs_law()
            else:
                axis.set_title('No Data, please run the corresponding analysis')
        else:
            axis.set_title('No Data, please run the corresponding analysis')

    # Zipf's Law for K-means
    elif what_to_do =='kmeans-zipf':
        if kmeans_cat is not None:
            fig = ZipfsLaw(kmeans_cat).fit_zipfs_law()
        elif path.exists('data/kmeans_categorization.csv'):
            logger.info('Reading data/kmeans_categorization.csv')
            kmeans_cat = pd.read_csv('data/kmeans_categorization.csv')
            fig = ZipfsLaw(kmeans_cat.kmeans_cat).fit_zipfs_law()
        else:
            axis.set_title('No Data, please run the corresponding analysis')
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
