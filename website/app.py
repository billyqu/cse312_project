from flask import Flask, jsonify, request, render_template, redirect, url_for, session, make_response
import pymongo
import bcrypt

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

@app.route('/register-account', methods=['POST'])
def registerAccount():
    username = request.form['username']
    password = request.form['password']

    existing_username = db.users.find_one({'username': username})
    if existing_username:
        response = make_response(
            jsonify({'success': False, 'message': 'Username is already in use'}))
        return response
    
    user_id = get_next_id()
    session['user'] = user_id

    salt = bcrypt.hashpw(password.encode(), salt)
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    user = {'id': user_id, 'username': username, 'password': hashed_password}
    users_collection.insert_one(user)
    return redirect(url_for('index'))

    # Redirect to index endpoint
    # return render_template('index.html')
@app.route('/login', methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']

    user = db.users.find_one({'username': username})
    print(user)
    if user:
        session['user'] = user['id']
        return redirect(url_for('index'))
    else:
        response = make_response(jsonify({'success': False, 'message': 'Error logging in. Try again.'}))
        return response

@app.route('/get-user', methods=["GET"])
def getUser():
    user_session = session['user']
    if user_session:
        print(user_session, " usersession")
        user = users_collection.find_one({'id': user_session})
        print(user, " user")
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)