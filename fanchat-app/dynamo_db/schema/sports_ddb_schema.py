# SportTable schema
SPORT_TABLE_NAME = 'SportTable'
SPORT_KEY_SCHEMA = [
    {
        'AttributeName': 'SportId',
        'KeyType': 'HASH'  # Partition key
    }
]

SPORT_ATTRIBUTE_DEFINITIONS = [
    {
        'AttributeName': 'SportId',
        'AttributeType': 'S'  # String type
    }
]

SPORT_PROVISIONED_THROUGHPUT = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}

# MatchTable schema
MATCH_TABLE_NAME = 'MatchTable'
MATCH_KEY_SCHEMA = [
    {
        'AttributeName': 'MatchId',
        'KeyType': 'HASH'  # Partition key
    },
    {
        'AttributeName': 'Date',
        'KeyType': 'RANGE'  # Sort key
    }
]

MATCH_ATTRIBUTE_DEFINITIONS = [
    {
        'AttributeName': 'MatchId',
        'AttributeType': 'S'  # String type
    },
    {
        'AttributeName': 'Date',
        'AttributeType': 'S'  # String type (optional)
    }
]

MATCH_PROVISIONED_THROUGHPUT = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}

# ChatMessageTable schema
CHAT_MESSAGE_TABLE_NAME = 'ChatMessageTable'
CHAT_MESSAGE_KEY_SCHEMA = [
    {
        'AttributeName': 'MatchId',
        'KeyType': 'HASH'  # Partition key
    },
    {
        'AttributeName': 'Timestamp',
        'KeyType': 'RANGE'  # Sort key
    }
]

CHAT_MESSAGE_ATTRIBUTE_DEFINITIONS = [
    {
        'AttributeName': 'MatchId',
        'AttributeType': 'S'  # String type
    },
    {
        'AttributeName': 'Timestamp',
        'AttributeType': 'N'  # Number type
    }
]

CHAT_MESSAGE_PROVISIONED_THROUGHPUT = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}
