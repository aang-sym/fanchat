from datetime import date, datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
import os
import re
import time
import schedule
from dateutil import parser
import requests
import secrets
import pandas as pd
from pytz import utc

import firebase_admin
from firebase_admin import credentials, db, firestore

cred = credentials.Certificate("fanchat/backend/secrets/firebase_account_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

scheduler = BackgroundScheduler(timezone=utc)

def get_nba_season_url(season_year: str, season_type: str):
    request_url=f"http://api.sportradar.us/nba/trial/v7/en/games/{season_year}/{season_type}/schedule.json?api_key=kkth6h8yhnr698t7aq2esmqz"
    
    return request_url


def get_nba_season(season_year: str, season_type: str):
    """Retrieve the current year's NBA season

    Args:
        season_year (str): current year
        season_type (str): REG or FINALS

    Returns:
        nba_season_df: full dataframe for the entire nba_season
    """
    current_season_url = get_nba_season_url(season_year=season_year,
                                            season_type=season_type)
    
    response = requests.get(current_season_url).json()
    
    nba_season_df = pd.DataFrame(response["games"])
        
    return nba_season_df


def split_dict_column(df: pd.DataFrame, column: str):
    """Splits columns that have dicts within them into multiple columns

    Args:
        df (pd.DataFrame): any dataframe
        column (str): column to explode

    Returns:
        _type_: exploded dataframe
    """
    df2 = pd.json_normalize(df[column])
    
    df.pop(column)
    
    df2_list = list(df2.columns)
    new_list = []
    
    for value in df2_list:
        value = f"{column}_{value}"        
        new_list.append(value)
    
    df2.columns = new_list
    
    return df2


def check_df_for_dict(df: pd.DataFrame):
    """Checks dataframe for dict 

    Args:
        df (pd.DataFrame): dataframe to check for dictionary

    Returns:
        _type_: _description_
    """
    for column in df.columns:
        if type(df[column][0]) == dict:
            add_df = split_dict_column(df, column)
            df = pd.concat([df, add_df], axis=1)
    
    return df


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


def get_pbp_bs_list(daily_df, 
                    req_type=str):
    pbp_bs_list = []

    inprogress_df = daily_df[daily_df['status'] == 'inprogress']['id']
    for match_id in inprogress_df:
        pbp_response = get_nba_pbp_bs(match_id=match_id,
                                      req_type=req_type)
        pbp_bs_list.append(pbp_response)
    
    df = pd.DataFrame(pbp_bs_list) 
    
    df = check_df_for_dict(df)
         
    return df


def get_live_match_data(daily_df: pd.DataFrame):
    live_columns = ['id', 'clock', 'quarter', 'home_points', 'away_points']
    
    live_df = get_pbp_bs_list(daily_df=daily_df,
                    req_type='boxscore')
    
    live_df = live_df[live_df.columns.intersection(live_columns)]
    
    return live_df

def get_daily_df(df:pd.DataFrame):
    """retrieve's today's matches

    Args:
        df (pd.DataFrame): df to retrieve daily matches for

    Returns:
        _type_: _description_
    """

    today_date = date.today()
    yesterday_date = today_date + timedelta(days=-1)
    
    today_date_iso = f"{today_date.isoformat()}T12:00:00:000Z"
    yesterday_date_iso = f"{yesterday_date.isoformat()}T12:00:00:000Z"
    
    daily_df = df[(df['scheduled'] > yesterday_date_iso) & (df['scheduled'] <= today_date_iso)]
    live_df = get_live_match_data(daily_df=daily_df)
    
    if live_df.empty:
        print('No live dataframe')
    else:
        daily_df.drop(['home_points', 'away_points'], axis=1, inplace=True)
        daily_df =  pd.merge(daily_df, live_df, on='id', how='left')
    
    if daily_df.isnull().values.any():
        print("NaN values present")
    else:
        daily_df['home_points'] = daily_df['home_points'].apply(int).apply(str)
        daily_df['away_points'] = daily_df['away_points'].apply(int).apply(str)

    return daily_df

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.get().to_dict()}')
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)
   
        
def post_firebase(daily_df: pd.DataFrame):
    """posts list of matches as dicts into firebase

    Args:
        daily_df (pd.DataFrame): _description_
    """
    df_dict = daily_df.to_dict(orient='records')
    
    for record in df_dict:
        scheduled = record['scheduled']
        home_alias = record['home_alias']
        away_alias = record['away_alias']
        
        doc_ref = db.collection(u'nba_daily_matches').document(f'{scheduled}_{away_alias}_{home_alias}')
        doc_ref.set(record)
    
    print(df_dict)

def nba_scheduler(daily_df: pd.DataFrame, coll_ref, batch_size):
    # delete_time = datetime.strptime(daily_df['scheduled'].iloc[0], '%Y-%m-%dT%H:%M:%SZ') + timedelta(minutes=18) 
    delete_time =  datetime.now(timezone.utc) + timedelta(seconds=10) 
    scheduler.add_job(delete_collection, 'date',run_date=delete_time, args=[coll_ref, batch_size])

    # post_time =  datetime.strptime(daily_df['scheduled'].iloc[0], '%Y-%m-%dT%H:%M:%SZ') + timedelta(minutes=19) 
    post_time =  datetime.now(timezone.utc) + timedelta(seconds=20) 
    scheduler.add_job(post_firebase, 'date',run_date=post_time, args=[daily_df])

    scheduler.start()

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()


def start_load():
    current_year = str(datetime.now().year)
    season_type = "REG"
    match_columns = ['id', 'status', 'scheduled','venue_name', 
                    'home_name', 'home_alias', 'home_points', 
                    'away_name', 'away_alias', 'away_points',]
    
    firestore_ref = db.collection(u'nba_daily_matches')
    
    nba_sport_df = get_nba_season(season_year=current_year,
                            season_type=season_type)

    nba_season_df = check_df_for_dict(df=nba_sport_df)

    nba_season_df = nba_season_df[nba_season_df.columns.intersection(match_columns)]

    nba_daily_df = get_daily_df(df=nba_season_df)
    
    nba_scheduler(daily_df=nba_daily_df, coll_ref = firestore_ref, batch_size=1)

    print(nba_daily_df)


if __name__ == "__main__":
    start_load()