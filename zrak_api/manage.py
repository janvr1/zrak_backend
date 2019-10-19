from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from .auth import login_required

bp = Blueprint('manage', __name__, url_prefix='/manage')

@bp.route('/')
def index():
    return redirect(url_for('manage.users_view'))

@bp.route('/users')
@login_required
def users_view():
    users = db.get_all_users()
    return render_template('manage/users.html', users=users)

@bp.route('/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    db.delete_user(user_id)
    return redirect(url_for('manage.users_view'))

@bp.route('users/edit/<int:user_id>', methods=('GET', 'POST'))
@login_required
def edit_user(user_id):
    if request.method == 'POST':
        username = request.form['username']
        if username != '':
            if db.check_if_user_exists(username):
                flash("Username already exists")
                return redirect(url_for('manage.edit_user', user_id=user_id))
        else:
            username = None
        email = request.form['email']
        if email != '':
            if db.check_if_email_exists(email):
                flash("Email already exists")
                return redirect(url_for('manage.edit_user', user_id=user_id))
        else:
            email = None
        user_type = request.form['user_type']
        if user_type != '':
            user_type = int(user_type)
            if (user_type < 0) or (user_type>1):
                flash("user_type can only be 0 (ordinary user) or 1 (admin)")
                return redirect(url_for('manage.edit_user', user_id=user_id))
        else:
            user_type = None

        db.edit_user(user_id, username=username, email=email, user_type=user_type)
        return redirect(url_for('manage.users_view'))
    if request.method == 'GET':
        user = db.get_user(user_id)
        return render_template('manage/users_edit.html', user=user)

@bp.route('/devices/<int:user_id>')
@login_required
def devices_view(user_id):
    devices = db.get_devices(user_id)
    username = db.get_user(user_id)['username']
    return render_template('manage/devices.html', devices=devices, username=username)

@bp.route('/devices/<int:user_id>/delete/<int:dev_id>')
@login_required
def delete_device(user_id, dev_id):
    db.delete_device(dev_id)
    return redirect(url_for('manage.devices_view', user_id=user_id))

@bp.route('devices/edit/<int:dev_id>', methods=('GET', 'POST'))
@login_required
def edit_device(dev_id):
    device = db.get_device(dev_id)
    user = db.get_user(device['user_id'])
    if request.method == 'POST':
        dev_name = request.form['dev_name']
        if dev_name != '':
            if db.check_if_device_exists(dev_name=dev_name, user_id=user['id']):
                flash("Device name already exists")
                return redirect(url_for('manage.edit_device', dev_id=dev_id))
        else:
            dev_name = None

        dev_loc = request.form['dev_loc']
        if dev_loc == '': dev_loc = None

        variables = request.form['vars']
        if variables != '':
            var_list = [var.strip() for var in variables.split(',')]
        else:
            variables = None

        db.edit_device(dev_id, dev_name, dev_loc, var_list)
        return redirect(url_for('manage.devices_view', user_id=user['id']))
    if request.method == 'GET':
        return render_template('manage/devices_edit.html', device=device, username=user['username'])

@bp.route('/measurements/<int:dev_id>')
@login_required
def measurements_view(dev_id):
    measurements = db.get_last_n_measurements(dev_id, 10)
    key_to_name_dict = db.var_key_to_name_dict(dev_id)
    dev_name = db.get_device(dev_id)['name']
    username = db.get_user(db.get_device(dev_id)['user_id'])['username']
    variables = db.var_key_to_name_dict(dev_id)
    return render_template('manage/measurements.html', measurements=measurements,
                            variables=variables, dev_name=dev_name, username=username)

@bp.route('/measurements/<int:dev_id>/delete/<int:meas_id>')
@login_required
def delete_measurement(dev_id, meas_id):
    db.delete_measurement(meas_id)
    return redirect(url_for('manage.measurements_view', dev_id=dev_id))