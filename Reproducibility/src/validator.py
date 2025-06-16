import os
import json
import pandas as pd

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

# Helper function that checks whether a file exists at specified path. It takes the key, file data for that key and also name of the 
def check_files(json_key, data, name):
    if json_key not in data:
        return 
    for entry in data[json_key]:
        file_path = entry.get("pathToFile")
        if not file_path:
            raise ValueError(f"Missing 'pathToFile' in {json_key} entry of '{name}': {entry}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found for {json_key} in '{name}': {file_path}")

# Helper function that recursively traverses the directory provided and collects all the parquet files
def get_parquet_files_recursive(root_dir):
    parquet_files = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".parquet"):
                relative_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
                parquet_files[relative_path] = os.path.join(dirpath, filename)
    return parquet_files

# Helper function that checks whether the experiment outputs match
def compare_experiment_outputs(orig_path, repr_path):
    try:
        orig_files = get_parquet_files_recursive(orig_path)
        repr_files = get_parquet_files_recursive(repr_path)

        missing = set(orig_files.keys()) - set(repr_files.keys())
        extra = set(repr_files.keys()) - set(orig_files.keys())
        if missing or extra:
            return False

        for rel_path in orig_files:
            df1 = pd.read_parquet(orig_files[rel_path])
            df2 = pd.read_parquet(repr_files[rel_path])
            if not df1.equals(df2):
                return False
        return True
    except Exception as e:
        return False

# Function that goes over all of the experiment and its reproduced output pairs and checks whether they match
def compare_all_experiments_outputs():
    dirs = [direc for direc in os.listdir("output") if os.path.isdir(f"output/{direc}")]

    experiment_pairs = []
    repr_dirs = [direc for direc in dirs if direc.startswith("repr_")]

    for repr_dir in repr_dirs:
        original_dir = repr_dir.replace("repr_", "")
        if original_dir in dirs:
            experiment_pairs.append((original_dir, repr_dir))

    if not experiment_pairs:
        print("No experiment pairs found.")
        return

    for orig, repr_ in experiment_pairs:
        orig_path = f"output/{orig}"
        repr_path = f"output/{repr_}"
        if compare_experiment_outputs(orig_path, repr_path) is False:
            print("Files missmatch")
            return
    print("Experiments match")