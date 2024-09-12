import os
import sys
import io

import sqlite3
import requests
import mimetypes

from flask import Flask, render_template, send_file, request, session, abort, jsonify

SQLITE_PATH = 'data.db'

app = Flask(__name__)
app.secret_key = os.urandom(32)

ADMIN_INFO = {
    'name': 'admin',
    'key': 'admin'
}

ERROR_URLS = dict()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/img")
def img():
    
    url = rand_sqlite()
    if not url:
        abort(404)
    
    image_data, image_type = get_image(url)

    if image_type:
        return send_file(image_data, mimetype = image_type)
    
    # url 的出错次数加一
    if ERROR_URLS.get(url):
        ERROR_URLS[url] += 1
    else:
        ERROR_URLS[url] = 1

    # 超过三次就从数据库里删除这个url
    if ERROR_URLS[url] > 3:
        delete_sqlite(url)

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
            response['message'] = 'invalid request'
            return jsonify(response), 400
        
        image_data, image_type = get_image(url)

        if image_type is None:
            response['message'] = image_data
            return jsonify(response), 400

        with sqlite3.connect(SQLITE_PATH) as conn:
            img_id = conn.execute('''SELECT MAX(id) FROM images;''').fetchone()[0]
            if img_id:
                img_id = img_id + 1
            else:
                img_id = 1
            sql_cmd = '''INSERT INTO images(id, url, des) VALUES(?, ?, ?);'''
            conn.execute(sql_cmd, (img_id, url, des))
            conn.commit()
            response['status'] = 0
            response['message'] = 'success'
            
        if response['status']:
            return jsonify(response), 400
        
        return jsonify(response)


# 尝试从 url 获取图片
def get_image(url: str) -> tuple[str, str] | tuple[str, None]:
    try:
        response = requests.get(url)
        response.raise_for_status()
        image_type = response.headers.get('Content-Type', None)

        if not image_type:
            extension = url.split('.')[-1]
            image_type = mimetypes.types_map.get(f'.{extension}', 'application/octet-stream')

        image_data = io.BytesIO(response.content)

    except Exception as e:
        return str(e), None
    
    return image_data, image_type

def init_sqlite() -> None :
    with sqlite3.connect(SQLITE_PATH) as conn:
        sql_cmd = '''CREATE TABLE IF NOT EXISTS images(
            id      INT     NOT NULL    PRIMARY KEY,
            url     TEXT    NOT NULL,
            des     TEXT
        );'''
        conn.execute(sql_cmd)
def rand_sqlite(num = 1) -> str | None:

    url = None
    with sqlite3.connect(SQLITE_PATH) as conn:
        sql_cmd = '''SELECT url FROM images ORDER BY RANDOM() LIMIT {};'''.format(num)
        sel_data = conn.execute(sql_cmd).fetchone()
        print(sel_data)

    if sel_data:
        url = sel_data[0]

    return url

def delete_sqlite(url: str) -> bool:
    try:
        with sqlite3.connect(SQLITE_PATH) as conn:
            sql_cmd = '''DELETE FROM images WHERE url = '{}';'''.format(url)
            conn.execute(sql_cmd)
            return True
    except Exception as e:
        print(e)
        return False

def get_ip() -> str:
    ip = request.headers.get('X-Forwarded-For', None)
    if not ip:
        ip = request.remote_addr

    return ip

if __name__ == '__main__':

    init_sqlite()
    app.run(host = '0.0.0.0', port = 8080)