from datetime import date, datetime, timedelta
import re
import time
from dateutil import parser
import requests
import secrets
import pandas as pd

def get_nba_season_url(season_year: str,
                        season_type: str
                        ):

    request_url=f"http://api.sportradar.us/nba/trial/v7/en/games/{season_year}/{season_type}/schedule.json?api_key=kkth6h8yhnr698t7aq2esmqz"
    
    return request_url

def get_nba_season(season_year: str, 
                   season_type: str):
    current_season = get_nba_season_url(season_year=season_year,
                                        season_type=season_type)
    response = requests.get(current_season)
    nba_response = response.json()
    
    nba_df = pd.DataFrame(nba_response["games"])
        
    return nba_df

def get_nba_pbp_bs_url(match_id: str, 
                       req_type:str):

    request_url=f"http://api.sportradar.us/nba/trial/v7/en/games/{match_id}/{req_type}.json?api_key=kkth6h8yhnr698t7aq2esmqz"
    
    return request_url

def get_nba_pbp_bs(match_id: str,
                   req_type: str):
    
    pbp_bs_url = get_nba_pbp_bs_url(match_id=match_id,
                                    req_type=req_type)
    
    url_response = requests.get(pbp_bs_url)
    time.sleep(1)
    response = url_response.json()
 
    return response

def split_dict_column(df, column: str):
    df2 = pd.json_normalize(df[column])
    
    df.pop(column)
    
    df2_list = list(df2.columns)
    new_list = []
    
    for value in df2_list:
        value = f"{column}_{value}"        
        new_list.append(value)
    
    df2.columns = new_list
    
    return df2

def check_df_for_dict(df):
    for column in df.columns:
        if type(df[column][0]) == dict:
            add_df = split_dict_column(df, column)
            df = pd.concat([df, add_df], axis=1)
    
    return df

def get_daily_df(df):
    today_date = date.today()
    yesterday_date = today_date + timedelta(days=-1)
    
    today_date_iso = f"{today_date.isoformat()}T12:00:00:000Z"
    yesterday_date_iso = f"{yesterday_date.isoformat()}T12:00:00:000Z"
    
    daily_df = df[(df['scheduled'] > yesterday_date_iso) & (df['scheduled'] <= today_date_iso)]
    
    return daily_df
        
def get_pbp_bs_list(daily_df, 
                    req_type=str):
    pbp_bs_list = []

    inprogress_df = daily_df[daily_df['status'] == 'closed']['id'] # daily_df[daily_df['status'] == 'inprogress']['id']
    for match_id in inprogress_df:
        pbp_response = get_nba_pbp_bs(match_id=match_id,
                                      req_type=req_type)
        pbp_bs_list.append(pbp_response)
    
    df = pd.DataFrame(pbp_bs_list) 
    
    df = check_df_for_dict(df)
         
    return df

def get_live_match_data(daily_df):
    live_columns = ['id', 'status', 'scheduled', 'clock', 'quarter',
                    'home_name', 'home_points', 'away_name',
                    'away_points']
    
    get_pbp_bs_list(daily_df=nba_daily_df,
                    req_type='boxscore')
    
    live_df = daily_df[daily_df.columns.intersection(live_columns)]
    
    return live_df

season_year = "2022"
season_type = "REG"

nba_df = get_nba_season(season_year=season_year,
                          season_type=season_type)

nba_season_df = check_df_for_dict(nba_df)

match_columns = ['id', 'status', 'scheduled','venue_name', 
                 'home_name', 'home_alias', 'home_points', 
                 'away_name', 'away_alias', 'away_points',]

nba_season_df = nba_season_df[nba_season_df.columns.intersection(match_columns)]

nba_daily_df = get_daily_df(nba_season_df)

daily_live_df = get_live_match_data(nba_daily_df)

print(nba_season_df)