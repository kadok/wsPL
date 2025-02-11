import requests
from bs4 import BeautifulSoup
import argparse

class Player :
    def __init__(self, rank, name, badge, club, flag, nationality, goals):
        self.rank = rank
        self.name = name
        self.badge = badge
        self.club = club
        self.flag = flag
        self.nationality = nationality
        self.goals = goals

    def __repr__(self): 
        return f"{self.rank} {self.name} {self.badge} {self.club} {self.flag} {self.nationality} {self.goals}" 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    args = parser.parse_args()


    # specify the url of the advanced search results page

    headers = {'USER-AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

    url = "https://www.premierleague.com/stats/top/players/goals?se=418"
    #url = args.url

    # send a GET request to the url and store the response
    #response = requests.get(url)

    response = requests.get(url, headers=headers, timeout=10)

    # create a BeautifulSoup object from the response content
    soup = BeautifulSoup(response.content, "html.parser")

    # find the table on the page that contains the search results
    table = soup.find("tbody", class_="statsTableContainer")

    players = []


    # iterate over each row in the table
    for row in table.find_all("tr", class_=['table__row']):
        
        nationality = []
        
        #Rank, Name, Badge, Club, Flag, Nationality, and Goals.
        #if (row.find("table", class_="inline-table")) :
        rank = row.find_next("td", class_="stats-table__rank")
        rank = rank.text.strip()
        print(rank)

        name = row.find_next("a", class_="playerName")
        name = name.text.strip()
        print(name)

        badge = row.find_next("img", class_="badge-image").get("src")
        print(badge)
        club = row.find_next("a", class_="stats-table__cell-icon-align")
        club = club.text.strip()
        print(club)


        #nationality = row.find_next(class_="stats-table__cell-icon-align")
        nationality = row.find_next("div", class_="stats-table__cell-icon-align")
        flag = row.find_next("img", class_="stats-table__flag-icon").get("src")
        print(flag)
        nationality = nationality.find_next("span", class_="stats__player-country")
        nationality = nationality.text.strip()
        print(nationality)
        


        goals = row.find_next("td", class_="stats-table__main-stat")
        goals = goals.text.strip()
        print(goals)


        players.append(Player(rank,name,badge,club,flag,nationality,goals))


    fwrite = open(args.output, 'w', encoding="utf-8")

    for player in players:
        #print(f"""{player.name} {player.age} - {flag}\n{player.position}\n{player.team}\n""")
        fwrite.write("%s;%s;%s;%s;%s;%s;%s\n" % (player.rank, player.name, player.badge, player.club,  player.flag, player.nationality, player.goals))