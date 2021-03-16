from flask import Flask
from LaundryAPI import laundry_api

app = Flask(__name__)

app.register_blueprint(laundry_api)

@app.route("/")
def hello():
    return "hello backend"

if __name__ == "__main__":
    app.run()
