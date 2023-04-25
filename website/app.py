from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import pymongo
import bcrypt

app = Flask(__name__)
app.secret_key = 'random generated key'

client = pymongo.MongoClient('mongo')
db = client["main"]
users_collection = db['users']

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
    session['user'] = username

    salt = bcrypt.hashpw(password.encode(), salt)
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    user = {'username': username, 'password': hashed_password}
    users_collection.insert_one(user)
    return redirect(url_for('index'))

    # Redirect to index endpoint
    # return render_template('index.html')

@app.route('/get-user', methods=["GET"])
def getUser():
    user_session = session['user']
    if user_session:
        print(user_session, " usersession")
        user = users_collection.find_one({'username': user_session})
        print(user, " user")
        updated_user = user['username']
        return jsonify({'user': {'username': updated_user}})
    return redirect(url('register'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)