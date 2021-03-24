import pymongo
DB_USERNAME = "rhdevs-db-admin"
DB_PWD = "rhdevs-admin"
AUTH_SECRET_KEY = "rhdevs-32806134351679125416"


URL = "mongodb+srv://{}:{}@cluster0.0urzo.mongodb.net/RHApp?retryWrites=true&w=majority".format(
    DB_USERNAME, DB_PWD)

client = pymongo.MongoClient(URL)
db = client["RHApp"]
