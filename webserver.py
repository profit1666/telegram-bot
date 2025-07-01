from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def keep_alive():
    app.run(host='0.0.0.0', port=8080)
