import pandas as pd
from pymongo import MongoClient
import json
from config import Config

# Connect to MongoDB
client = MongoClient(Config.DB_LINK)
db = client[Config.DATABASE]
collection = db[Config.COLLECTION]

# List all registers
docs = list(collection.find({}, {
    "season": 1,
    "owner.nationalTeam": 1,
    "owner.name.display": 1,
    "value": 1,
    "_id": 0
}))

# Convert to DataFrame
df = pd.DataFrame(docs)

# --- Extract fields ---
def get_country(owner):
    return owner.get("nationalTeam", {}).get("country", "Unknown")

def get_player_name(owner):
    return owner.get("name", {}).get("display", "Unknown")

df["country"] = df["owner"].apply(get_country)
df["player"] = df["owner"].apply(get_player_name)
df = df.rename(columns={"value": "goals"})

# Remove Unknowns
df = df[(df['country'] != "Unknown") & (df['player'] != "Unknown")]

# Group by season, country and player
df_grouped = (
    df.groupby(['season', 'country', 'player'])['goals']
    .sum()
    .reset_index()
)

# Sort
df_grouped['season_year'] = df_grouped['season'].str[:4].astype(int)
df_grouped = df_grouped.sort_values(by=['country', 'season_year', 'goals'], ascending=[True, True, False])

# Get fixed lists
all_seasons = sorted(df_grouped['season'].unique().tolist())
all_countries = sorted(df_grouped['country'].unique().tolist())

# Convert to JSON
json_data = df_grouped.to_json(orient='records')

# --- HTML ---
html_content = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premier League: Goals by Player</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Inter', sans-serif;
        }}
        .btn {{
            @apply px-4 py-2 rounded-md font-semibold border border-gray-300 hover:bg-gray-200 transition;
        }}
        .btn-active {{
            background-color: #2563eb;
            color: white;
            border-color: #2563eb;
        }}
        input[type=range] {{
            width: 100%;
        }}
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-5xl">
        <h1 class="text-3xl font-bold text-center mb-6 text-gray-800">
            Premier League: Goals by Player
        </h1>

        <!-- Filters -->
        <div class="mb-6 flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <label for="country-select" class="text-lg font-medium text-gray-700">Select the Country:</label>
            <select id="country-select" class="p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {"".join(f'<option value="{c}">{c}</option>' for c in all_countries)}
            </select>
        </div>

        <!-- Options buttons -->
        <div class="flex justify-center mb-4 space-x-4">
            <button id="total-btn" class="btn btn-active">🏆 History of All Seasons</button>
            <button id="season-btn" class="btn">📅 Season</button>
        </div>

        <!-- Slider -->
        <div id="slider-container" class="hidden mb-6 text-center">
            <label for="season-slider" class="font-medium text-gray-700">Choose a Season:</label>
            <input type="range" id="season-slider" min="0" max="{len(all_seasons)-1}" value="{len(all_seasons)-1}" step="1">
            <div id="season-label" class="mt-2 font-semibold text-blue-700">{all_seasons[-1]}</div>
        </div>

        <div id="chart-container" class="w-full">
            <div id="bar-chart" class="w-full h-[600px]"></div>
        </div>
    </div>

    <script>
        const allData = {json_data};
        const chartDiv = document.getElementById('bar-chart');
        const countrySelect = document.getElementById('country-select');
        const totalBtn = document.getElementById('total-btn');
        const seasonBtn = document.getElementById('season-btn');
        const sliderContainer = document.getElementById('slider-container');
        const seasonSlider = document.getElementById('season-slider');
        const seasonLabel = document.getElementById('season-label');

        const allSeasons = {json.dumps(all_seasons)};
        let currentMode = 'total'; // total or season
        let currentSeasonIndex = allSeasons.length - 1;

        function drawChart(country) {{
            const filteredData = allData.filter(d => d.country === country);
            const latestSeason = allSeasons[currentSeasonIndex];
            let dataToUse;

            if (currentMode === 'total') {{
                const totals = {{}};
                filteredData.forEach(d => {{
                    totals[d.player] = (totals[d.player] || 0) + d.goals;
                }});
                dataToUse = Object.entries(totals)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 20)
                    .map(([player, goals]) => ({{ player, goals }}));
            }} else {{
                const seasonData = filteredData.filter(d => d.season === latestSeason);
                dataToUse = seasonData
                    .sort((a, b) => b.goals - a.goals)
                    .slice(0, 20)
                    .map(d => ({{ player: d.player, goals: d.goals }}));
            }}

            const players = dataToUse.map(d => d.player + '   ');
            const goals = dataToUse.map(d => d.goals);

            const trace = {{
                x: goals.reverse(),
                y: players.reverse(),
                type: 'bar',
                orientation: 'h',
                marker: {{ color: currentMode === 'total' ? '#1f77b4' : '#ff7f0e' }}
            }};

            const title = currentMode === 'total'
                ? `Top 20 (${{country}}) Players - History of All Seasons`
                : `Top 20 (${{country}}) Players - Season ${{latestSeason-1}}-${{latestSeason}}`;

            const layout = {{
                title,
                xaxis: {{ title: 'Goals' }},
                yaxis: {{ automargin: true}},
                margin: {{ l: 200, r: 50, t: 80, b: 50 }}
            }};

            Plotly.newPlot(chartDiv, [trace], layout);
        }}

        // Buttons
        function setActiveButton(button) {{
            totalBtn.classList.remove('btn-active');
            seasonBtn.classList.remove('btn-active');
            button.classList.add('btn-active');
        }}

        totalBtn.addEventListener('click', () => {{
            currentMode = 'total';
            sliderContainer.classList.add('hidden');
            setActiveButton(totalBtn);
            drawChart(countrySelect.value);
        }});

        seasonBtn.addEventListener('click', () => {{
            currentMode = 'season';
            sliderContainer.classList.remove('hidden');
            setActiveButton(seasonBtn);
            drawChart(countrySelect.value);
        }});

        // Slider
        seasonSlider.addEventListener('input', (e) => {{
            currentSeasonIndex = parseInt(e.target.value);
            seasonLabel.textContent = allSeasons[currentSeasonIndex];
            if (currentMode === 'season') {{
                drawChart(countrySelect.value);
            }}
        }});

        // Initializing
        const countries = [...new Set(allData.map(d => d.country))];
        if (countries.length > 0) {{
            drawChart(countries[0]);
        }}

        // Change Country
        countrySelect.addEventListener('change', (e) => {{
            drawChart(e.target.value);
        }});
    </script>
</body>
</html>
"""

# Salvar HTML
file_name = "players_goals_by_country.html"
with open(file_name, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"✅ Interactive Graph generated! Check '{file_name}' in your path.")
