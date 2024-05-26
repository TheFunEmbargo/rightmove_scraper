from tinydb import TinyDB, Query

# singleton DB
db = TinyDB("db.json")
PropertyQuery = Query()
