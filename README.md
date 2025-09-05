# Premier League Top Scorer

This repo contains the source code that consumes the Premier League stats API receiving JSON season files with goals stats from each player, since the League creation, 1992-93. And store these JSON season files into a non-relational database, MongoDB. After insert seasons data in MongoDB, creating queries calculating the cumulate numbers of goals of each player through all seasons, until the 2024-25 season.

Data Source: https://www.premierleague.com/en


## Getting Started

1. Install MongoDB
https://www.mongodb.com/docs/manual/installation/


2. Create a virtual environment(Virtualenv (venv))

```bash
python3 -m venv .venv
#Linux
source .venv/bin/activate
#Windows
.\.venv\Scripts\activate
```

3. Install project requirements

```bash
pip install -r requirements.txt
```


4. Copy the .env.example file rename to `.env` in the root directory and define the environment variables:

```.env
DB_LINK=<YOUR_MONGODB_LINK>
DATABASE=<YOUR_DATABASE_NAME>
COLLECTION=<YOUR_COLLECTION_NAME>
DATA=<YOUR_CSV_PATH>
```

## Running

1. First we need to get the data from Premier League website beyond their API and store into CSV files.

```bash
python parserjson.py
```

2. After get the data we store those CVS data into a MongoDB.

```bash
python dbinsert.py
```

3. Generate a video with the statistics of the Premier League Top Scorer of all time.

```bash
python topscorer.py
```

![Bar](images/bar.png?raw=true)



## Others Statistics

1. Generate Goals by Country - Map

```bash
python goalsmap.py
```

![Map](images/map.png?raw=true)


2. Generate Goals by Country - List

```bash
python goalsbycountrylist.py
```

![List](images/list.png?raw=true)


3. Generate Goals by Country - Polar Histogram

```bash
python goalsbycountry.py
```

![Polar Histogram](images/polar.png?raw=true)


4. Generate Goals by Position

```bash
python goalsbyposition.py
```


5. Generate Goals by Season

```bash
python goalsbyseason.py
```

## Future Additions

- **Instead using MongoDB use Pandas consuming the CSV files**
- **Speedup the video processing using CUDA**