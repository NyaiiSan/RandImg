import os
from flask import Flask, render_template, send_file, request, session, abort, jsonify

from imgdb import ImageDatabase
from imgmanager import *

ADMIN_INFO = {
    'name': 'admin',
    'key': 'admin'
}

db = ImageDatabase('images.db')

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/img")
def img():
    
    url = db.random_url()
    if not url:
        abort(404)
    
    image_data, image_type = get_image(url)

    if image_type:
        return send_file(image_data, mimetype = image_type)
    
    db.error_url(url)

    abort(500, image_data)

@app.route("/insert", methods = ['GET', 'POST'])
def insert():
    user = session.get('user')
    if request.method == 'GET':

        if user == get_ip():
            return render_template('insert.html')
        
        name = request.args.get('name')
        key = request.args.get('key')
        if(name == ADMIN_INFO['name'] and key == ADMIN_INFO['key']):
            session['user'] = get_ip()
            return render_template('insert.html')
        else:
            abort(403)

    if request.method == 'POST':
        response = {
            'status': -1,
            'message': None
        }

        # 验证身份
        if user != get_ip():
            response['message'] = 'Unauthorized'
            return jsonify(response), 401

        url = request.json.get('url')
        des = request.json.get('des')
        if not url or not des:
            response['message'] = 'Invalid request'
            return jsonify(response), 400
        
        image_data, image_type = get_image(url)

        if image_type is None:
            response['message'] = image_data
            return jsonify(response), 404

        db.insert_url(url, des)
        
        response['message'] = "success"
        return jsonify(response)
    
def get_ip() -> str:
    ip = request.headers.get('X-Forwarded-For', None)
    if not ip:
        ip = request.remote_addr

    return ip


