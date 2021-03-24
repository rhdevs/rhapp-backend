

from flask import Flask
from flask_cors import CORS, cross_origin
import os
import pymongo
from Laundry.LaundryAPI import laundry_api

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = "Content-Type"
app.config['SECRET_KEY'] = os.getenv('AUTH_SECRET_KEY')

app.register_blueprint(laundry_api, url_prefix="/laundry")


@app.route("/")
def hello():
    return "hello backend"


if __name__ == "__main__":
    app.run("0.0.0.0", port=8080)
