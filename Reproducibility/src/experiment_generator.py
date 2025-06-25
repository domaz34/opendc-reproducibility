import os
import json

from src.utils import *


def build_entry(folder, file, original_entry=None, default_type=None):
    
    """
    Build a dictionary representing a file entry in the experiment configuration.

    Args:
        folder: Folder path prefix for the file.
        file: File name.
        original_entry: Existing entry to preserve the type field.
        default_type: Default type to assign if not in original.

    Returns:
        A dictionary with 'pathToFile' and possibly 'type'.
    """
     
    entry = {"pathToFile": f"{folder}/{file}"}

    if original_entry and "type" in original_entry:
        entry["type"] = original_entry["type"]
    elif default_type:
        entry["type"] = default_type
    return entry


def update_experiment_values(
    experiment_template=None,
    topologies=None,
    workloads=None,
    failures=None,
    prefab_types=None,
    checkpoint_interval=None,
    checkpoint_duration=None,
    checkpoint_scaling=None,
    export_intervals=None,
    print_frequencies=None,
    files_to_export=None,
    name=None,
    seeds=None,
    runs=None,
    max_failures=None,
    output_folder=None
):
    """
    Generate and save an experiment configuration file.

    This function loads a base experiment template (if provided), overrides or populates its fields with 
    user-defined inputs, and then writes the updated configuration to a new file.

    Supports batch generation using seed, run, interval, and frequency lists.

    Args:
        Can tell from the names, all optional.

    Returns:
        The generated filename.
    """

    if experiment_template:
        try:
            with open(f"templates/experiments/{experiment_template}", 'r') as f:
                base_experiment = json.load(f)
        except Exception as e:
            print(f"Failed to load base experiment: {e}")
            return
    else:
        base_experiment = {}
    
    base_name = name or base_experiment.get("name", "custom_experiment")

    # Topologies: no default type  
    if topologies is not None:
        original_entries = base_experiment.get("topologies", [])
        base_experiment["topologies"] = [
            build_entry("topologies", file, original_entries[index] if index < len(original_entries) else None)
            for index, file in enumerate(topologies)
        ]
    
    # Workloads: default to ComputeWorkload
    if workloads is not None:
        original_entries = base_experiment.get("workloads", [])
        base_experiment["workloads"] = [
            build_entry("workload_traces", file, original_entries[index] if index < len(original_entries) else None, "ComputeWorkload")
            for index, file in enumerate(workloads)
        ]

    # Failures: default to trace-based
    if failures is not None:
        original_entries = base_experiment.get("failureModels", [])
        base_experiment["failureModels"] = [
            build_entry("failure_traces", file, original_entries[index] if index < len(original_entries) else None, "trace-based")
            for index, file in enumerate(failures)
        ]

    max_length = max(
        len(seeds or []),
        len(runs or []),
        len(export_intervals or []),
        len(print_frequencies or []),
        1
    )

    for i in range(max_length):
        experiment = json.loads(json.dumps(base_experiment))

        seed = get_val(seeds, i)
        run = get_val(runs, i)

        full_name = f"{base_name}"
        if seed is not None:
            full_name += f"_s{seed}"
            experiment["initialSeed"] = int(seed)
        if run is not None:
            full_name += f"_r{run}"
            experiment["runs"] = int(run)

        experiment["name"] = full_name

        policies = []

        for idx in range(len(prefab_types or [])):
            policy_type = get_val(prefab_types, idx)
            
            if policy_type:
                policy = {
                    "type": "prefab",
                    "policyName": policy_type
                }

            policies.append(policy)
        
        if policies:
            experiment["allocationPolicies"] = policies

    
        if checkpoint_interval is not None and checkpoint_duration is not None and checkpoint_scaling is not None:
            experiment["checkpointModels"] = [{
                "checkpointInterval": int(checkpoint_interval),
                "checkpointDuration": int(checkpoint_duration),
                "checkpointIntervalScaling": float(checkpoint_scaling)
            }]

        if max_failures is not None:
            experiment["maxNumFailures"] = [int(mf) for mf in max_failures]

        interval = get_val(export_intervals, i)
        freq = get_val(print_frequencies, i)

        if "exportModels" in experiment and experiment["exportModels"]:
            if interval is not None:
                experiment["exportModels"][0]["exportInterval"] = int(interval)
            if freq is not None:
                experiment["exportModels"][0]["printFrequency"] = int(freq)
            if files_to_export:
                experiment["exportModels"][0]["filesToExport"] = files_to_export
       
        else:
            export_entry = {}
            if interval is not None:
                export_entry["exportInterval"] = int(interval)
            if freq is not None:
                export_entry["printFrequency"] = int(freq)
            if files_to_export:
                export_entry["filesToExport"] = files_to_export
            if export_entry:
                experiment["exportModels"] = [export_entry]
        
        if output_folder is not None:
            experiment["outputFolder"] = output_folder

        filename = f"{full_name}.json" if not full_name.endswith(".json") else full_name

        save_experiment(experiment, filename)

        return filename


def save_experiment(experiment, new_name):
    """
    Save a single experiment configuration to disk.

    Args:
        experiment: The experiment JSON content.
        new_name: Filename to save as.
    """
    new_path = f"experiments/{new_name}"
    try:
        with open(new_path, 'w') as f:
            json.dump(experiment, f, indent=4)
        print(f"Generated {new_name}")
    except Exception as e:
        print(f"Error saving {new_name}: {e}")





