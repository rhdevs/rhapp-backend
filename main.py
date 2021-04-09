

from flask import Flask
from flask_cors import CORS, cross_origin
import os
import pymongo
from Laundry.LaundryAPI import laundry_api
from FacilityBooking.FacilitiesAPI import facilities_api
from Scheduling.SchedulingAPI import scheduling_api
from Authentication.auth import authentication_api

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = "Content-Type"
app.config['SECRET_KEY'] = os.getenv('AUTH_SECRET_KEY')

app.register_blueprint(laundry_api, url_prefix="/laundry")
app.register_blueprint(facilities_api, url_prefix="/facilities")
app.register_blueprint(scheduling_api, url_prefix="/scheduling")
app.register_blueprint(authentication_api, url_prefix="/auth")

@app.route("/")
def hello():
    return "hello backend"


if __name__ == "__main__":
    app.run("0.0.0.0", port=8080)
