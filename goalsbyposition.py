import pandas as pd
from pymongo import MongoClient
import json
from config import Config

# Connect to MongoDB
client = MongoClient(Config.DB_LINK)
db = client[Config.DATABASE]
collection = db[Config.COLLECTION]

# List all registers
docs = list(collection.find({}, {"season": 1, "owner.nationalTeam": 1, "owner.info.position": 1, "value": 1, "_id": 0}))

# Convert to Dataframe
df = pd.DataFrame(docs)


# Normalizing positions
position_map = {
    "G": "GK",
    "D": "DEF",
    "M": "MID",
    "F": "FWD"
}

# Fixing the unknown data
def get_country(owner):
    return owner.get("nationalTeam", {}).get("country", "Unknown")

def get_position(owner):
    return owner.get("info", {}).get("position", "Unknown")

df["country"] = df["owner"].apply(get_country)
df["position"] = df["owner"].apply(get_position)

# Rename value column to goals
df = df.rename(columns={"value": "goals"})

#Normalize Postions
df["position"] = df["owner"].apply(get_position).map(position_map).fillna("Unknown")

# Filter: Ignore Unknown Country and Position
df = df[(df['country'] != "Unknown") & (df['position'] != "Unknown")]


last_season = df["season"].iloc[-1]
df = df[df["season"] != last_season]

# Group by season, country and position (goals sum)
df_grouped = df.groupby(['season', 'country', 'position'])['goals'].sum().reset_index()

# Sort the seasons (Ascending)
df_grouped['season_year'] = df_grouped['season'].str[:4].astype(int)


# Create a fixed list to seasons and positions
all_seasons = sorted(df_grouped['season'].unique().tolist())
all_positions = sorted(df_grouped['position'].unique().tolist())
all_countries = sorted(df_grouped['country'].unique().tolist())

# Create a complete grid (All combinations)
full_index = pd.MultiIndex.from_product(
    [all_seasons, all_countries, all_positions],
    names=['season', 'country', 'position']
)

# Fixing sort
df_grouped['season_year'] = df_grouped['season'].str[:4].astype(int)
df_grouped = df_grouped.sort_values(by=['country', 'season_year', 'position'])

# Get the unique country list to the dropdown
countries = all_countries

# Convert the DataFrame to JSON
json_data = df_grouped.to_json(orient='records')

file_name = "test.json"
with open(file_name, "w", encoding="utf-8") as file:
    file.write(json_data)

# Generate HTML
html_content = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premier League: Goals by Position</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Inter', sans-serif;
        }}
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-4xl">
        <h1 class="text-3xl font-bold text-center mb-6 text-gray-800">Goals by Position (Premier League)</h1>
        
        <div class="mb-6 flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <label for="country-select" class="text-lg font-medium text-gray-700">Select the Country:</label>
            <select id="country-select" class="p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {"".join(f'<option value="{c}">{c}</option>' for c in countries)}
            </select>
        </div>
        
        <div id="chart-container" class="w-full">
            <div id="line-chart" class="w-full h-96"></div>
        </div>
    </div>

    <script>
        const allData = {json_data};
        const countrySelect = document.getElementById('country-select');
        const chartDiv = document.getElementById('line-chart');

        // Fixed Seasons list
        const allSeasons = [...new Set(allData.map(d => d.season))].sort();
        const allPositions = [...new Set(allData.map(d => d.position))].sort();

        // Positions order
        const positionOrder = ['GK', 'DEF', 'MID', 'FWD'];

        // Fixed Colors Map
        const positionColors = {{
            'GK': '#1f77b4',   // blue
            'DEF': '#2ca02c',  // green
            'MID': '#ff7f0e',  // orange
            'FWD': '#d62728'   // red
        }};

        function drawChart(country) {{
            const filteredData = allData.filter(d => d.country === country);
            
            //const positions = [...new Set(filteredData.map(d => d.position))];
            
            const traces = allPositions.map(pos => {{
                const posData = filteredData.filter(d => d.position === pos);
                return {{
                    x: allSeasons,
                    y: allSeasons.map(season => {{
                        const found = posData.find(d => d.season === season);
                        return found ? found.goals : 0;
                    }}),
                    mode: 'lines+markers',
                    name: pos,
                    connectgaps: false,
                    line: {{
                        color: positionColors[pos] || "#999999" // fallback cinza
                    }},
                    marker: {{
                        color: positionColors[pos] || "#999999"
                    }}
                }};
            }});

            const layout = {{
                title: `Goals by Position -  ${{country}}`,
                xaxis: {{
                    title: 'Season',
                    type: 'category',
                    automargin: true,
                    categoryorder: 'array',
                    categoryarray: allSeasons
                }},
                yaxis: {{
                    title: 'Goals',
                    automargin: true
                }},
                legend: {{
                    title: {{
                        text: 'Position'
                    }}
                }}
            }};

            Plotly.newPlot(chartDiv, traces, layout);
        }}

        // Initialize the first country alphabetically
        const countries = [...new Set(allData.map(d => d.country))];
        if (countries.length > 0) {{
            drawChart(countries[0]);
        }}

        // Change Country Event
        countrySelect.addEventListener('change', (event) => {{
            drawChart(event.target.value);
        }});
    </script>
</body>
</html>
"""

# Save the HTML file
file_name = "goals_by_position_interactive.html"
with open(file_name, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"Interactive Graph generated! Check the file '{file_name}' in your path.")
