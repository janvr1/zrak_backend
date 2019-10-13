import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug import generate_password_hash, check_password_hash
import pandas as pd
import json

err_user_not_exists = "Error: Username {} does not exist"
err_dev_not_exists = "Error: Device {} dost not exist"
err_user_exists = "Error: Username {} already exists"
err_dev_exists = "Error: Device {} already exists"
err_pass = "Error: Passwords do not match"

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

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables"""
    db = get_db()
    
    cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    db.execute("PRAGMA foreign_keys = OFF")
    for table in tables:
        db.execute(f"DROP TABLE {table['name']}")
    db.execute("PRAGMA foreign_key = ON")
    db.commit()

    init_db()
    click.echo("Initialized the database")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def check_if_user_exists(username):
    db = get_db()
    sql_cmd = "SELECT id FROM users WHERE username=?"
    if db.execute(sql_cmd, (username, )).fetchone() is not None:
        return True
    return False

def check_if_device_exists(username, dev_name):
    db = get_db()
    sql_cmd = "SELECT id FROM devices WHERE user_id=? AND name=?"
    if db.execute(sql_cmd, (get_id_from_user(username), dev_name)).fetchone() is not None:
        return True
    return False

def get_id_from_user(username):
    db = get_db()
    sql_cmd = "SELECT id FROM users WHERE username=?"
    user = db.execute(sql_cmd, (username, )).fetchone()
    return user['id']

def get_user_from_id(id):
    db = get_db()
    sql_cmd = "SELECT username FROM users WHERE id=?"
    user = db.execute(sql_cmd, (id, )).fetchone()
    return user['username']

def get_device_id(username, dev_name):
    db = get_db()
    sql_cmd = "SELECT id FROM devices WHERE name=? AND user_id=?"
    user_id = get_id_from_user(username)
    device = db.execute(sql_cmd, (dev_name, user_id)).fetchone()
    return device['id']

def get_device_name(dev_id):
    db = get_db()
    sql_cmd = "SELECT name FROM devices WHERE id=?"
    device = db.execute(sql_cmd, (dev_id, )).fetchone()
    return device['name']

def create_table_for_device(dev_id, var_list):
    db = get_db()
    table_name = f"measurements_{dev_id}"
    sql_cmd_1 = f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL)"
    db.execute(sql_cmd_1)
    for var in var_list:
        sql_cmd_2 = f"ALTER TABLE {table_name} ADD COLUMN {var} REAL"
        db.execute(sql_cmd_2)

    # sql_cmd_2 = ""
    # for var in var_list:
    #     sql_cmd_2 = sql_cmd_2 + f", {var} REAL"
    # sql_cmd_3 = ")"
    # sql_cmd = sql_cmd_1 + sql_cmd_2 + sql_cmd_3
    # db.execute(sql_cmd)
    db.commit()

def delete_table_for_device(dev_id):
    db = get_db()
    sql_cmd = f"DROP TABLE measurements_{dev_id}"
    db.execute(sql_cmd)
    db.commit()

def check_password(username, password):
    db = get_db()
    sql_cmd = "SELECT * FROM users WHERE username=?"
    user = db.execute(sql_cmd, (username, )).fetchone()
    return check_password_hash(user['password'], password)

def new_user(username, password):
    db = get_db()
    if check_if_user_exists(username): return err_user_exists.format(username)
    sql_cmd = "INSERT INTO users(username, password) VALUES(?, ?)"
    password_hash = generate_password_hash(password)
    db.execute(sql_cmd, (username, password_hash))
    db.commit()
    return f"Success: New user {username} created"

def delete_user(username, password):
    db = get_db()
    if not check_if_user_exists(username): return err_user_not_exists.format(username)
    if not check_password(username, password): return err_pass
    sql_cmd = "DELETE FROM users WHERE username=?"
    db.execute(sql_cmd, (username, ))
    db.commit()
    return f"Success: User {username} deleted"

def new_device(username, password, dev_name, dev_location, var_list):
    db = get_db()
    if not check_if_user_exists(username): return err_user_not_exists.format(username)
    if not check_password(username, password): return err_pass
    if check_if_device_exists(username, dev_name): return err_dev_exists.format(dev_name)
    sql_cmd = "INSERT INTO devices(name, location, user_id) VALUES(?, ?, ?)"
    db.execute(sql_cmd, (dev_name, dev_location, get_id_from_user(username)))
    db.commit()
    create_table_for_device(get_device_id(username, dev_name), var_list)
    return f"Success: Device {dev_name} added for user: {username}"

def delete_device(username, password, dev_name):
    db = get_db()
    
    if not check_if_user_exists(username):  return err_user_not_exists.format(username)
    if not check_password(username, password): return err_pass
    if not check_if_device_exists(username, dev_name): return err_dev_not_exists.format(dev_name)

    delete_table_for_device(get_device_id(username, dev_name))
    sql_cmd = "DELETE FROM devices WHERE name=? AND user_id=?"
    db.execute(sql_cmd, (dev_name, get_id_from_user(username)))
    db.commit()
    return f"Success: Device {dev_name} deleted for user {username}"

def get_devices(username, password):
    db = get_db()
    
    if not check_if_user_exists(username): return err_user_not_exists.format(username)
    if not check_password(username, password): return err_pass
    
    sql_cmd = "SELECT * FROM devices WHERE user_id=? ORDER BY name"
    devices = db.execute(sql_cmd, (get_id_from_user(username), )).fetchall()
    device_names = []
    device_locations = []
    for device in devices:
        device_names.append(device['name'])
        device_locations.append(device['location'])

    devices_dict = {"device_name": device_names, "device_location": device_locations}
    df = pd.DataFrame(data=devices_dict)
    return df.to_csv(index=False)

def new_measurement(username, password, dev_name, data):
    db = get_db()
    if not check_if_user_exists(username): return err_user_not_exists
    if not check_password(username, password): return err_pass
    if not check_if_device_exists(username, dev_name): return err_dev_not_exists
    dev_id = get_device_id(username, dev_name)
    cursor = db.execute(f"INSERT INTO measurements_{dev_id}(time) VALUES(CURRENT_TIMESTAMP)")
    row_id = cursor.lastrowid
    for key in data.keys():
        sql_cmd = f"UPDATE measurements_{dev_id} SET {key} = ? WHERE id=?"
        db.execute(sql_cmd, (data[key], row_id))
    db.commit()
    return f"Success: New measurement added for device {dev_name}. Data = {json.dumps(data)}"