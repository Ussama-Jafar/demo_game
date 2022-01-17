import json
from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
from gamification_methods import *
from process_gophish import *

###########################################################

application = Flask(__name__)
application.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(application, resources={
						r"/test": {"origins": '*'},
						r"/get/leaderboard": {"origins": '*'},
						r"/signin": {"origins": '*'},
						r"/signup": {"origins": '*'},
						r"/get/user/progress": {"origins": '*'},
						r"/submit/answer": {"origins": '*'},
						r"/get/level/data": {"origins": '*'},
						r"/get/gamification/port": {"origins": '*'},
						r"/get/organization/code": {"origins": '*'},
						r"/create/gophish/group": {"origins": '*'},
						r"/test/server/": {"origins": '*'},

						######## Docker related ###################
						r"/spin/docker": {"origins": '*'},
						r"/remove/docker": {"origins": '*'},
						});

###########################################################

@application.route("/test")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

###########################################################

@application.route('/get/leaderboard', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def get_leaderboard():
	try:
		return process_get_leaderboard(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (get_leaderboard method): ", str(e))
		abort(503)

###########################################################

@application.route('/signin', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def signin():
	try:
		return process_signin(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (signin method): ", str(e))
		abort(503)

###########################################################

@application.route('/signup', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def signup():
	try:
		return process_signup(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (signup method): ", str(e))
		abort(503)

###########################################################

@application.route('/get/user/progress', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def get_user_progress():
	try:
		return process_get_user_progress(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (get_user_progress method): ", str(e))
		abort(503)

###########################################################

@application.route('/submit/answer', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def submit_answer():
	try:
		return process_submit_answer(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (submit_answer method): ", str(e))
		abort(503)

###########################################################

@application.route('/get/level/data', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def get_level_data():
	try:
		return process_get_level_data(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (get_level_data method): ", str(e))
		abort(503)

###########################################################

@application.route('/spin/docker', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def spin_docker():
	try:
		return process_spin_docker(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (spin_docker method): ", str(e))
		abort(503)

###########################################################

@application.route('/remove/docker', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def remove_docker():
	try:
		return process_remove_docker(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (remove_docker method): ", str(e))
		abort(503)

###########################################################

@application.route('/get/gamification/port', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def get_gamification_port():
	try:
		return process_get_gamification_port(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (get_gamification_port method): ", str(e))
		abort(503)

###########################################################

@application.route('/get/organization/code', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def get_organization_code():
	try:
		return process_get_organization_code(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (get_organization_code method): ", str(e))
		abort(503)

###########################################################

@application.route('/create/gophish/group', methods=['POST'])
@cross_origin(origin='*', headers=["Content- Type", "application/json"])
# @validate_credentials
def create_gophish_group():
	try:
		return process_create_gophish_group(request.json)
	except Exception as e:
		print ("Exception in gamificatio.py (get_organization_code method): ", str(e))
		abort(503)

###########################################################

###########################################################
# test server
@application.route('/test/server/')
def test_server():
	try:
		# method's implementation in helpers.py
		return process_test_server()
	except Exception as e:
		if DEBUG_FLAG: print(str(e))
		abort(503)
############################################################

if __name__ == "__main__":
    application.run(host='0.0.0.0')

###########################################################