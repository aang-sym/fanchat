import boto3
import json
import logging
import os
import pytz
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ssm_client = boto3.client("ssm")
dynamodb = boto3.client('dynamodb')
event_bridge_client = boto3.client("events")

table_name = 'MatchTable'
               
def lambda_handler(event, context): 
    try:
        sport = event.get("sport")
        
        config_file_path = os.path.join(os.path.dirname(__file__), "config", f"{sport}_config.json")
        with open(config_file_path, "r") as config_file:
            sport_config = json.load(config_file)
        
        # Get API key from Parameter Store
        api_key_data = ssm_client.get_parameter(Name=sport_config["api_key_param"], WithDecryption=True)
        api_key = api_key_data["Parameter"]["Value"]
        print(f"API Key: {api_key}")
        if not api_key or api_key == "" or api_key == "update-this":
            return {
                'statusCode': 400,
                'body': json.dumps("You should set the API Key in the Parameter Store")
            }
        
        # Prepare today's date in the required format
        # game_date = datetime.now(pytz.timezone("America/Los_Angeles"))
        # game_year = game_date.strftime("%Y")
        # game_month = game_date.strftime("%m")
        # game_day = game_date.strftime("%d")
        
        # Prepare today's date if testing
        game_year = event['matches_year']
        game_month = event['matches_month']
        game_day = event['matches_day']
        print(f"Game day: {game_day}")
        
        # Construct URL for the API call
        games_url = sport_config["api_sport"]
        access_level = "trial"
        games_by_date_url = f"{access_level}/v7/en/games/{game_year}/{game_month}/{game_day}/schedule.json"
        games_by_date_url_with_key = f"{games_by_date_url}?api_key={api_key}"

        # Print the URL for logging
        print("Games By Date Url: ", games_url + games_by_date_url_with_key)

        # Get game data
        try:
            response = requests.get(games_url + games_by_date_url_with_key)
            response.raise_for_status()  # Check for HTTP errors
            
            if response.status_code == 200:
                payload = response.json()
                games = payload["games"]
                print(f"Games payload: {games[0]}")
            else:
                return {
                    'statusCode': response.status_code,
                    'body': json.dumps(f"HTTP Request failed with status code: {response.status_code}")
                }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error: {str(e)}')
            }
            
        field_mapping = sport_config['field_mapping']
        default_values = sport_config['default_values']
                
        for game in games:
            item = {}
            for field, field_info in field_mapping.items():
                value_mapping = field_info['field'].split('.')
                field_value = game
                for field_part in value_mapping:
                    field_value = field_value.get(field_part, {})

                field_type = field_info['type']
                default_value = default_values.get(field, '')

                if field_value or field_value == 0:  # Include 0 values as well
                    if field_type == 'S':
                        item[field] = {'S': str(field_value)}
                    elif field_type == 'N':
                        item[field] = {'N': str(field_value)}
                else:
                    if field_type == 'S':
                        item[field] = {'S': default_value}
                    elif field_type == 'N':
                        item[field] = {'N': str(default_value)}

            # Construct the MatchId based on the scheduled, home_alias, and away_alias fields
            match_id_value = f"{item['Date']['S']}_{item['HomeAlias']['S']}_{item['AwayAlias']['S']}"
            item['MatchId'] = {'S': match_id_value}

            response = dynamodb.put_item(
                TableName=table_name,
                Item=item
            )
            
            print('Item added successfully:', response)
            
            print(f"Game with Game ID: {game['id']} at {game['scheduled']}")
            game_datetime = datetime.strptime(game["scheduled"], "%Y-%m-%dT%H:%M:%S%z")
            game_month = game_datetime.month
            game_day = game_datetime.day
            game_hour = game_datetime.hour
            game_minute = game_datetime.minute
            
            # try:
            #     # Create a cron rule for EventBridge
            #     put_rule_response = event_bridge_client.put_rule(
            #         Name=event_bridge_rule_name,
            #         Description="Game start time rule to execute the state machine",
            #         ScheduleExpression=f"cron({game_minute} {game_hour} {game_day} {game_month} ? *)",
            #         State="ENABLED"
            #     )

            #     try:
            #         # Add target for the rule
            #         event_bridge_client.put_targets(
            #             Rule=event_bridge_rule_name,
            #             Targets=[
            #                 {
            #                     "Id": "SportsDataStateMachine",
            #                     "Arn": os.environ["STATE_MACHINE"],
            #                     "RoleArn": os.environ["STATE_MACHINE_EXECUTION_ROLE"],
            #                     "Input": json.dumps({
            #                         "gameId": game['id'],
            #                         "homeGame": game['home']['name'],
            #                         "apiKey": api_key
            #                     })
            #                 }
            #             ]
            #         )
            #     except Exception as e:
            #         print("Error occurred while adding target to EventBridge rule:", e)
            # except Exception as e:
            #     print("Error occurred while creating EventBridge rule:", e)
            
        return {
            'statusCode': 200,
            'body': json.dumps('Data posted to DynamoDB and EventBridge successfully')
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }