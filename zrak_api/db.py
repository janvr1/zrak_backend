import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug import generate_password_hash, check_password_hash

### CORE functions

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    pass_hash = generate_password_hash("admin")
    sql_cmd = "INSERT INTO users(username, password, user_type) VALUES(?, ?, ?)"
    db.execute(sql_cmd, ("admin", pass_hash, 1))
    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo("Initialized the database")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


### USERS functions
def new_user(username, password, email=None):
    db = get_db()
    password_hash = generate_password_hash(password)
    sql_cmd = "INSERT INTO users(username, password, email) VALUES(?, ?, ?)"
    cursor = db.execute(sql_cmd, (username, password_hash, email))
    db.commit()
    return cursor.lastrowid


def edit_user(user_id, username=None, password=None, email=None):
    db = get_db()
    if username is not None:
        sql_cmd = "UPDATE users SET username=? WHERE id=?"
        db.execute(sql_cmd, (username, user_id))
    if password is not None:
        sql_cmd = "UPDATE users SET password=? WHERE id=?"
        password_hash = generate_password_hash(password)
        db.execute(sql_cmd, (password_hash, user_id))
    if email is not None:
        sql_cmd = "UPDATE users SET email=? WHERE id=?"
        db.execute(sql_cmd, (email, user_id))
    db.commit()


def delete_user(user_id):
    db = get_db()
    #delete_devices_for_user(user_id)
    sql_cmd = "DELETE FROM users WHERE id=?"
    db.execute(sql_cmd, (user_id, ))
    db.commit()

def get_user(id=None, username=None, email=None):
    db = get_db()
    if id is not None:
        sql_cmd = "SELECT * FROM users WHERE id=?"
        return db.execute(sql_cmd, (id, )).fetchone()
    if username is not None:
        sql_cmd = "SELECT * FROM users WHERE username=?"
        return db.execute(sql_cmd, (username, )).fetchone()
    if email is not None:
        sql_cmd = "SELECT * FROM users WHERE email=?"
        return db.execute(sql_cmd, (email, )).fetchone()

def get_all_users():
    db = get_db()
    sql_cmd = "SELECT * FROM users ORDER BY id"
    return db.execute(sql_cmd).fetchall()

def change_password(user_id, new_password):
    db = get_db()
    sql_cmd = "UPDATE TABLE users SET password=? WHERE id=?"
    pass_hash = generate_password_hash(new_password)
    db.execute(sql_cmd, (pass_hash, user_id))
    db.commit()

def change_email(user_id, new_email):
    db = get_db()
    sql_cmd = "UPDATE TABLE users SET email=? WHERE id=?"
    db.execute(sql_cmd, (new_email, user_id))
    db.commit()

### DEVICES functions
def get_device(dev_id=None, dev_name=None, user_id=None):
    db = get_db()
    if dev_id is not None:
        sql_cmd = "SELECT * FROM DEVICES WHERE id=?"
        return db.execute(sql_cmd, (dev_id, )).fetchone()
    if (dev_name is not None) and (user_id is not None):
        sql_cmd = "SELECT * FROM devices WHERE name=? AND user_id=?"
        return db.execute(sql_cmd, (dev_name, user_id)).fetchone()

def get_devices(user_id=None):
    db = get_db()
    if user_id is not None:
        sql_cmd = "SELECT * FROM devices WHERE user_id=? ORDER BY name"
        return db.execute(sql_cmd, (user_id, )).fetchall()
    sql_cmd = "SELECT * FROM devices ORDER BY name"
    return db.execute(sql_cmd).fetchall()

def new_device(user_id, dev_name, dev_location=None, variable_list=None):
    db = get_db()
    var_list = [None]*10
    for i, var in enumerate(variable_list):
        var_list[i] = var
    sql_cmd = "INSERT INTO devices(name, location, user_id, var0, var1, var2, var3, var4, var5, var6, var7, var8, var9) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cursor = db.execute(sql_cmd, (dev_name, dev_location, user_id, *var_list))
    db.commit()
    return cursor.lastrowid

def edit_device(dev_id, dev_name=None, dev_loc=None, variable_list=None):
    db = get_db()
    if dev_name is not None:
        sql_cmd = "UPDATE devices SET name=? WHERE id=?"
        db.execute(sql_cmd, (dev_name, dev_id))
    if dev_loc is not None:
        sql_cmd = "UPDATE devices SET location=? WHERE id=?"
        db.execute(sql_cmd, (dev_loc, dev_id))
    if variable_list is not None:
        var_list = [None]*10
        for i, var in enumerate(variable_list):
            var_list[i] = var
        sql_cmd = "UPDATE devices SET var0=?, var1=?, var2=?, var3=?, var4=?, var5=?, var6=?, var7=?, var8=?, var9=? WHERE id=?"
        db.execute(sql_cmd, (*var_list, dev_id))
    db.commit()

def delete_device(dev_id):
    db = get_db()
    #delete_measurements_for_device(dev_id)
    sql_cmd = "DELETE FROM devices WHERE id=?"
    db.execute(sql_cmd, (dev_id,))
    db.commit()

def change_dev_name(dev_id, new_name):
    db = get_db()
    sql_cmd = "UPDATE TABLE devices SET name=? WHERE id=?"
    db.execute(sql_cmd, (new_name, dev_id))
    db.commit()

def change_dev_location(dev_id, new_location):
    db = get_db()
    sql_cmd = "UPDATE TABLE devices SET location=? WHERE id=?"
    db.execute(sql_cmd, (new_location, id))
    db.commit()

def change_dev_var(dev_id, old_var, new_var):
    db = get_db()
    device = get_device(dev_id)
    var_key = var_key_to_name_dict(dev_id)[old_var]
    sql_cmd = f"UPDATE TABLE devices SET {var_key}=? WHERE id=?"
    db.execute(sql_cmd, (new_var, dev_id))
    db.commit()

### MEASUREMENTS functions
def new_measurement(dev_id, data):
    db = get_db()
    device = get_device(dev_id=dev_id)
    values = [None]*11
    values[0] = dev_id
    sql_cmd = "INSERT INTO measurements(dev_id) VALUES(?)"
    cursor = db.execute(sql_cmd, (dev_id, ))
    row_id = cursor.lastrowid
    name_key_dict = var_name_to_key_dict(dev_id)
    for var_name in data.keys():
        var_key = name_key_dict[var_name]
        sql_cmd = f"UPDATE measurements SET {var_key}=? WHERE id=?"
        db.execute(sql_cmd, (data[var_name], row_id))
    db.commit()
    return row_id

def get_measurement(meas_id=None, dev_id=None, time=None):
    db = get_db()
    if meas_id is not None:
        sql_cmd = "SELECT * FROM measurements WHERE id=?"
        return db.execute(sql_cmd, (meas_id, )).fetchone()
    if (dev_id is not None) and (time is not None):
        sql_cmd = "SELECT * FROM measurements WHERE dev_id=? AND time=?"
        return db.execute(sql_cmd, (dev_id, time)).fetchone()

def delete_measurement(meas_id):
    db = get_db()
    sql_cmd = "DELETE FROM measurements WHERE id=?"
    db.execute(sql_cmd, (meas_id, ))
    db.commit()

def get_last_n_measurements(dev_id, n):
    db = get_db()
    sql_cmd = "SELECT * FROM measurements WHERE dev_id=? LIMIT ?"
    return db.execute(sql_cmd, (dev_id, n)).fetchall()

def get_measurements_range(dev_id, time_start, time_stop):
    db = get_db()
    sql_cmd = "SELECT * FROM measurements WHERE dev_id=? AND time>=? AND time<=?"
    return db.execute(sql_cmd, (dev_id, time_start, time_stop)).fetchall()

def delete_measurements_range(dev_id, time_start, time_stop):
    db = get_db()
    sql_cmd = "DELETE FROM measurements WHERE dev_id=? AND time>=? AND time<=?"
    db.execute(sql_cmd, (dev_id, time_start, time_stop))
    db.commit()


### HELPER functions
def check_if_user_exists(username):
    if get_user(username=username) is not None:
        return True
    return False

def check_if_email_exists(email):
    if get_user(email=email) is not None:
        return True
    return False

def check_if_device_exists(dev_name=None, user_id=None, dev_id=None):
    if (dev_name is not None) and (user_id is not None):
        if get_device(dev_name = dev_name, user_id=user_id) is not None:
            return True
        return False
    if dev_id is not None:
        if get_device(dev_id) is not None:
            return True
        return False

def check_password(username, password):
    user = get_user(username=username)
    return check_password_hash(user['password'], password)

def get_user_id(username):
    user = get_user(username=username)
    return user['id']

def get_dev_id(dev_name, username):
    user_id = get_user_id(username)
    device = get_device(dev_name=dev_name, user_id=user_id)
    return device['id']

def get_var_key(dev_id, var):
    d = var_name_to_key_dict_dict(dev_id)
    return d[var]

def var_key_to_name_dict(dev_id):
    db = get_db()
    device = db.execute("SELECT var0, var1, var2, var3, var4, var5, var6, var7, var8, var9 FROM devices WHERE id=?", (dev_id, )).fetchone()
    d = {}
    for key in device.keys():
        if device[key] is not None: d[key] = device[key]
    return d

def var_name_to_key_dict(dev_id):
    db = get_db()
    device = db.execute("SELECT var0, var1, var2, var3, var4, var5, var6, var7, var8, var9 FROM devices WHERE id=?", (dev_id, )).fetchone()
    d = {}
    for idx, name in enumerate(device):
        if name is not None: d[name] = device.keys()[idx]
    return d

def delete_devices_for_user(user_id):
    db = get_db()
    devices = get_devices(user_id)
    for device in devices:
        dev_id = device['id']
        delete_measurements_for_device(dev_id)
        delete_device(dev_id)

def delete_measurements_for_device(dev_id):
    db = get_db()
    sql_cmd = "DELETE FROM measurements WHERE dev_id=?"
    db.execute(sql_cmd, (dev_id, ))
    db.commit()