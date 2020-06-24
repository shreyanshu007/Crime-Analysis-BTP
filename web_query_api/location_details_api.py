import flask
from flask import request, jsonify, render_template
import pymysql
import sys
sys.path.append('/home/2016CSB1059/BTP')
from part2 import unknownLocationCrimeInfo

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/')
def location_main_hone():
	return render_template('index.html')

@app.route('/location_info', methods=['GET'])
def home():
	
	query_params = request.args
	name = query_params.get('name')


	try:
		score = unknownLocationCrimeInfo(name)
		if not score:
			score = 'NOT AVAILABLE'
		else:
			score = round(score, 5)
		return render_template('index.html', location=name, crime_score=score)

	except:
		return render_template('index.html', location=name, crime_score='ERROR OCCURRED')
		

app.run(host='0.0.0.0')
