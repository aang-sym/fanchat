from aws_cdk import (
    aws_ec2 as ec2,
    aws_events as events,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    aws_ssm as ssm,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_events_targets as events_targets,
    core
)
import os
import json
from datetime import datetime, timedelta

class SportsDataStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Constants
        app_name = "NbaMatchPolling"
        event_bridge_rule_name = "GameDayGameStartRule"
        hit_interval_in_seconds = 60
        hit_duration_in_seconds = 3 * 60 * 60

        # VPC setup
        vpc = ec2.Vpc(self, f"{app_name}-SportDataVpc",
            cidr="10.0.0.0/16",
            nat_gateways=1,
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Web Tier",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Application Tier",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=24,
                )
            ]
        )

        # Parameter Store - API Key
        api_key = ssm.StringParameter(self, f"{app_name}-APIKey",
            parameter_name="SportradarApiKey",
            description="API key to pull data from sportradar.com",
            simple_name=True,
            string_value="update-this",
            tier=ssm.ParameterTier.STANDARD
        )
        
        # Create an SNS topic to publish game scores
        scores_topic = sns.Topic(self, f"{app_name}-ScoresTopic",
            display_name="Scores Topic"
        )

        # IAM role for game data Lambda
        game_data_lambda_role = iam.Role(self, f"{app_name}-GameDataLambdaIAMRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"),
            ],
        )

        # Lambda function for game data
        game_data_lambda = _lambda.Function(self, f"{app_name}-GameDataLambda",
            description="Lambda function that pulls game data for a game from sportradar.com",
            role=game_data_lambda_role,
            runtime=_lambda.Runtime.NODEJS_14_X,
            memory_size=1024,
            timeout=core.Duration.minutes(1),
            code=_lambda.Code.from_asset(path=os.path.join(__dirname, "/../src")),
            handler="game-data-lambda.handler",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            environment={
                "REGION": core.Aws.REGION,
            }
        )

        # State machine to iterate
        configure_count = sfn.Pass(self, "ConfigureCount",
            result={
                "index": 0,
                "step": 1,
                "count": hit_duration_in_seconds // hit_interval_in_seconds,
                "score": 0,
            },
            result_path="$.iterator"
        )

        iterator = sfn_tasks.LambdaInvoke(self, "GameDataTask",
            lambda_function=game_data_lambda,
            payload_response_only=True,
            retry_on_service_exceptions=False,
            result_path="$.iterator"
        )

        wait_state = sfn.Wait(self, "Wait",
            time=sfn.WaitTime.duration(core.Duration.seconds(hit_interval_in_seconds))
        ).next(iterator)

        done_state = sfn.Succeed(self, "Done")

        is_count_reached = sfn.Choice(self, "IsCountReached").when(
            sfn.Condition.string_equals("$.iterator.continue", "CONTINUE"),
            wait_state
        ).otherwise(done_state)

        game_data_state_machine = sfn.StateMachine(self, f"{app_name}-SportsDataStateMachine",
            state_machine_name=f"{app_name}-SportsDataStateMachine",
            definition=configure_count.next(iterator).next(is_count_reached)
        )

        # IAM Role for state machine execution
        step_function_execution_role = iam.Role(self, f"{app_name}-StepFunctionExecutionRole",
            role_name=f"{app_name}-StepFunctionExecutionRole",
            assumed_by=iam.ServicePrincipal("events.amazonaws.com"),
            inline_policies={
                "ExecuteStepFunction": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["states:StartExecution"],
                            resources=[game_data_state_machine.state_machine_arn],
                        )
                    ]
                )
            }
        )

        # IAM role for check games Lambda
        check_games_lambda_role = iam.Role(self, f"{app_name}-CheckGamesLambdaIAMRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"),
            ],
            inline_policies={
                "ReadParameterStore": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["ssm:GetParameter", "ssm:GetParameters"],
                            resources=[api_key.parameter_arn]
                        )
                    ]
                ),
                "CreateEventBridgeRule": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["events:PutTargets", "events:PutRule"],
                            resources=[
                                f"arn:aws:events:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:rule/{event_bridge_rule_name}"
                            ]
                        )
                    ]
                ),
                "IamPassRole": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["iam:PassRole"],
                            resources=[step_function_execution_role.role_arn]
                        )
                    ]
                )
            }
        )

        # Lambda function for checking games
        check_games_lambda = _lambda.Function(self, f"{app_name}-CheckGamesLambda",
            description="Lambda function that pulls game data from sportradar.com",
            role=check_games_lambda_role,
            runtime=_lambda.Runtime.NODEJS_14_X,
            memory_size=1024,
            timeout=core.Duration.minutes(1),
            code=_lambda.Code.from_asset(path=os.path.join(__dirname, "/../src")),
            handler="check-games-lambda.handler",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            environment={
                "REGION": core.Aws.REGION,
                "EVENT_BRIDGE_RULE": event_bridge_rule_name,
                "STATE_MACHINE": game_data_state_machine.state_machine_arn,
                "STATE_MACHINE_EXECUTION_ROLE": step_function_execution_role.role_arn,
            }
        )
            
        lambda_target = targets.LambdaFunction(check_games_lambda, retry_attempts=2)
        check_games_schedule_rule = events.Rule(
            self,
            f"{app_name}-CheckGamesScheduleRule",
            rule_name=f"{app_name}-CheckGamesScheduleRule",
            description="Rule for running Lambda function once every day",
            schedule=events.Schedule.cron(minute="0", hour="16"),  # 16 GMT -> 9am PDT
        )
        check_games_schedule_rule.add_target(lambda_target)