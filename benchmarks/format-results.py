# Format k6 results
import json
from pathlib import Path

import numpy as np


results = []

pwd = Path().absolute()
results_dir = pwd / "benchmarks" / "results"

pathlist = results_dir.glob("*.json")
for path in pathlist:
    # because path is object not string
    path_in_str = str(path)

    if path.name == "all-results.json":
        continue

    data_points = []
    with open(path_in_str, "r") as results_file:
        while True:
            line = results_file.readline()

            if not line:
                break  # EOF

            result = json.loads(line)
            if result["type"] == "Point":
                data_points.append(result)

    request_duration_results = filter(
        lambda r: r["metric"] == "http_req_duration", data_points
    )
    request_durations = list(
        map(lambda r: r["data"]["value"], request_duration_results)
    )
    requests = len(list(filter(lambda r: r["metric"] == "http_reqs", data_points)))

    results.append(
        {
            "api_name": path.stem,
            "results": {
                "latency": {
                    "max": np.max(request_durations) * 1000,
                    "min": np.min(request_durations) * 1000,
                    "mean": np.mean(request_durations) * 1000,
                    "dist": {
                        "95": np.percentile(request_durations, 95) * 1000,
                        "98": np.percentile(request_durations, 98) * 1000,
                        "99": np.percentile(request_durations, 99) * 1000,
                    },
                    "stdev": np.std(request_durations) * 1000,
                },
                "requests": {
                    "max": requests / 15,
                    "min": requests / 15,
                    "mean": requests / 15,
                    "dist": {
                        "95": requests / 15,
                        "98": requests / 15,
                        "99": requests / 15,
                    },
                    "stdev": requests / 15,
                },
            },
        }
    )


with open(results_dir / "all-results.json", "w") as results_file:
    json.dump(results, results_file, indent=2)
