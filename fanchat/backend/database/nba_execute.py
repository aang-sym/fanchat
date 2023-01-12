from nba_class import NbaMatchHandler
from firebase_admin import credentials, db, firestore

nba = NbaMatchHandler()
db = firestore.client()
    
current_year = "2022"
season_type = "REG"
match_columns = ['id', 'status', 'scheduled','venue_name', 
                'home_name', 'home_alias', 'home_points', 
                'away_name', 'away_alias', 'away_points',]

firestore_ref = db.collection(u'nba_daily_matches')

nba_sport_df = nba.get_nba_season(season_year=current_year,
                        season_type=season_type)

nba_season_df = nba.check_df_for_dict(df=nba_sport_df)

nba_season_df = nba_season_df[nba_season_df.columns.intersection(match_columns)]

nba_daily_df = nba.get_daily_df(df=nba_season_df)

nba.nba_scheduler(daily_df=nba_daily_df, coll_ref = firestore_ref, batch_size=1)

print(nba_daily_df)