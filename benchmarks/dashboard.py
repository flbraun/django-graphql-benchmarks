import json
import os

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

colors = [
    "#636EFA",
    "#EF553B",
    "#00CC96",
    "#AB63FA",
    "#FFA15A",
    "#19D3F3",
    "#FF6692",
    "#B6E880",
    "#FF97FF",
    "#FECB52",
]


def get_data(results, fn):
    all_servers = {result["api_name"]: True for result in results}.keys()

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

    # print(program_rps_map)
    ys = []
    for server_name in all_servers:
        query_results = [
            result["results"] for result in results if result["api_name"] == server_name
        ]
        dataRow = {
            "x": "top250",
            "y": list(map(fn, query_results)),
            "type": "bar",
            "name": server_name,
        }
        ys.append(dataRow)
    return ys


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

    # elif yMetric == "ERRORS":
    #     yMetricFn = lambda x: sum(x['summary']['errors'].values())
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
        # Input('benchmark-index', 'value'),
        Input("response-time-metric", "value")
    ],
)
def updateGraph2(yMetric):
    # print(bench_results)
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
