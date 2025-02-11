import json
import requests
   

if __name__ == "__main__":

    # specify the url of the advanced search results page
    headers = {'USER-AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

    #PL Seasons API URL
    url = "https://footballapi.pulselive.com/football/competitions/1/compseasons?page=0&pageSize=100"

    # send a GET request to the url and store the response
    response = requests.get(url, headers=headers, timeout=10)

    # create a object from the response content
    seasons = json.loads(response.text)

    seasons = seasons["content"]

    for season in seasons:
        #Creating JSON file for each Season
        s = season["label"]
        s1 = s.replace("/", "-")
        filename = s1 +".json"
        fwrite = open(filename, 'w', encoding="utf-8")

        page = "0"
        pageSize = "25"
        id = str(season["id"])
        id = id[:-2]

        #PL Rank API URL
        url = "https://footballapi.pulselive.com/football/stats/ranked/players/goals?page="+page+"&pageSize="+pageSize+"&compSeasons="+id
        response = requests.get(url, headers=headers, timeout=10)
        
        # create a object from the response content
        goals = json.loads(response.text)
        goals = goals["stats"]["content"]

        fwrite.write("%s" % (goals))