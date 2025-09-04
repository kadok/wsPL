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

# Extract Country ISO names and codes
df["country"] = df["owner"].apply(lambda x: x.get("nationalTeam", {}).get("country", "Unknown"))
df["iso_code"] = df["owner"].apply(lambda x: x.get("nationalTeam", {}).get("isoCode", "Unknown"))


# Rename value column to goals
df = df.rename(columns={"value": "goals"})

# Group by ISO_CODE, sum the total of goals and add the country name column
country_goals = df.groupby('iso_code').agg(
    goals=('goals', 'sum'),
    country_name=('country', 'first')
).reset_index()

# Remove data with country names 'Unknown' or empty codes
country_goals = country_goals[country_goals['country_name'] != 'Unknown']
country_goals = country_goals[country_goals['iso_code'] != '']

# Sort by number of goals descending order
country_goals = country_goals.sort_values(by="goals", ascending=False)
country_goals = country_goals.reset_index(drop=True)
country_goals['rank'] = country_goals.index + 1

# Create HTML code
html_output = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premier League Goals per Country</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            background-color: #f4f7f6;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            padding: 20px;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            padding: 30px;
            width: 100%;
            max-width: 600px;
        }}
        h1 {{
            text-align: center;
            color: #1a237e;
            font-weight: 700;
            margin-bottom: 30px;
        }}
        .country-item {{
            display: flex;
            align-items: center;
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 12px;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}
        .country-item:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
        }}
        .rank {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #4caf50;
            margin-right: 20px;
            width: 30px;
            text-align: center;
        }}
        .flag {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid #fff;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            margin-right: 15px;
        }}
        .country-info {{
            flex-grow: 1;
        }}
        .country-name {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #2e7d32;
        }}
        .goals {{
            font-size: 1.1rem;
            color: #555;
            font-weight: 400;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Premier League Goals per Country</h1>
        <ul>
"""

for index, row in country_goals.iterrows():
    flag_url = f"https://flagcdn.com/w1280/{row['iso_code'].lower()}.png"
    html_output += f"""
        <div class="country-item">
            <span class="rank">{row['rank']}</span>
            <img class="flag" src='{flag_url}' alt='{row['country_name']} flag'>
            <div class="country-info">
                <div class="country-name">{row['country_name']}</div>
                <div class="goals">{int(row['goals'])} goals</div>
            </div>
        </div>
    """

html_output += """
        </ul>
    </div>
</body>
</html>
"""

# Save the HTML file
with open("PremierLeague_Goals_Ranking.html", "w", encoding="utf-8") as file:
    file.write(html_output)

print("Ranking generated!")
