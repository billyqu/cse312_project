from flask import Flask, jsonify, request, render_template, redirect, url_for
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient('mongo')
db = client["main"]
users_collection = db['users']

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register-account', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    user = {'username': username, 'password': password}

    users_collection.insert_one(user)
    # Redirect to index endpoint
    return render_template('index.html')

@app.route('/get-user', methods=["GET"])
def getUser():
    user = users_collection.find_one({})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)