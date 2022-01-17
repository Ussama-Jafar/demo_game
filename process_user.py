from flask import abort
import json
from mongo_connection import db_users, db_defaults
from constants_defaults import LEVEL_JSON_PATH, BADGES_JSON_PATH, NEW_BADGES_JSON_PATH

###########################################################

def verifiy_email(email):
	try:
		collection = db_users['users_data']
		data = collection.find({'email': email}).count()
		print("DATA ", data)
		if data > 0:
			return False
		else:
			return True

	except Exception as e:
		print("Exception in verifiy_email", str(e))
		abort(401)

###########################################################

def verify_username(username):
	try:
		collection = db_users['users_data']
		data = collection.find({'username': username}).count()
		if data > 0:
			return False
		else:
			return True

	except Exception as e:
		print("Exception in verify_username", str(e))
		abort(401)	

###########################################################

def verify_organization_code(code):
	try:
		return True
	except Exception as e:
		abort(401)	

###########################################################

def calculate_rank(score):
	try:
		rank = 1
		return rank
	except Exception as e:
		abort(400)

###########################################################

def create_user(data):
	try:
		email = data.get('email')
		username = data.get('username')
		code = data.get('organization_code')
		# check if email already exist
		if verifiy_email(email):
			# verify if username already exist 
			if verify_username(username):
				# check if organization code is valid
				if verify_organization_code(code):
					## Creating a new user
					collection = db_users['users_data']
					count = int(db_defaults['user_counter'].find_one()['count'])
					count += 1
					data['user_count'] = count
					data['score'] = 0
					data['current_level'] = 1

					with open(BADGES_JSON_PATH, 'r') as data_file:
						default_data = json.load(data_file)
					data['badges'] = []
					data['badges'].append({
							'id': default_data[0]['id'],
							'name': default_data[0]['name'],
							'locked': False
						})
					with open(NEW_BADGES_JSON_PATH, 'r') as data_file:
						badge_data = json.load(data_file)
					for badge in badge_data:
						data['badges'].append({
								'id': int(badge['id']),
								'name': badge['name'],
								'locked': badge['locked']
							})
					data['current_badge'] = 1
					collection.insert(data)

					## Set default for user
					with open(LEVEL_JSON_PATH, 'r') as data_file:
						default_data = json.load(data_file)
						# print(default_data)

					name = "".join(["user", str(count)])
					level = 1
					for d in default_data:
						if d['level'] == level:
							level_info = {}
							level_info['id'] = d['level']
							level_info['attempt'] = 0
							level_info['score'] = 0
							level_info['locked'] = False
							level_info['total_points'] = d['total_points']
							level_info['user_points'] = 0
							defaults_collection = db_users['users_data'][name]
							defaults_collection.insert(level_info)

					db_defaults['user_counter'].update({}, {
							'$set': {'count': count}
						})

					return "USER CREATED"
				else:
					return "ORGANIZATION CODE INVALID"
			else:
				return "USERNAME ALREADY EXISTS"
		else:
			return "EMAIL ALREADY EXISTS"
	except Exception as e:
		print("Exception creating user: ", str(e))
		return json.dumps({"message": "ERROR CREATING USER"}), 400, {"ContentType": "application/json"}	

###########################################################

def verify_user_credentials(username, password):
	try:
		collection = db_users['users_data']
		check = False
		data = collection.find({"username": str(username)}).count()
		
		if data > 0:
			check = True
		
		data = collection.find({'username': username, 'password': password}).count()
		print("USERNAME: ", username)
		if data > 0:
			return "SUCCESS"
		elif check:
			return "INVALID PASSWORD"
		else:
			return "INVALID USERNAME"

	except Exception as e:
		abort(401)

###########################################################