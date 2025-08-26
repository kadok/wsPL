import os
import json
from pymongo import MongoClient
from config import Config

#Connect to MongoDB
client = MongoClient(Config.DB_LINK) 

#Select or Create a Database
db = client[Config.DATABASE]
collection = db[Config.COLLECTION]

#Load the JSON Data
folder = Config.DATA

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