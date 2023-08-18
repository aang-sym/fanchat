import boto3
from schema.sports_ddb_schema import (
    SPORT_TABLE_NAME, SPORT_KEY_SCHEMA, SPORT_ATTRIBUTE_DEFINITIONS, SPORT_PROVISIONED_THROUGHPUT,
    MATCH_TABLE_NAME, MATCH_KEY_SCHEMA, MATCH_ATTRIBUTE_DEFINITIONS, MATCH_PROVISIONED_THROUGHPUT,
    CHAT_MESSAGE_TABLE_NAME, CHAT_MESSAGE_KEY_SCHEMA, CHAT_MESSAGE_ATTRIBUTE_DEFINITIONS, CHAT_MESSAGE_PROVISIONED_THROUGHPUT
)

class DynamoDBSetup:
    def __init__(self):
        self.dynamodb = boto3.client('dynamodb')

    def create_sport_table(self):
        self.create_table(
            table_name=SPORT_TABLE_NAME,
            key_schema=SPORT_KEY_SCHEMA,
            attribute_definitions=SPORT_ATTRIBUTE_DEFINITIONS,
            provisioned_throughput=SPORT_PROVISIONED_THROUGHPUT
        )

    def create_match_table(self):
        self.create_table(
            table_name=MATCH_TABLE_NAME,
            key_schema=MATCH_KEY_SCHEMA,
            attribute_definitions=MATCH_ATTRIBUTE_DEFINITIONS,
            provisioned_throughput=MATCH_PROVISIONED_THROUGHPUT
        )

    def create_chat_message_table(self):
        self.create_table(
            table_name=CHAT_MESSAGE_TABLE_NAME,
            key_schema=CHAT_MESSAGE_KEY_SCHEMA,
            attribute_definitions=CHAT_MESSAGE_ATTRIBUTE_DEFINITIONS,
            provisioned_throughput=CHAT_MESSAGE_PROVISIONED_THROUGHPUT
        )

    def create_table(self, table_name, key_schema, attribute_definitions, provisioned_throughput):
        try:
            table_names = self.dynamodb.list_tables()['TableNames']
            if table_name not in table_names:
                self.dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=key_schema,
                    AttributeDefinitions=attribute_definitions,
                    ProvisionedThroughput=provisioned_throughput
                )
                print(f"{table_name} created successfully.")
            else:
                print(f"{table_name} already exists.")
        except Exception as e:
            print(f"An error occurred while creating the table: {e}")

if __name__ == "__main__":
    dynamodb_setup = DynamoDBSetup()

    # Create the SportTable
    dynamodb_setup.create_sport_table()

    # Create the MatchTable
    dynamodb_setup.create_match_table()

    # Create the ChatMessageTable
    dynamodb_setup.create_chat_message_table()
