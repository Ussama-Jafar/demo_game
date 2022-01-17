import docker, os, ssl, time, uuid, shutil
from subprocess import call
from mongo_connection import db_docker
from pymongo import MongoClient
from constants_mongo import *
from constants_spin_docker import *
from process_docker import get_api_key

###########################################################

def start_new_docker(image, name, ports, volume):
	try:
		client = docker.from_env()
		container = client.containers.run(image=image,
										  detach=True,
										  name=name,
										  ports={
											3333:ports['gophish_admin'],
											3499:ports['gophish_user'],
											443:ports['gamification']
										  },
										  volumes={
											volume:{'bind':'/data/db', 'mode':'rw'}
										  })
		container.start()
		time.sleep(3)
		return True
	except Exception as e:
		print("Exception in start_new_docker: ", str(e))
		return False

###########################################################

def get_ports():
	try:
		collection = db_docker['current_ports']
		data = collection.find_one()
		ports = {
			'gophish_admin': int(data['gophish_admin']),
			'gophish_user':int(data['gophish_user']),
			'gamification': int(data['gamification'])
		}
		return ports
	except Exception as e:
		print("Exception in get_ports: ", str(e))

###########################################################

def get_volume(username):
	try:
		path = "".join([VOLUMES_PATH, username])
		os.mkdir(path)
		return path
	except:
		return ""

###########################################################

def spin_docker(username, key, organization):
	ports = get_ports()
	container_name = "".join([username, "_", key])
	volume = get_volume(container_name)
	if not volume:
		return {"message": "FAILED"}
	try:
		if start_new_docker(IMAGE_NAME, container_name, ports, volume):
			print('docker started SUCCESS')
			collection = db_docker['current_ports']
			collection.update_one({}, {"$set": {
					'gophish_admin': int(ports['gophish_admin']+1),
					'gophish_user': int(ports['gophish_user']+1),
					'gamification': int(ports['gamification']+1)
				}})
			
			api_key = get_api_key("admin", ports['gamification'])
			organization_code = get_code(organization)

			db_docker["users_data"].insert({
					"username": username,
					"key": key,
					"gamification": ports['gamification'],
					"gophish_user": ports['gophish_user'],
					"gophish_admin": ports['gophish_admin'],
					"organization_code": organization_code
				})
			return {
				"message": "SUCCESS",
				"gamification": ports['gamification'],
				"gophish_user": ports['gophish_user'],
				"gophish_admin": ports['gophish_admin'],
				"api_key": api_key,
				"organization_code": organization_code 
			}
		else:
			return {"message": "FAILED"}

	except Exception as e:
		print('Exception in spin docker: ', str(e))
		return {"message": "FAILED"}

###########################################################

def get_code(name):
	name = name.lower()
	name = name.replace(" ", "?")
	uid = uuid.uuid1()
	collection = db_docker["users_data"]
	organization_code = "".join([name, "-", uid.hex])
	count = collection.find({'organization_code': organization_code}).count()
	while count > 0:
		uid = uuid.uuid1()
		organization_code = "".join([name, "-", uid.hex])
		count = db.find({'organization_code': organization_code})

	return organization_code

###########################################################

def remove_docker(username, key):
	try:
		container_name = "{}_{}".format(username, key)
		volume = "".join([VOLUMES_PATH, container_name])
		if os.path.exists(volume):
			command = REMOVE_DIR_COMMAND.format(volume)
			call('echo {} | /usr/bin/sudo -S {}'.format(PASSWORD, command), shell=True)
		client = docker.from_env()
		try:
			container = client.containers.get(container_name)
		except:
			return {"message": "NO DOCKER FOUND"}
		if container.status == "running":
			client.containers.get(container_name).kill()
		client.containers.get(container_name).remove()
		print("Docker remove SUCCESS")
		return {"message": "DOCKER REMOVED"}
	except Exception as e:
		container_name = "{}_{}".format(username, key)
		volume = "".join([VOLUMES_PATH, container_name])
		if os.path.exists(volume):
			command = REMOVE_DIR_COMMAND.format(volume)
			call('echo {} | /usr/bin/sudo -S {}'.format(PASSWORD, command), shell=True)
			return {"message": "NO DOCKER RUNNING"}
		return {"message": "NO DOCKER FOUND"}
###########################################################
