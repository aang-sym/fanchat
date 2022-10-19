import requests
import secrets
import pandas as pd

def generate_nba_season(season_year: str,
                        season_type: str
                        ):

    request_url=f"http://api.sportradar.us/nba/trial/v7/en/games/{season_year}/{season_type}/schedule.json?api_key=kkth6h8yhnr698t7aq2esmqz"
    
    return request_url

season_year = "2022"
season_type = "REG"

current_season = generate_nba_season(season_year=season_year,
                                     season_type=season_type)
response = requests.get(current_season)
response_json = response.json()

# season_dict = {}

# def generate_season_dict(all_dict: dict):
#     for match_id in all_dict['games'].values():
#         match_dict = {
#             'id': [id]
#         } 

df = pd.DataFrame(response_json["games"])

def split_dict_column(df, column: str):
    df2 = pd.json_normalize(df[column])
    
    df2_list = list(df2.columns)
    
    for column_name in df2_list:
        for i in range(len(df2_list)):
            column_name = f"{column}_{df2_list[0][i]}"
    
    return df2

venue_df = split_dict_column(df, "venue")
home_df = split_dict_column(df, "home")
away_df = split_dict_column(df, "away")

df.drop(['coverage', 'track_on_court', 'reference'], axis=1, inplace=True)  
column_list = list(df.columns)

print(df)