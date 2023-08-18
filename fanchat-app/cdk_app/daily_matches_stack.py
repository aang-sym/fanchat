from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets

class NBADataStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define DynamoDB table
        table = dynamodb.Table(
            self, 'MatchTable',
            table_name='MatchTable',
            partition_key=dynamodb.Attribute(
                name='MatchId',
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=5,
            write_capacity=5
        )

        # Define Lambda function
        function = _lambda.Function(
            self, 'NBALambdaFunction',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='lambda_function.lambda_handler',
            code=_lambda.Code.from_asset('path_to_lambda_code_directory'),  # Replace with actual path
            role=YOUR_LAMBDA_ROLE_ARN,  # Replace with actual role ARN
            description='NBA Lambda Function',
            timeout=core.Duration.seconds(10),
            memory_size=128
        )

        # Define EventBridge rule
        rule = events.Rule(
            self, 'EventBridgeRule',
            schedule=events.Schedule.rate(core.Duration.minutes(5)),  # Trigger every 5 minutes
            targets=[targets.LambdaFunction(function)]
        )

app = core.App()
NBADataStack(app, "NBADataStack")
app.synth()