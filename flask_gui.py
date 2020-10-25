import io
import random
import logging
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, request, render_template, redirect, Response

app = Flask(__name__)
# PATHS
senti_jar_path = '/home/zabrakk/nlp/data/SentiStr/SentiStrength.jar'
senti_data_path = '/home/zabrakk/nlp/data/SentiStr/SentiDataFI'
db_path = '/home/zabrakk/nlp/data/data_combined_preprocessed.csv'
# DATA
db = None
# What To Do
what_to_do = 'lineplot'
# LOGGING
logger = logging.getLogger('gui')

@app.route('/', methods=['GET', 'POST'])
def index():
    global senti_jar_path, senti_data_path, db_path, what_to_do, logger
    if senti_data_path == '' or senti_jar_path == '' or db_path == '':
        logger.info('Prompt user to update the settings')
        return render_template('settings.html', jar=senti_jar_path, data=senti_data_path, db=db_path)
    else:
        try:
            # This is where we decide what the program should do
            # Currently only effects the plot
            what_to_do = request.form.to_dict()['subject']
        except:
            pass

        logger.info(f'What to do {what_to_do}')
        return render_template('index.html')

@app.route('/settings', methods=['GET', 'POST'])
def update_settings():
    global senti_jar_path, senti_data_path, db_path, logger
    if request.method == 'POST':
        logger.info('New settigns received, updating...')
        new_settings = request.form
        senti_jar_path = new_settings['jar_path']
        senti_data_path = new_settings['data_path']
        db_path = new_settings['db_path']
        logger.info(f'User set the following: jar-path {senti_jar_path}, data-path: {senti_data_path}, db-path: {db_path}')
        load_db()
        logger.info('Settings updated, redirecting to "/"')
        return redirect('/')
    if request.method == 'GET':
        logger.info('User is accessing the settings page')
        return render_template('settings.html', jar=senti_jar_path, data=senti_data_path, db=db_path)

def load_db(): # TODO: ERROR HANDLING!
    global db, db_path, logger
    logger.info('Reading database into memory')
    db = pd.read_csv(db_path, engine='python')
    logger.info(f'Dataabased loaded, contains {len(db)} lines')

@app.route('/plot.png')
def plot():
    global logger
    # Create figure based on selected command
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    logger.info('Returning the plot.png')
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    global what_to_do, logger
    logger.info('Creating a random figure')

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    if what_to_do == 'lineplot':
        axis.plot(xs, ys)
    else:
        axis.bar(xs, ys)
    return fig


# Stop Flask from writing to the log
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
#Set up logging
logging.basicConfig(format='%(asctime)s %(module)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S', filename='logs/gui.log', filemode='w')
#Run the Flask Application
app.run(host='0.0.0.0', port=8000)
