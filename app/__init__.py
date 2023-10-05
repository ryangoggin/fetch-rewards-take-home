from flask import Flask

app = Flask(__name__)

receipts = {}

@app.route('/')
def index():
    return '<h1>Fetch Rewards Take Home Assessment</h1>'

def id_generator():
    '''
    returns a random id in xxxxxxxx-xxxx-xxxx-xxxxxxxxxxxx format
    '''
    return

@app.route('/receipts/process', methods=['POST'])
def process_receipts():
    '''
    Takes in a JSON receipt and returns a JSON object with a generated ID
    '''
    return
