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
