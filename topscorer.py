import pandas as pd
from pymongo import MongoClient
import bar_chart_race as bcr
from config import Config

#Connect to MongoDB
client = MongoClient(Config.DB_LINK) 
db = client[Config.DATABASE]
collection = db[Config.COLLECTION]

# Search all registers
docs = list(collection.find({}, {"season": 1, "owner.name.display": 1, "value": 1, "_id": 0}))

# List all the seasons
seasons = collection.distinct("season")

# Covert to Dataframe
df = pd.DataFrame(docs)

# Extract player names correctly
df["player"] = df["owner"].apply(lambda x: x["name"]["display"])

# Rename value column to goals
df = df.rename(columns={"value": "goals"})

# Build a pivot table
pivot = df.pivot_table( index="season", columns="player", values="goals", aggfunc="sum").fillna(0)

# Sort the seasons
pivot = pivot.sort_index()

# Accumulate the goals sum per season
pivot_cumulative = pivot.cumsum()


# Prolonging the last frame
extra_frames = 2

# Getting the last line
last_row = pivot_cumulative.iloc[[-1]]

# Repeating the last line
for i in range(extra_frames):
    last_row.index = [f"{last_row.index[0]}"]
    pivot_cumulative = pd.concat([pivot_cumulative, last_row])


# Create the Animated Graph
bcr.bar_chart_race(
    df=pivot_cumulative,
    filename="Top20_h.mp4",
    title="Premier League Top 20 Scorers",
    n_bars=20,
    fixed_order=False,
    fixed_max=True,
    steps_per_period=40,
    period_length=2000,
    figsize=(6, 10.67),
    dpi=200
)