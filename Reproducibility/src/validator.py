import os
import json

# Checks whether topologies, workloads and failure models exist in the experiment file 
# Can later be extended to support more robust validation
def validate_experiments(experiment_queue):
    for exp in experiment_queue:
        name = exp["name"]
        exp_path = f"experiments/{name}"

        try:
            with open(exp_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to read '{name}': {e}")
            continue

        try:
            check_files("topologies", data, name)
            check_files("workloads", data, name)
            check_files("failureModels", data, name)
        except Exception as e:
            print(f"Validation failed for '{name}': {e}")
            return False
    
    print(f"Validation Passed")
    return True

# Helper function that checks whether a file exists at specified path. It takes the key 
def check_files(json_key, data, name):
    if json_key not in data:
        return 
    for entry in data[json_key]:
        file_path = entry.get("pathToFile")
        if not file_path:
            raise ValueError(f"Missing 'pathToFile' in {json_key} entry of '{name}': {entry}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found for {json_key} in '{name}': {file_path}")