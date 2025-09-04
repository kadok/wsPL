import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
from config import Config

#Connect to MongoDB
client = MongoClient(Config.DB_LINK)
db = client[Config.DATABASE]
collection = db[Config.COLLECTION]

# List all registers
docs = list(collection.find({}, {"season": 1, "value": 1, "_id": 0}))

# Convert to Dataframe
df = pd.DataFrame(docs)

# Rename Value
df = df.rename(columns={"value": "goals"})

# Sum the total goals by season 
df_total = df.groupby("season")["goals"].sum().reset_index()

# Sort the seasons
df_total["season_year"] = df_total["season"].str[:4].astype(int)
df_total = df_total.sort_values("season_year")

# Remove the last Session, the incomplete one
last_season = df_total["season"].iloc[-1]
df_total = df_total[df_total["season"] != last_season]

# Create the line Graph
plt.figure(figsize=(10, 6))
plt.plot(df_total["season"], df_total["goals"], marker="o", linewidth=2)

# Make some visual adjusts
plt.title("Total Goals by Season (Premier League)", fontsize=14)
plt.xlabel("Season")
plt.ylabel("Total Goals")
plt.xticks(rotation=45)
plt.grid(True, linestyle="--", alpha=0.6)

# Mostrar gráfico
plt.tight_layout()
plt.show()
