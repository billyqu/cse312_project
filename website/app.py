from flask import Flask, jsonify, request, render_template, redirect, url_for, session, make_response
import pymongo
import bcrypt
import html
import eventlet
import socketio

app = Flask(__name__)
app.secret_key = 'random generated key'

client = pymongo.MongoClient('mongo')
db = client["main"]
users_collection = db['users']
users_id_collection = db['users_id']

@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html')
    return render_template('register.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/user/register', methods=['POST'])
def registerAccount():
    username = request.json['username']
    password = request.json['password']

    escaped_username = html.escape(username)

    existing_username = db.users.find_one({'username': escaped_username})
    if existing_username:
        response = make_response(
            jsonify({'success': False, 'message': 'Username is already in use'}))
        return response
    
    user_id = get_next_id()
    session['user'] = user_id

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    user = {'id': user_id, 'username': escaped_username, 'password': hashed_password}
    users_collection.insert_one(user)
    response = make_response(jsonify({'success': True}))
    return response

    # Redirect to index endpoint
    # return render_template('index.html')
@app.route('/user/login', methods=["POST"])
def userLogin():
    username = request.json['username']
    password = request.json['password']

    user = db.users.find_one({'username': username})

    hashed_password = user.get("password")
    password_match = bcrypt.checkpw(password.encode(), hashed_password)

    if user and password_match:
        session['user'] = user['id']
        response = make_response(jsonify({'success': True}))
        return response
    elif not password_match:
        response = make_response(jsonify({'success': False, 'message': 'Incorrect password. Try again.'}))
        return response
    else:
        response = make_response(jsonify({'success': False, 'message': 'Error logging in. Try again.'}))
        return response

@app.route('/user/logout', methods=["POST"])
def logout():
    session.pop('user')
    return redirect(url_for('register'))

@app.route('/user', methods=["GET"])
def getUser():
    user_session = session['user']
    if user_session:
        user = users_collection.find_one({'id': user_session})
        updated_user = user['username']
        return jsonify({'id': user_session, 'user': {'username': updated_user}})
    return redirect(url_for('register'))

def get_next_id():
    id_object = users_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id']) + 1
        users_id_collection.update_one({}, {"$set": {"last_id": next_id}})
        return next_id
    else:
        users_id_collection.insert_one({"last_id": 1})
        return 1

@app.route('/question', methods=["GET"])
def question():
    return render_template('test.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)