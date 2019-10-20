from flask import request, Blueprint, jsonify, abort
from . import db
import datetime as dt

bp = Blueprint('api', __name__, url_prefix='/api')


err_json = "Error: Request was not JSON"
err_auth = "Error: Invalid password"
err_user_exists = "Error: Username already exists"
err_user_not_exists = "Error: Username does not exist"
err_email_exists = "Error: Email already exists"
err_dev_exists = "Error: Device already exists"
err_dev_not_exists = "Error: Device does not exist"

### USERS api
@bp.route('/users', methods=('GET', 'POST', 'PUT', 'DELETE'))
def api_user():
    if request.method == 'POST': #create new user
        if not request.is_json: abort(400, err_json)
        req_data = request.get_json()

        if 'username' not in req_data.keys(): abort(400, "Error: Username not provided")
        if 'password' not in req_data.keys(): abort(400, "Error: Password not provided")
        username = req_data['username']
        password = req_data['password']
        
        if db.check_if_user_exists(username): abort(409, err_user_exists)
        
        if 'email' in req_data.keys():
            email = req_data['email']
            if db.check_if_email_exists(email): abort(409, err_email_exists)
        else:
            email = None
        
        user_id = db.new_user(username, password, email)
        #user_id = db.get_user_id(username)
        user_json = get_user_json(user_id)
        return jsonify(user_json), 200

    if request.method == 'PUT': #modify an existing user
        username, password = get_user_pass()
        if not db.check_if_user_exists(username): abort(401, err_user_not_exists)
        if not db.check_password(username, password): abort(401, err_auth)
        user_id = db.get_user_id(username)

        if not request.is_json: abort(400, err_json)
        req_data = request.get_json()

        if 'username' in req_data.keys():
            username = req_data['username']
            if db.check_if_user_exists(username): abort(409, err_user_exists)
        else:
            username = None

        if 'password' in req_data.keys():
            password = req_data['password']
        else:
            password = None

        if 'email' in req_data.keys():
            email = req_data['email']
            if db.check_if_email_exists(email): abort(409, err_email_exists)
        else:
            email = None

        db.edit_user(user_id, username, password, email)
        user_json = get_user_json(user_id)
        return jsonify(user_json), 200

    if request.method == 'GET': #get info about an existing user
        username, password = get_user_pass()
        if not db.check_if_user_exists(username): abort(401, err_user_not_exists)
        if not db.check_password(username, password): abort(401, err_auth)
        user_id = db.get_user_id(username)
        user_json = get_user_json(user_id)
        return jsonify(user_json), 200

    if request.method == 'DELETE': #delete an existing user
        username, password = get_user_pass()
        if not db.check_if_user_exists(username): abort(401, err_user_not_exists)
        if not db.check_password(username, password): abort(401, err_auth)
        user_id = db.get_user_id(username)
        db.delete_user(user_id)
        return f"Success: User '{username}' deleted"



### DEVICES api
@bp.route('/devices', methods=('POST', 'PUT', 'GET', 'DELETE'))
def devices_api():
    username, password = get_user_pass()
    if not db.check_if_user_exists(username): abort(401, err_user_not_exists)
    if not db.check_password(username, password): abort(401, err_auth)
    user_id = db.get_user_id(username)
    
    if request.method == 'POST':
        if not request.is_json: abort(400, err_json)
        req_data = request.get_json()
        dev_name = req_data['device_name']
        variables = req_data['variables']
        if 'device_location' in req_data.keys(): dev_loc = req_data['device_location']
        else: dev_loc = None
        
        if db.check_if_device_exists(dev_name, user_id): abort(409, err_dev_exists)
        
        device_id = db.new_device(user_id, dev_name, dev_loc, variables)
        #device_id = db.get_dev_id(dev_name, username)
        device_json = get_dev_json(device_id)
        return jsonify(device_json), 200
    
    if request.method == 'PUT':
        dev_id = request.args.get('device_id', None, int)
        if dev_id is None: abort(400, "Error: Device ID not provided")
        if not db.check_if_device_exists(dev_id=dev_id): abort(404, err_dev_not_exists)

        if not request.is_json: abort(400, err_json)
        req_data = request.get_json()

        if 'device_name' in req_data.keys():
            dev_name = req_data['device_name']
        else:
            dev_name = None
        if 'variables' in req_data.keys():
            variables = req_data['variables']
        else:
            variables = None
        if 'device_location' in req_data.keys():
            dev_loc = req_data['device_location']
        else:
            dev_loc = None

        if db.check_if_device_exists(dev_name, user_id): abort(409, "Error: Device name already exists")

        db.edit_device(dev_id, dev_name, dev_loc, variables)
        device_json = get_dev_json(dev_id)
        return jsonify(device_json), 200

    if request.method == 'GET':
        device_id = request.args.get('device_id', None, int)

        if device_id is not None:
            if not db.check_if_device_exists(dev_id=device_id): abort(404, err_dev_not_exists)
            device_json = get_dev_json(device_id)
            return jsonify(device_json), 200

        if device_id is None:
            devices_dict = {}
            devices = db.get_devices(user_id)

            for idx, device in enumerate(devices):
                devices_dict[idx] = get_dev_json(device['id'])
            return jsonify(devices_dict), 200

    if request.method == 'DELETE':

        device_id = request.args.get('device_id', None, int)
        if device_id is None: abort(400, "Error device ID not provided")
        if not db.check_if_device_exists(dev_id=device_id): abort(404, err_dev_not_exists)

        device_name = db.get_device(device_id)['name']
        db.delete_device(device_id)
        return f"Success: Device '{device_name}' deleted for user '{username}'"



@bp.route('/measurements', methods=('POST', 'GET', 'DELETE'))
def measurements_api():
    username, password = get_user_pass()
    if not db.check_if_user_exists(username): abort(401, err_user_not_exists)
    if not db.check_password(username, password): abort(401, err_auth)
    user_id = db.get_user_id(username)

    dev_name = request.args.get('device_name', None, str)
    meas_id = request.args.get('measurement_id', None, int)
    start = request.args.get('start', None, str)
    stop = request.args.get('stop', None, str)
    lim = request.args.get('lim', None, int)

    if dev_name is None: abort(400, "Error: Device name not provided")
    if not db.check_if_device_exists(dev_name, user_id): abort (404, err_dev_not_exists)
    dev_id = db.get_dev_id(dev_name, username)

    if request.method == 'POST':
        if not request.is_json: return err_json, 400
        req_data = request.get_json()
        var_list = db.get_device_var_list(dev_id)
        for var in req_data.keys():
            if var not in var_list: abort(400, f"Error: Variable '{var}' does not exist for device '{dev_name}'")
        meas_id = db.new_measurement(dev_id, req_data)
        measurement = db.get_measurement(meas_id)
        meas_json = get_meas_json(meas_id)
        return jsonify(meas_json), 200
    
    if request.method == 'DELETE':
        if meas_id is None: abort(400, "Error: Measurement ID not provided")
        if not db.check_if_measurement_exists(meas_id): abort(404, "Error: Measurement ID does not exist")
        db.delete_measurement(meas_id)
        return f"Success: Measurement successfully deleted for device '{dev_name}', user '{username}'"

    if request.method == 'GET':
        if start is not None:
            start = dt.datetime.strptime(start, "%Y%m%dT%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        if stop is not None:
            stop = dt.datetime.strptime(stop, "%Y%m%dT%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

        measurements = db.get_measurements(dev_id, start, stop, lim)
        measurements_dict = {}
        key_to_name_dict = db.var_key_to_name_dict(dev_id)
        for idx, meas in enumerate(measurements):
            measurements_dict[idx] = get_meas_json(meas['id'], key_to_name_dict)
        return jsonify(measurements_dict), 200

### HELPER functions

def get_user_pass():
    return request.authorization['username'], request.authorization['password']

def get_user_json(user_id):
    user = db.get_user(user_id)
    user_dict = {"user_id": user["id"], "username": user["username"], "email": user['email'], "time_created": user['time_created']}
    return user_dict

def get_dev_json(dev_id):
    device = db.get_device(dev_id)
    dev_dict = {}
    for key in device.keys():
        dev_dict[key] = device[key]
    return dev_dict

def get_meas_json(meas_id, key_to_name):
    meas = db.get_measurement(meas_id)
    meas_dict = {}
    for key in meas.keys():
        if key.startswith('var'): continue
        meas_dict[key] = meas[key]
    for key in key_to_name.keys():
        meas_dict[key_to_name[key]] = meas[key]
    return meas_dict