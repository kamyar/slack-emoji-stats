from datetime import datetime

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_resource import MetricResource
from datadog_api_client.v2.model.metric_series import MetricSeries


def get_metric(**kwargs):
    return MetricPayload(
        series=[
            MetricSeries(
                metric="slack.emoji.reaction",
                type=MetricIntakeType.COUNT,
                points=[
                    MetricPoint(
                        timestamp=int(datetime.now().timestamp()),
                        value=1,
                    ),
                ],
                resources=[
                    MetricResource(
                        type=key,
                        name=str(value),
                    )
                    for key, value in kwargs.items()
                ],
            ),
        ],
    )


def publish_emoji_metric(**kwargs):
    configuration = Configuration()
    with ApiClient(configuration) as api_client:
        api_instance = MetricsApi(api_client)
        response = api_instance.submit_metrics(body=get_metric(**kwargs))
        # print(response)
