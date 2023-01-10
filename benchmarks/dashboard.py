import json
import os
import random

import dash
from dash.dependencies import Input, Output
from dash import dcc, html

colors = [
    "#77DD77",
    "#836953",
    "#89CFF0",
    "#99C5C4",
    "#9ADEDB",
    "#AA9499",
    "#AAF0D1",
    "#B2FBA5",
    "#B39EB5",
    "#BEE7A5",
    "#BEFD73",
    "#C1C6FC",
    "#C6A4A4",
    "#CB99C9",
    "#FDFD96",
    "#FF6961",
    "#FF964F",
    "#FF9899",
    "#FFB7CE",
    "#CA9BF7",
    "#BDB0D0",
]
random.shuffle(colors)


def get_data(results, fn):
    api_names = [result["api_name"] for result in results]
    query_results = [result["results"] for result in results]

    return [
        {
            "x": api_names,
            "y": list(map(fn, query_results)),
            "type": "bar",
            "name": api_names,
            "marker": {
                "color": colors,
            },
        }
    ]


def get_ymetric_fn(yMetric, on="latency"):
    if yMetric == "P95":

        def yMetricFn(x):
            return x[on]["dist"]["95"]

    elif yMetric == "P98":

        def yMetricFn(x):
            return x[on]["dist"]["98"]

    elif yMetric == "P99":

        def yMetricFn(x):
            return x[on]["dist"]["99"]

    elif yMetric == "MIN":

        def yMetricFn(x):
            return x[on]["min"]

    elif yMetric == "MAX":

        def yMetricFn(x):
            return x[on]["max"]

    else:

        def yMetricFn(x):
            return x[on]["mean"]

    if on == "latency":
        return lambda x: round(yMetricFn(x) / 1000, 2)

    return lambda x: int(yMetricFn(x))


with open("./benchmarks/results/all-results.json", "r") as json_file:
    bench_results = json.load(json_file)


app = dash.Dash()

app.layout = html.Div(
    children=[
        html.Label("Response time metric"),
        dcc.Dropdown(
            id="response-time-metric",
            options=[
                {"label": "P95", "value": "P95"},
                {"label": "P98", "value": "P98"},
                {"label": "P99", "value": "P99"},
                {"label": "Min", "value": "MIN"},
                {"label": "Max", "value": "MAX"},
                {"label": "Average", "value": "AVG"},
                {"label": "Mean", "value": "MEAN"},
            ],
            value="P99",
        ),
        dcc.Graph(id="response-time-vs-query"),
        dcc.Graph(id="requests-vs-query"),
    ]
)


@app.callback(
    Output("response-time-vs-query", "figure"),
    [
        # Input('benchmark-index', 'value'),
        Input("response-time-metric", "value")
    ],
)
def updateGraph(yMetric):
    figure = {
        "data": get_data(bench_results, get_ymetric_fn(yMetric, on="latency")),
        "layout": {
            "yaxis": {"title": "Response time ({}) in ms".format(yMetric)},
            "xaxis": {"title": "API", "categoryorder": "total descending"},
            "title": "Response time by API",
        },
    }
    return figure


@app.callback(
    Output("requests-vs-query", "figure"),
    [
        Input("response-time-metric", "value")
    ],
)
def updateGraph2(yMetric):
    figure = {
        "data": get_data(bench_results, get_ymetric_fn(yMetric, on="requests")),
        "layout": {
            "yaxis": {"title": "Requests/s ({})".format(yMetric)},
            "xaxis": {"title": "API", "categoryorder": "total descending"},
            "title": "Reqs/s by API",
        },
    }
    return figure


port = int(os.environ.get("DASHBOARD_PORT", "8099"))
app.run_server(host="0.0.0.0", port=port, debug=True)
