import json
import requests
import logger
import os
from config import Config
   
log = logger.Logger().logger

if __name__ == "__main__":

    #Create the path if it's not exist
    os.makedirs(Config.DATA, exist_ok=True)

    # specify the url of the advanced search results page
    headers = {'USER-AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

    #PL Seasons API URL
    url = "https://footballapi.pulselive.com/football/competitions/1/compseasons?page=0&pageSize=100"

    # send a GET request to the url and store the response
    response = requests.get(url, headers=headers, timeout=10)
    log.info("Response form Seasons API - OK")

    # create a object from the response content
    seasons = json.loads(response.text)

    seasons = seasons["content"]

    for season in seasons:
        #Setting the JSON filename for each season
        s = season["label"]
        s1 = s.replace("/", "-")
        #filename = s1 +".json"
        filename = os.path.join(Config.DATA, s1 + ".json")

        #Setting the pageSize first ranked on the first page.
        page = "0"
        pageSize = "500"
        id = str(season["id"])
        id = id[:-2]

        try:
            #Creating a JSON file
            fwrite = open(filename, 'w', encoding="utf-8")

            #Premier League Rank API URL
            url = "https://footballapi.pulselive.com/football/stats/ranked/players/goals?page="+page+"&pageSize="+pageSize+"&compSeasons="+id
            response = requests.get(url, headers=headers, timeout=10)
            log.info("Response form "+ s +" Ranking API - OK")
            
            # create a object from the response content
            goals = response.text
            #goals = json.loads(response.text)
            #goals = goals["stats"]["content"]

            #Writing the JSON file from API response
            fwrite.write("%s" % (goals))

        except(OSError, requests.exceptions.RequestException) as e:
            log.error("Response form "+ s +" Ranking API - ERROR")
            log.error(e)


        

        