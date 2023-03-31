from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient

app = Flask(__name__)

# client = MongoClient('mongodb://localhost/')
# db = client["Main"]

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)