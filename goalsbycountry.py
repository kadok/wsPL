import pandas as pd
from pymongo import MongoClient
import plotly.express as px
from config import Config

#Connect to MongoDB
client = MongoClient(Config.DB_LINK)
db = client[Config.DATABASE]
collection = db[Config.COLLECTION]

# List all registers
docs = list(collection.find({}, {"owner.nationalTeam": 1, "value": 1, "_id": 0}))

# Convert to Dataframe
df = pd.DataFrame(docs)

# Normalization Dictionary to country names
country_normalization_map = {
    "England": "United Kingdom",
    "United Kingdom": "United Kingdom",
    "GB-ENG": "England",
    "Wales": "Wales",
    "Scotland": "Scotland",
    "Northern Ireland": "Northern Ireland"
}

# Extract and normalize the country names
df["country"] = df["owner"].apply(lambda x: x.get("nationalTeam", {}).get("country", "Unknown"))
df["country"] = df["country"].apply(lambda x: country_normalization_map.get(x, x))

# Rename value column to goals
df = df.rename(columns={"value": "goals"})

# Agrupar por país e somar o total de gols
country_goals = df.groupby("country")["goals"].sum().reset_index()

# Printing the dataframe to verification
print("Total of goals per country:")
print(country_goals.to_string())

# Sort by number of goals descending order
country_goals = country_goals.sort_values(by="goals", ascending=False)

# Create Polar Histogram
# 'r' = Histogram Radius (goals value) and 'theta' =  angle (country name).
fig = px.bar_polar(
    country_goals, 
    r="goals", 
    theta="country",
    color="country", # colors per country
    title="Premier League: Goals per Country (Polar Histogram)",
    color_discrete_sequence=px.colors.sequential.Plasma_r,
    labels={'r':'Total of Goals', 'theta':'Country'}
)

# Save the graph on HTML file
fig.write_html("PremierLeague_Polar_Histogram.html")

print("Polar Histogram generated!")
