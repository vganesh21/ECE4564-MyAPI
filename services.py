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

#Init authentication and Flask interaction
app = Flask(__name__)
auth = HTTPBasicAuth()

#Establish username-password that have access to the API
users = {
    "admin": generate_password_hash("secret"),
    "varun": generate_password_hash("ganesh")
}

#This function will verify that the client provided user-pass is valid
@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

#The general page
@app.route('/')
@auth.login_required
def index():
    return "Hello, %s!" % auth.username()

#The Marvel route that will obtain given story info if it exists
@app.route('/Marvel', methods=['GET'])
@auth.login_required
def get_marvel():
    #This gets the query string with the info wanted
    story_no = request.args.get('story', None)
    if story_no == None:
        abort(400)
    #These next 3 lines set up the parameters for the marvel api gateway
    ts = str(time.time())
    prehash = ts+marvel_api_private+marvel_api_public
    apiHash = hashlib.md5(prehash.encode()).hexdigest()
    #The url will access the story
    url = "http://gateway.marvel.com/v1/public/stories/36864?apikey=%s&hash=%s&ts=%s" % (marvel_api_public,apiHash,ts)
    #The Response is returned and stored as a JSON Response
    r = requests.get(url)
    data = jsonify(r.json())
    #The information is then stored in a file in the same directory
    f= open("marvelStories.txt","w+")
    f.write(data.get_data(as_text=True))
    f.close()
    #The JSON Response is returned
    return data

#The Canvas route that will download the passed in file
@app.route('/Canvas', methods=['GET'])
@auth.login_required
def get_canvas():
    #This gets the query string with the info wanted
    filename = request.args.get('file', None)
    if filename == None:
        abort(400)
    #The url will direct to JSON information about the file
    url = "https://vt.instructure.com/api/v1/courses/%s/files/?search_term=%s&access_token=%s" % (course_id, filename, canvas_api)
    #The Response is returned and stored as a JSON Response
    file = requests.get(url)
    data = jsonify(file.json())
    #The JSON Response is deserialized and parsed to find the download url
    decodeddata = json.loads(file.text)
    dats = decodeddata[0]
    stad = dats["url"]
    #The a GET request is issued through the download url returning the file contents
    data2 = requests.get(stad, allow_redirects=True)
    #A new file is created in the same directory and the content is saved in it
    open(filename, 'wb').write(data2.content)
    #The first JSON Response is returned
    return data

if __name__ == '__main__':
    #These lines get the Command Line Arguments and make sure they are valid
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




