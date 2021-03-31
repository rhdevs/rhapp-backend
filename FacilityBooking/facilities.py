from flask import Flask, request, make_response
from flask_cors import CORS, cross_origin
import pymongo
import json
from datetime import datetime
from threading import Thread


def removeObjectID(xs):
    for i, item in enumerate(xs, start=0):
        del xs[i]["_id"]
    return xs


def listToIndexedDict(xs):
    output = {}
    for i, item in enumerate(xs, start=0):
        del xs[i]["_id"]
        output[i] = item
    return output


# MongoDB
myclient = client = pymongo.MongoClient(
    "mongodb+srv://rhdevs-db-admin:rhdevs-admin@cluster0.0urzo.mongodb.net/RHApp?retryWrites=true&w=majority")
db = myclient["RHApp"]

# Flask
app = Flask("rhapp")
CORS(app, resources={r"/*": {"origins": "*"}})
# resources allowed to be accessed explicitly
# response.headers.add("Access-Control-Allow-Origin", "*"), add this to all responses
# if the cors still now working
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
@cross_origin()
def root_route():
    return 'What up losers'


@app.route('/facilities', methods=["GET"])
@cross_origin(supports_credentials=True)
def all_facilities():
    try:
        data = removeObjectID(
            list(db.Facilities.find().sort([("facilityName", 1)])))
        response = {"status": "success", "data": {"facilities": data}}
    except Exception as e:
        print(e)
        return {"err": str(e), "status": "failed"}, 400
    return make_response(response)


@ app.route('/facilities/<facilityID>', methods=["GET"])
@ cross_origin(supports_credentials=True)
def get_facility_name(facilityID):
    try:
        data = removeObjectID(
            list(db.Facilities.find({"facilityID": int(facilityID)})))
        if len(data) == 0:
            raise Exception("Facility not found")
        response = {"status": "success", "data": data}
    except Exception as e:
        return {"err": str(e), "status": "failed"}, 400
    return make_response(response)


@ app.route('/bookings/<bookingID>', methods=["GET"])
@ cross_origin(supports_credentials=True)
def get_one_booking(bookingID):
    try:
        data = removeObjectID(
            list(db.Bookings.find({"bookingID": int(bookingID)})))
        response = {"status": "success", "data": data}
        if len(data) == 0:
            raise Exception("Booking not found")
    except Exception as e:
        return {"err": str(e), "status": "failed"}, 400
    return make_response(response)


@ app.route('/bookings/user/<userID>', methods=["GET"])
@ cross_origin(supports_credentials=True)
def user_bookings(userID):
    try:
        data = removeObjectID(list(db.Bookings.find(
            {"userID": userID}).sort([("startTime", 1)])))
        response = {"status": "success", "data": data}
    except Exception as e:
        return {"err": str(e), "status": "failed"}, 400
    return make_response(response)


@ app.route('/bookings/facility/<facilityID>/', methods=["GET"])
@ cross_origin(supports_credentials=True)
def check_bookings(facilityID):
    try:
        data = removeObjectID(list(db.Bookings.find({"facilityID": int(facilityID), "startTime": {"$gte": int(
            request.args.get('startTime'))}, "endTime": {"$lte": int(request.args.get('endTime'))}}).sort([("startTime", 1)])))
        response = {"status": "success", "data": data}
    except Exception as e:
        return {"err": str(e), "status": "failed"}, 400

    return make_response(response)


@ app.route('/bookings', methods=['POST'])
@ cross_origin(supports_credentials=True)
def add_booking():
    try:
        formData = request.get_json()
        formData["startTime"] = int(formData["startTime"])
        formData["endTime"] = int(formData["endTime"])

        formData["facilityID"] = int(formData["facilityID"])
        if not formData.get("ccaID"):
            formData["ccaID"] = int(0)
        else:
            formData["ccaID"] = int(formData["ccaID"])

        if (formData["endTime"] < formData["startTime"]):
            raise Exception("End time eariler than start time")

        conflict = removeObjectID(list(db.Bookings.find({"facilityID": formData.get("facilityID"),
                                                         "endTime": {
            "$gte": formData.get('startTime')},
            "startTime": {
            "$lte": formData.get('endTime')}
        })))

        if (len(conflict) != 0):
            raise Exception("Conflict Booking")

        lastbookingID = list(db.Bookings.find().sort(
            [('_id', pymongo.DESCENDING)]).limit(1))
        newBookingID = 1 if len(lastbookingID) == 0 else int(
            lastbookingID[0].get("bookingID")) + 1

        formData["bookingID"] = newBookingID
        db.Bookings.insert_one(formData)
        response = {"status": "success"}

    except Exception as e:
        print(e)
        return {"err": str(e), "status": "failed"}, 400

    return make_response(response)


@ app.route('/bookings/<bookingID>', methods=['GET'])
@ cross_origin(supports_credentials=True)
def get_booking(bookingID):
    try:
        data = listToIndexedDict(
            list(db.Bookings.find({"bookingID": int(bookingID)})))
        response = {"status": "success", "data": data}
    except Exception as e:
        print(e)
        return {"err": str(e), "status": "failed"}, 400
    return make_response(response)


@ app.route('/bookings/<bookingID>', methods=['PUT'])
@ cross_origin(supports_credentials=True)
def edit_booking(bookingID):
    try:
        formData = request.get_json()
        if not formData.get("ccaID"):
            formData["ccaID"] = int(0)
        else:
            formData["ccaID"] = int(formData["ccaID"])

        data = list(db.Bookings.find({"bookingID": int(bookingID)}))

        if (len(data) == 0):
            raise Exception("Booking not found")

        db.Bookings.update_one({"bookingID": int(bookingID)}, {
            "$set": request.get_json()})

        response = {"status": "success"}
    except Exception as e:
        print(e)
        return {"err": str(e), "status": "failed"}, 400

    return make_response(response)


@ app.route('/bookings/<bookingID>', methods=['DELETE'])
@ cross_origin(supports_credentials=True)
def delete_booking(bookingID):
    try:

        data = list(db.Bookings.find({"bookingID": int(bookingID)}))

        if (len(data) == 0):
            raise Exception("Booking not found")

        db.Bookings.delete_one({"bookingID": int(bookingID)})

        response = {"status": "success"}
    except Exception as e:
        print(e)
        return {"err": str(e), "status": "failed"}, 400

    return make_response(response)


@ app.route('/users/telegramID/<userID>', methods=["GET"])
@ cross_origin(supports_credentials=True)
def user_telegram(userID):
    try:
        profile = db.Profiles.find_one({"userID": userID})
        telegramHandle = profile.get(
            'telegramHandle') if profile else "No User Found"
        data = {"telegramHandle": telegramHandle}

        if (telegramHandle == "No User Found"):
            return {"err": "No User Found"}, 400
    except Exception as e:
        print(e)
        return {"err": str(e), "status": "failed"}, 400
    return data, 200


def keep_alive():
    t = Thread(target=run)
    t.start()


def run():
    app.run(host='0.0.0.0', port=8080)


keep_alive()

# if __name__ == '__main__':
#   keep_alive();
#   app.run('0.0.0.0', port=8080)
