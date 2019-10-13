from flask import request, Blueprint
from . import db

api = Blueprint('api', __name__, url_prefix='/api')

err_json = "Request was not in a JSON format"

@api.route('users', methods=('POST', ))
def addOrDeleteUser():
    req_data = request.get_data()
    req_str = req_data.decode()
    if req_str == "newUser":
        return db.new_user(request.authorization['username'], request.authorization['password'])
    if req_str == "deleteUser":
        return db.delete_user(request.authorization['username'], request.authorization['password'])
    else: 
        return "Unknown request string"

@api.route('newDevice', methods=('POST', ))
def newDevice():
    if not request.is_json: return err_json
    username = request.authorization['username']
    password = request.authorization['password']
    req_data = request.get_json()
    dev_name = req_data['device_name']
    dev_loc = req_data['device_location']
    var_list = req_data['variables']
    print(var_list, flush=True)
    return db.new_device(username, password, dev_name, dev_loc, var_list)

@api.route('deleteDevice', methods=('POST', ))
def deleteDevice():
    if not request.is_json: return err_json
    username = request.authorization['username']
    password = request.authorization['password']
    dev_name = request.get_json()['device_name']
    return db.delete_device(username, password, dev_name)

@api.route('getDevices', methods=('GET', ))
def getDevices():
    username = request.authorization['username']
    password = request.authorization['password']
    return db.get_devices(username, password)

@api.route('newMeasurement', methods=('POST', ))
def newMeasurement():
    if not request.is_json: return err_json
    username = request.authorization['username']
    password = request.authorization['password']
    req = request.get_json()
    dev_name = req['device_name']
    data = req['data']
    return db.new_measurement(username, password, dev_name, data)
