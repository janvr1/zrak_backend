from flask import request, Blueprint
from . import db
import pandas as pd
import json

bp = Blueprint('api', __name__, url_prefix='/api')


err_json = "Error: Request was not JSON"
err_auth = "Error: Invalid username/password"

### USERS api
@bp.route('/users/new', methods=('POST', ))
def newUser():
    if not request.is_json: return err_json
    req_data = request.get_json()
    username = req_data['username']
    password = req_data['password']
    email = None
    if 'email' in req_data.keys():
        email = req_data['email']
    db.new_user(username, password, email)
    return f"Success: User {username} created"


### DEVICES api
@bp.route('/devices/new', methods=('POST', ))
def newDevice():
    if not request.is_json: return err_json
    username, password = get_user_pass()
    user_id = db.get_user_id(username)
    if not db.check_password(username, password): return err_auth
    req_data = request.get_json()
    dev_name = req_data['device_name']
    dev_loc = req_data['device_location']
    var_list = req_data['variables']
    print(var_list, flush=True)
    db.new_device(user_id, dev_name, dev_loc, var_list)
    return f"Success: Device {dev_name} for user {username} created"

@bp.route('/devices/delete', methods=('POST', ))
def deleteDevice():
    if not request.is_json: return err_json
    username, password = get_user_pass()
    if not db.check_password(username, password): return err_auth
    dev_name = request.get_json()['device_name']
    dev_id = db.get_dev_id(username, dev_name)
    db.delete_device(dev_id)
    return f"Success: Device {dev_name} deleted for user {username}"

@bp.route('/devices/getAll', methods=('GET', ))
def getDevices():
    username, password = get_user_pass()
    user_id = db.get_user_id(username)
    if not db.check_password(username, password): return err_auth
    devices = db.get_devices(user_id)
    df = pd.DataFrame(devices)
    df.columns = devices.keys()
    return df.to_csv(index=False)

@bp.route('/measurements/new', methods=('POST', ))
def newMeasurement():
    if not request.is_json: return err_json
    username, password = get_user_pass()
    if not db.check_password(username, password): return err_auth
    req_data = request.get_json()
    dev_name = req_data['device_name']
    data = req_data['data']
    db.new_measurement(db.get_dev_id(dev_name, username), data)
    return f"Succes: Measurement added for {dev_name}. Data = {json.dumps(data)}"

### HELPER functions

def get_user_pass():
    return request.authorization['username'], request.authorization['password']