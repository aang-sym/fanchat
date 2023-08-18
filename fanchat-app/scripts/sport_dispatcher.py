import boto3
import json

lambda_client = boto3.client('lambda')
sports_config = {
    "nba": {
        "api_key_param": "/fanchat/nba-api-token",
        "api_sport": "http://api.sportradar.us/nba/",
        "dynamodb_table": "NbaMatchTable"
    },
    # Add other sports configurations here
}

def lambda_handler(event, context):
    sport = event.get('sport')
    if not sport:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing sport parameter')
        }
    
    sport_config = sports_config.get(sport)
    if not sport_config:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid sport')
        }
    
    # Construct event for get_daily_matches.py Lambda
    daily_matches_event = {
        "api_key_param": sport_config['api_key_param'],
        "api_sport": sport_config['api_sport'],
        "dynamodb_table": sport_config['dynamodb_table']
    }
    
    # Invoke get_daily_matches.py Lambda
    response = lambda_client.invoke(
        FunctionName='get_daily_matches',  # Replace with your function name
        InvocationType='Event',  # Asynchronous invocation
        Payload=json.dumps(daily_matches_event)
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Dispatcher Lambda invoked successfully')
    }
