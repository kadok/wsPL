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

# Group by Country and sum the goals
country_goals = df.groupby("country")["goals"].sum().reset_index()

# Printing the dataframe to verification
print("Total de gols por país:")
print(country_goals.to_string())

# Create the interactive world map using plotly
fig = px.choropleth(
    country_goals,
    locations="country",
    locationmode="country names",
    color="goals",
    hover_name="country",
    color_continuous_scale=px.colors.sequential.Plasma,
    title="Premier League: Total of Goals per Country",
    labels={'goals':'Total of Goals'}
)

# Save the graph on HTML file
fig.write_html("PremierLeague_Goals_WorldMap.html")

print("Map generated!")