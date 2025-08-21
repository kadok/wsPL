import os
import json
from pymongo import MongoClient

#Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/") 

#Select or Create a Database
db = client["pl"]
collection = db["premier"]

#Load the JSON Data
folder = "data"

for file in os.listdir(folder):
    if file.endswith(".json"):
        season = file.replace(".json", "")
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            data = json.load(f)

        #Insert Data into a Collection
        for jogador in data["stats"]["content"]:
            jogador["season"] = season
            collection.insert_one(jogador)
            #collection.update_one(jogador, upsert=True)

print("Data inserted on MongoDB!")

# Close the connection
client.close()