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

scheduler = BackgroundScheduler(timezone=utc)

class NbaMatchHandler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=utc)
        self.cred = credentials.Certificate("fanchat/backend/secrets/firebase_account_key.json")
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()

    def get_nba_season_url(self, season_year: str, season_type: str):
        request_url=f"http://api.sportradar.us/nba/trial/v7/en/games/{season_year}/{season_type}/schedule.json?api_key=kkth6h8yhnr698t7aq2esmqz"
        
        return request_url


    def get_nba_season(self, season_year: str, season_type: str):
        """Retrieve the current year's NBA season

        Args:
            season_year (str): current year
            season_type (str): REG or FINALS

        Returns:
            nba_season_df: full dataframe for the entire nba_season
        """
        current_season_url = self.get_nba_season_url(season_year=season_year,
                                                season_type=season_type)
        
        response = requests.get(current_season_url).json()
        
        nba_season_df = pd.DataFrame(response["games"])
            
        return nba_season_df
    
    def split_dict_column(self, df, column):
        """Splits columns that have dicts within them into multiple columns

        Args:
            df (pd.DataFrame): any dataframe
            column (str): column to explode

        Returns:
            _type_: exploded dataframe
        """
        df2 = pd.json_normalize(df[column])
        df.pop(column)
        df2.columns = [f"{column}_{col}" for col in df2.columns]
        return df2

    
    def check_df_for_dict(self, df):
        """Checks dataframe for dict 

        Args:
            df (pd.DataFrame): dataframe to check for dictionary

        Returns:
            _type_: _description_
        """
        for column in df.columns:
            if type(df[column][0]) == dict:
                df = pd.concat([df, self.split_dict_column(df, column)], axis=1)
        return df


    def get_nba_pbp_bs_url(match_id: str, 
                        req_type:str):

        request_url=f"http://api.sportradar.us/nba/trial/v7/en/games/{match_id}/{req_type}.json?api_key=kkth6h8yhnr698t7aq2esmqz"
        
        return request_url


    def get_nba_pbp_bs(self, match_id: str,
                    req_type: str):
        
        url = self.get_nba_pbp_bs_url(match_id=match_id,
                                        req_type=req_type)
        
        response = requests.get(url)
        time.sleep(1)
        response = url.json()
    
        return response


    def get_pbp_bs_list(self, daily_df, req_type):
        """
        This function takes in a Pandas DataFrame daily_df and a string req_type, and returns a DataFrame with the play-by-play and box score data for all in-progress matches. It does this by first creating an empty list pbp_bs_list, then filtering daily_df to only include rows where the status column is equal to "inprogress" and extracting the id column from this filtered DataFrame. It then iterates over the id values, calls the get_nba_pbp_bs function with each id value and req_type to get the play-by-play and box score data, and appends the response to pbp_bs_list. Finally, it creates a DataFrame from pbp_bs_list and passes it to the check_df_for_dict function to check for and explode dictionary columns, then returns the modified DataFrame.
        """
        pbp_bs_list = []
        inprogress_ids = daily_df[daily_df['status'] == 'inprogress']['id']
        for match_id in inprogress_ids:
            pbp_bs_list.append(self.get_nba_pbp_bs(match_id, req_type))
        df = pd.DataFrame(pbp_bs_list)
        return self.check_df_for_dict(df)


    def get_live_match_data(self, daily_df: pd.DataFrame):
        live_columns = ['id', 'clock', 'quarter', 'home_points', 'away_points']
        
        live_df = self.get_pbp_bs_list(daily_df=daily_df,
                        req_type='boxscore')
        
        live_df = live_df[live_df.columns.intersection(live_columns)]
        
        return live_df


    def get_daily_df(self, df:pd.DataFrame):
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
        live_df = self.get_live_match_data(daily_df)
        
        if not live_df.empty:
            daily_df.drop(['home_points', 'away_points'], axis=1, inplace=True)
            daily_df = pd.merge(daily_df, live_df, on='id', how='left')
            daily_df['quarter'] = daily_df['quarter'].apply(int).apply(str)
            if daily_df.isnull().values.any():
                print("NaN values present")
            else:
                daily_df['home_points'] = daily_df['home_points'].apply(int).apply(str)
                daily_df['away_points'] = daily_df['away_points'].apply(int).apply(str)
        else:
            print('No live dataframe')
        return daily_df

        
    def delete_collection(self, coll_ref, batch_size):
        docs = coll_ref.list_documents(page_size=batch_size)
        deleted_docs = []
        for doc in docs:
            print(f'Deleting doc {doc.id} => {doc.get().to_dict()}')
            deleted_docs.append(doc.id)
            doc.delete()
        if len(deleted_docs) >= batch_size:
            self.delete_collection(coll_ref, batch_size)

            
    def post_firebase(self, daily_df: pd.DataFrame):
        """posts list of matches as dicts into firebase

        Args:
            daily_df (pd.DataFrame): _description_
        """
        df_dict = daily_df.to_dict(orient='records')
        
        for record in df_dict:
            scheduled = record['scheduled']
            home_alias = record['home_alias']
            away_alias = record['away_alias']
            
            doc_ref = self.db.collection(u'nba_daily_matches').document(f'{scheduled}_{away_alias}_{home_alias}')
            doc_ref.set(record)
        
        print(df_dict)

    def nba_scheduler(self, daily_df: pd.DataFrame, coll_ref, batch_size: int):
        # delete_time = datetime.strptime(daily_df['scheduled'].iloc[0], '%Y-%m-%dT%H:%M:%SZ') + timedelta(minutes=18) 
        delete_time =  datetime.now(timezone.utc) + timedelta(seconds=2) 
        scheduler.add_job(self.delete_collection, 'date',run_date=delete_time, args=[coll_ref, batch_size])

        # post_time =  datetime.strptime(daily_df['scheduled'].iloc[0], '%Y-%m-%dT%H:%M:%SZ') + timedelta(minutes=19) 
        post_time =  datetime.now(timezone.utc) + timedelta(seconds=7) 
        scheduler.add_job(self.post_firebase, 'date',run_date=post_time, args=[daily_df])

        scheduler.start()

        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

        try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()