import os

#Builds experiment file entry based on folder and file. Can take original entry in order to keep its time. Can also take a default type if set
def build_entry(folder, file, original_entry=None, default_type=None):

    entry = {"pathToFile": os.path.join(folder, file)}

    if original_entry and "type" in original_entry:
        entry["type"] = original_entry["type"]
    elif default_type:
        entry["type"] = default_type
    return entry

# Updates experiment fields given experiment file and dictionary of selections. 
def update_experiment_fields(experiment, selections):
    experiment["name"] = selections["name"]

    # Topologies: no default type  
    if selections.get("topology") is not None:
        original_entries = experiment.get("topologies", [])
        experiment["topologies"] = [
            build_entry("topologies", file, original_entries[index] if index < len(original_entries) else None)
            for index, file in enumerate(selections["topology"])
        ]

    # Workloads: default to ComputeWorkload
    if selections.get("workload") is not None:
        original_entries = experiment.get("workloads", [])
        experiment["workloads"] = [
            build_entry("workload_traces", file, original_entries[index] if index < len(original_entries) else None, "ComputeWorkload")
            for index, file in enumerate(selections["workload"])
        ]

    # Failures: default to trace-based
    if selections.get("failures") is not None:
        original_entries = experiment.get("failureModels", [])
        experiment["failureModels"] = [
            build_entry("failure_traces", file, original_entries[index] if index < len(original_entries) else None, "trace-based")
            for index, file in enumerate(selections["failures"])
        ]

    # Carbon: default to trace-based
    # if selections.get("carbon") is not None:
    #     original_entries = experiment.get("carbonModels", [])
    #     experiment["carbonModels"] = [
    #         build_entry("carbon_traces", file, original_entries[index] if index < len(original_entries) else None, "trace-based")
    #         for index, file in enumerate(selections["carbon"])
    #     ]

    return experiment

# Refreshes the dropdown menu after file has been uploaded, currently used for experiment file update
def refresh_dropdown(dropdown, folder, selected=None, keep_original=True):
    files = os.listdir(folder)
    options = ['[Keep original]'] + files if keep_original else files
    dropdown.options = options
    if selected in files:
        dropdown.value = selected

