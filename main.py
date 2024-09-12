import os
import sys
import io

import sqlite3
import requests
import mimetypes

from flask import Flask, send_file, request, session, abort, jsonify

SQLITE_PATH = 'data.db'

app = Flask(__name__)
app.secret_key = os.urandom(32)

ADMIN_INFO = {
    'name': 'admin',
    'key': 'admin'
}

@app.route("/")
def index():
    
    url = rand_sqlite()
    if not url:
        abort(404)

    try:
        response = requests.get(url)
        response.raise_for_status()
        image_type = response.headers.get('Content-Type', None)

        if not image_type:
            extension = url.split('.')[-1]
            image_type = mimetypes.types_map.get(f'.{extension}', 'application/octet-stream')

        image_data = io.BytesIO(response.content)

        return send_file(image_data, mimetype = image_type)

    except requests.RequestException as e:
        return str(e), 404

@app.route("/insert")
def insert():
    if 'user' not in session:
        name = request.args.get('name')
        key = request.args.get('key')

        if(name == ADMIN_INFO['name'] and key == ADMIN_INFO['key']):
            session['user'] = get_ip()
        else:
            abort(403)

    if session.get('user') != get_ip:
        session.pop('user')
        return 'ip was changed', 403


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

def get_ip() -> str:
    ip = request.headers.get('X-Forwarded-For', None)
    if not ip:
        ip = request.remote_addr

    return ip

if __name__ == '__main__':

    init_sqlite()
    app.run(host = '0.0.0.0', port = 8080)