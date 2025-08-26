from pymongo import MongoClient
from config import Config

#Connect to MongoDB
client = MongoClient(Config.DB_LINK) 

#Select or Create a Database
db = client[Config.DATABASE]
collection = db[Config.COLLECTION]

'''
#Filter registers by season
season = "1992-93"
results = collection.find({"season": season})

for r in results:
    print(r["owner"]["name"]["display"], "-", r["value"], "goals")
'''

player = "Alan Shearer"

pipeline = [
    {"$match": {"owner.name.display": player}},   # Filter by player name
    {"$group": {"_id": "$owner.name.display", "total_gols": {"$sum": "$value"}}}
]

resultado = list(collection.aggregate(pipeline))

if resultado:
    print(f"{resultado[0]['_id']} marcou {resultado[0]['total_gols']} gols.")
else:
    print("Jogador não encontrado.")
