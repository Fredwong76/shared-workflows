import aws_cdk as cdk
from aws_cdk import aws_sns as sns
from constructs import Construct


class SmokeStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        sns.Topic(self, "SmokeTopic")


app = cdk.App()
SmokeStack(app, "SmokeStack")
app.synth()
