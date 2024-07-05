from flask import Flask, jsonify, request
from Tools import Tools
from flask_cors import CORS
from ReadConfig import ReadConfig
import xgboost
from datetime import datetime
import os
import requests


tools = Tools()

app = Flask(__name__, instance_relative_config=True)
CORS(app)
app.config.from_pyfile('config.py', silent=True)


@app.route('/api')
# ____________________1 disaggregation____________________ #
@app.route('/disaggregation', methods=['GET', 'POST'])
def disaggregation():
    try:
        data = tools.disaggregate(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# _______________________2 comfort_________________________ #
@app.route('/comfort', methods=['POST'])
def comfort():
    try:
        data = tools.comfort(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# _______________________3 occupancy_______________________ #
@app.route('/occupancy', methods=['POST'])
def occupancy():
    try:
        data = tools.occupancy(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ________________________4 activity________________________ #
@app.route('/activity', methods=['POST'])
def activity():
    try:
        data = tools.activity(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________5 recommendation_____________________ #
@app.route('/recommendation', methods=['POST'])
def recommendation():
    try:
        data = tools.recommendation(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________6 occupancy_retrain_____________________ #
@app.route('/occupancy_retrain', methods=['POST'])
def occupancy_retrain():
    try:
        data = tools.occupancy_retrain(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________7 occupancy_correction_____________________ #
@app.route('/occupancy_correction', methods=['POST'])
def occupancy_correction():
    try:
        data = tools.occupancy_correction(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________8 activity_retrain_____________________ #
@app.route('/activity_retrain', methods=['POST'])
def activity_retrain():
    try:
        data = tools.activity_retrain(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________9 activity_correction_____________________ #
@app.route('/activity_correction', methods=['POST'])
def activity_correction():
    try:
        data = tools.activity_correction(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________10 vcl_train_____________________ #
@app.route('/vcl_train', methods=['POST'])
def vcl_train():
    try:
        data = tools.vcl_train(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________11 tct_train_____________________ #
@app.route('/tct_train', methods=['POST'])
def tct_train():
    try:
        data = tools.tct_train(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________12 tch_train_____________________ #
@app.route('/tch_train', methods=['POST'])
def tch_train():
    try:
        data = tools.tch_train(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________13 new_client_____________________ #
@app.route('/new_client', methods=['POST'])
def new_client():
    try:
        data = tools.new_client(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________14 create_occupancy_models_____________________ #
@app.route('/create_occupancy_models', methods=['POST'])
def create_occupancy_models():
    try:
        data = tools.create_occupancy_models(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________15 create_activity_models_____________________ #
@app.route('/create_activity_models', methods=['POST'])
def create_activity_models():
    try:
        data = tools.create_activity_models(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________16 delete_client_____________________ #
@app.route('/delete_client', methods=['POST'])
def delete_client():
    try:
        data = tools.delete_client(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400


# ______________________17 savings_____________________ #
@app.route('/savings', methods=['POST'])
def savings():
    try:
        data = tools.savings(request.json)
        return jsonify(data), 200
    except Exception as e:
        data = {'error': e}
        return jsonify(data), 400

def trial(url):
    s = requests.Session() 
    r = s.get(url)

    return r.json




if __name__ == '__main__':

    # run application
    conf = ReadConfig()
    app.run(host=conf.host, port=conf.api_port, debug=conf.debug, threaded=conf.threaded)#use_reloader=False


