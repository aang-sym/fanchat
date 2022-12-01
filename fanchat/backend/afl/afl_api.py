import requests
import secrets

def retrieve_season(season_url: str) -> str:
    split_url = season_url.split("/")
    currentSeason = split_url[8]
    
    return currentSeason

api_url = "http://api.sportradar.us/australianrules/trial/v3/en/seasons/sr:season:87642/info.json?api_key=rd8ftkfvpbemp9jucnhadd2k"

currentSeason = retrieve_season(api_url)
response = requests.get(api_url)
api_response = response.json()

afl_team_list = api_response["stages"][0]["groups"][0]["competitors"]
afl_team_dict_total = {}

for afl_team in afl_team_list:
        afl_team_dict = {
            afl_team["abbreviation"] : {
                "id": afl_team["id"],
                "name": afl_team["name"]
            }
        }
        
        afl_team_dict_total.update(afl_team_dict)
    
print(afl_team_list)

# def afl_team_list(team_list: dict) -> dict: