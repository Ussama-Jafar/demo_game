import json
from flask import abort
from mongo_connection import db_users, db_defaults, db_docker, db_config
from constants_gamification import *
from process_user import create_user, verify_user_credentials
from process_score import *
from constants_defaults import LEVEL_JSON_PATH, BADGES_JSON_PATH, NEW_BADGES_JSON_PATH
from spin_docker import spin_docker, remove_docker
from process_docker import *

###########################################################

def process_get_leaderboard(body):
	try:
		collection = db_users['users_data']
		data = collection.find({}, {
				'_id': 0, 
				'organization_code': 0,
				'password': 0,
				'user_count': 0
			}).sort([('score', -1)])
		
		total_levels = db_defaults['level_count'].find_one({}, {'_id': 0})['count']
		data_to_send = {}
		data_to_send['total_levels'] = total_levels

		if data:
			leaders = list(data)
		else:
			leaders = []

		data_to_send['leaders'] = leaders
		return json.dumps({"message": data_to_send}), 200, {"ContentType": "application/json"}
	except Exception as e:
		print("Exception in process_get_leaderboard", str(e))
		abort(400)

###########################################################

def process_signin(body):
	try:
		username = body.get('username')
		password = body.get('password')
		
		message = verify_user_credentials(username, password)
		return json.dumps({"message": message}), 200, {"ContentType": "application/json"}

	except Exception as e:
		print("Exception in process_signin", str(e))
		abort(400)

###########################################################

def process_signup(body):
	try:
		message = create_user(body)
		return json.dumps({"message": message}), 200, {"ContentType": "application/json"}
	except Exception as e:
		print("Exception in process_signup", str(e))
		abort(400)

###########################################################

def process_get_user_progress(body):
	try:
		collection = db_users['users_data']
		username = body.get('username')
		
		with open(LEVEL_JSON_PATH, 'r') as data_file:
			default_data = json.load(data_file)

		with open(BADGES_JSON_PATH, 'r') as data_file:
			badges_data = json.load(data_file)

		with open(NEW_BADGES_JSON_PATH, 'r') as data_file:
			new_badges = json.load(data_file)

		badges_data.extend(new_badges)

		progress = db_users['users_data'].find_one({
				'username': username
			}, {
				'_id': 0,
				'current_level': 1,
				'badges': 1,
				'user_count': 1,
				'current_badge': 1,
				'score': 1
			})
		level = progress['current_level']
		badge = progress['current_badge']
		name = "".join(['user', str(progress['user_count'])])
		print(name)
		col_name = ".".join(['users_data', name])
		cur = db_users[col_name].find({}, {'_id':0, 'attempt': 0, 'locked': 0})
		# print(list(cur))
		levels_record = []
		for l in cur:
			l['point_percentage'] = round(l['user_points'] / l['total_points'] * 100, 2)
			l['score_percentage'] = round((l['score']/(l['total_points']*10))*100, 2)
			l['unlocked'] = True
			levels_record.append(l)
		
		# print(levels_record)
		badges_record = progress['badges']
		
		data_to_send = {}
		data_to_send['current_level'] = progress['current_level']
		data_to_send['levels'] = levels_record
		data_to_send['current_badge'] = badges_data[int(badge)-1]['name']
		data_to_send['earned_badges'] = int(badge)
		data_to_send['next_badge'] = badges_data[int(badge)]['name']
		data_to_send['next_badge_num'] = int(badge) + 1
		data_to_send['current_score'] = progress['score']
		data_to_send['next_badge_score'] = progress['current_level'] * 30
		data_to_send['total_badges_percentage'] = round(int(badge)/len(badges_data)*100, 2)

		
		### dummy data
		dummy = [
			{'name': 'Vendor security', 'y': 45.23},
			{'name': 'Ransomware', 'y': 82.32},
			{'name': 'Phishing', 'y': 67.22},
			{'name': 'Bussiness protection', 'y': 72.22},
			{'name': 'Data breach', 'y': 54.22},
		]
		# data_to_send['skills'].append()
		data_to_send['skills'] = dummy
		
		for i in range(int(level), len(default_data)):
			data_to_send['levels'].append({
					'id': default_data[i]['level'],
					'unlocked': False
				})
		data_to_send['total_badges'] = []
		all_badges = progress['badges']
		print(all_badges)
		for i in range(0, len(all_badges)):
			print(all_badges[i])
			print(all_badges[i]['id'])
			data_to_send['total_badges'].append({
					'earned_badges': int(all_badges[i]['id'])
				})

		data = db_users['users_data'].find({}, {
				'_id': 0, 
				'organization_code': 0,
				'password': 0,
				'user_count': 0
			}).sort([('score', -1)])
		ranks = list(data)
		# print(ra.nks)
		for i in range(0, len(ranks)):
			if username == ranks[i]['username']:
				data_to_send['rank'] = i+1
				break

		return json.dumps(data_to_send), 200, {"ContentType": "application/json"}
	except Exception as e:
		print("Exception in process_get_user_progress", str(e))
		abort(400)

###########################################################

def process_submit_answer(body):
	try:
		# message = create_user(body)
		
		level_id = body.get("level_id")
		
		user_answers = body.get("user_answers")
		
		users_data = db_users['users_data'].find_one({
				'username': body.get('username')
			}, {
				'_id': 0,
				'user_count': 1
			})
		
		name = "".join(["user", str(users_data['user_count'])])
		
		prev_result = db_users['users_data'][name].find_one({
				'id': level_id
			}, {'_id': 0, 'score': 1, 'user_points': 1, 'attempt': 1})
		
		
		attempt = int(prev_result['attempt'])
		attempt += 1
		
		result = count_score(level_id, user_answers, attempt)
		
		score = result['score']
		points = result['points']

		prev_score = prev_result['score']
		prev_points = prev_result['user_points']
		
		res = update_score(body.get('username'), attempt, prev_score, prev_points, score, points, name, level_id)
		res['badge_unlocked'] = []
		res['score'] = score
		res['points'] = points
		if res['next_level_unlocked']:
			with open(BADGES_JSON_PATH, 'r') as data_file:
				badges = json.load(data_file)

			level_id += 1
			for b in badges:
				if b['id'] == level_id:
					db_users['users_data'].update({
							'username': body.get('username')
						}, {'$addToSet': {
								'badges': {
									'id': b['id'],
									'name': b['name'],
									'locked': False
								},
						},'$set': {'current_badge': level_id}
						})
					res['badge_unlocked'].append(b['name'])
		
		return json.dumps(res), 200, {"ContentType": "application/json"}
	except Exception as e:
		print("Exception in process_submit_answer", str(e))
		abort(400)

###########################################################

def process_get_level_data(body):
	try:
		level = body.get('level_id')
		print(level)
		with open(LEVEL_JSON_PATH, 'r') as data_file:
			default_data = json.load(data_file)

		data_to_send = {}
		for d in default_data:
			if d['level'] == level:
				data_to_send = d
				print(data_to_send)
				break

		if data_to_send == {}:
			return json.dumps({"message": "NOT FOUND"}), 400, {"ContentType": "application/json"}
		else:
			return json.dumps(data_to_send), 200, {"ContentType": "application/json"}

	except Exception as e:
		print("Exception in process_get_level_data", str(e))
		abort(400)

###########################################################

def process_spin_docker(body):
	try:
		username = body.get('username')
		key = body.get('key')
		organization = body.get('organization')
		print(username, ":", key, " - ", organization)
		res = spin_docker(username, key, organization)
		return json.dumps(res), 200, {"ContentType": "application/json"}

	except Exception as e:
		print("Exception in process_spin_docker", str(e))
		abort(400)

###########################################################

def process_remove_docker(body):
	try:
		username = body.get('username')
		key = body.get('key')
		res = remove_docker(username, key)
		return json.dumps(res), 200, {"ContentType": "application/json"}

	except Exception as e:
		print("Exception in process_remove_docker", str(e))
		abort(400)

###########################################################

####################################################################################

def process_test_server():
	payload = {}
	payload["status"] = "good"
	database = {}
	database_error = True
	
	# check config db
	try:
		res = db_config['test_server'].find_one()
		payload["status"] = res["status"]
	except Exception as e:
		database_error = False
		database["CONFIG"] = str(e)
	# if there was any error in databases
	if database_error == False:
		payload["status"] = "bad"
		payload["errors"] = {}
		payload["errors"]["database"] = database

	return json.dumps(payload), 200, {"ContentType":"application/json"}

####################################################################################