def update_experiment_fields(experiment, selections):
    experiment["name"] = f"{selections['experiment_name']}"

    if selections["topology"] != "[Keep original]":
        experiment["topologies"] = [{
            "pathToFile": f"topologies/{selections['topology']}"
        }]

    if selections["workload"] != "[Keep original]":
        experiment["workloads"] = [{
            "pathToFile": f"workload_traces/{selections['workload']}",
            "type": "ComputeWorkload"
        }]

    if selections["failures"] != "[Keep original]":
        experiment["failureModels"] = [{
            "type": "trace-based",
            "pathToFile": f"failure_traces/{selections['failures']}" 
        }]

    return experiment

# src/customization.py

import os


def refresh_dropdown(dropdown, folder, selected=None, keep_original=True):
    files = os.listdir(folder)
    options = ['[Keep original]'] + files if keep_original else files
    dropdown.options = options
    if selected in files:
        dropdown.value = selected

