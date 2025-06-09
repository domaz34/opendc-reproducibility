import os
import json

from src.utils import *

#Builds experiment file entry based on folder and file. Can take original entry in order to keep its type. Can also take a default type if set
def build_entry(folder, file, original_entry=None, default_type=None):

    entry = {"pathToFile": f"{folder}/{file}"}

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


    return experiment

#Updates values of experiment by taking list of prefab dictionaries, dictionary of checkpoint values and dictionary for export model values. 
# It will create different experiment file for different carbon trace, if list lengths missmatch then it will just ignore the missing part
def update_experiment_values(prefabs, checkpoint, export_model, name, experiment):
    try:
        with open(f"experiments/{experiment}", 'r') as f:
            base_experiment = json.load(f)
    except Exception as e:
        print(f"Failed to load base experiment: {e}")
        return

    seeds = export_model.get("initialSeed", [])
    runs = export_model.get("numberRuns", [])
    intervals = export_model.get("exportInterval", [])
    frequencies = export_model.get("printFrequency", [])

    max_length = max(len(seeds), len(runs), len(intervals), len(frequencies), 1)

    print(max_length)
    for i in range(max_length):
        experiment = json.loads(json.dumps(base_experiment))

        seed = get_val(seeds, i)
        run = get_val(runs, i)
        experiment["name"] = f"{name}_s{seed}_r{run}"

        if seed:
            experiment["seed"] = seed
            name = f"s{seed}_{name}"

        if run:
            experiment["runs"] = run
            name = f"r{run}_{name}"

        policies = []

        for idx in range(len(prefabs["type"])):
            policy_type = get_val(prefabs["type"], idx)
            filters = get_val(prefabs["filters"], idx)
            weighers = get_val(prefabs["weighers"], idx)
            
            
            if policy_type:
                policy = {
                    "type": "prefab",
                    "policyName": policy_type
                }

                if filters:
                    policy["filters"] = []
                    for f_type, ratio in filters:
                        entry = {"type": f_type}
                        if ratio is not None:
                            entry["allocationRatio"] = float(ratio)
                        policy["filters"].append(entry)

                if weighers:
                    policy["weighers"] = []
                    for weigher in weighers:
                        if weigher:
                            w_type, multiplier = weigher
                            policy["weighers"].append({
                                "type": w_type,
                                "multiplier": float(multiplier)
                            })

                policies.append(policy)
        
        if policies:
            experiment["allocationPolicies"] = policies

        
        if checkpoint:
            interval = get_val(checkpoint.get("checkpointInterval", []), i)
            duration = get_val(checkpoint.get("checkpointDuration", []), i)
            scaling = get_val(checkpoint.get("checkpointIntervalScaling", []), i)

            if interval is not None and duration is not None and scaling is not None:
                experiment["checkpointModels"] = [{
                    "checkpointInterval": int(interval),
                    "checkpointDuration": int(duration),
                    "checkpointIntervalScaling": float(scaling)
                }]

       
        interval = get_val(intervals, i)
        frequency = get_val(frequencies, i)

        if "exportModels" in experiment and experiment["exportModels"]:
            if interval is not None:
                experiment["exportModels"][0]["exportInterval"] = int(interval)
            if frequency is not None:
                experiment["exportModels"][0]["printFrequency"] = int(frequency)
       
        else:
            export_entry = {}
            if interval is not None:
                export_entry["exportInterval"] = int(interval)
            if frequency is not None:
                export_entry["printFrequency"] = int(frequency)
            if export_entry:
                experiment["exportModels"] = [export_entry]
        
        save_experiment(experiment, name)

def save_experiment(experiment, new_name):

    new_path = f"experiments/{new_name}"
    try:
        with open(new_path, 'w') as f:
            json.dump(experiment, f, indent=4)
        print(f"Generated {new_name}")
    except Exception as e:
        print(f"Error saving {new_name}: {e}")





