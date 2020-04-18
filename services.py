#!flask/bin/python
import sys
import argparse
import time
import requests
import hashlib
import json
from flask import Flask, jsonify, request, abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from servicesApiKeys import canvas_api, marvel_api_public, marvel_api_private, course_id

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("secret"),
    "varun": generate_password_hash("ganesh")
}

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@app.route('/')
@auth.login_required
def index():
    return "Hello, %s!" % auth.username()

@app.route('/Marvel', methods=['GET'])
@auth.login_required
def get_marvel():
    #?story=<story_no>
    story_no = request.args.get('story', None)
    if story_no == None:
        abort(400)
    ts = str(time.time())
    prehash = ts+marvel_api_private+marvel_api_public
    apiHash = hashlib.md5(prehash.encode()).hexdigest()
    url = "http://gateway.marvel.com/v1/public/stories/36864?apikey=%s&hash=%s&ts=%s" % (marvel_api_public,apiHash,ts)
    r = requests.get(url)
    data = jsonify(r.json())
    f= open("marvelStories.txt","w+")
    f.write(data.get_data(as_text=True))
    f.close()
    return data


@app.route('/Canvas', methods=['GET'])
@auth.login_required
def get_canvas():
    #?file=<filename>
    filename = request.args.get('file', None)
    if filename == None:
        abort(400)

    url = "https://vt.instructure.com/api/v1/courses/%s/files/?search_term=%s&access_token=%s" % (course_id, filename, canvas_api)
    file = requests.get(url)
    data = jsonify(file.json())
    decodeddata = json.loads(file.text)
    dats = decodeddata[0]
    stad = dats["url"]
    data2 = requests.get(stad, allow_redirects=True)
    open(filename, 'wb').write(data2.content)
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Processes arguments')
    parser.add_argument('-p', help='Set the server port.')
    args = parser.parse_args()
    if args.p == None:
        print('Please set server port number with the -p flag.')
        sys.exit(1)

    try:
        nport = int(args.p)
    except Exception as ex:
        print(ex)
        sys.exit(1)

    app.run(port=nport,debug=True)




