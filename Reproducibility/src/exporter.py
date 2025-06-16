import os
import zipfile
import json

from src.summary_generator import *

def collect_experiment_files(selections_list, experiments_dir="experiments"):
    required_files = set()

    for selection in selections_list:
        experiment_path = os.path.join(experiments_dir, selection["name"])
        required_files.add(experiment_path)

        try:
            with open(experiment_path) as f:
                exp_data = json.load(f)
        except Exception as e:
            print(f"Failed to load {experiment_path}: {e}")
            continue

        for key, folder, json_path in [
            ("topology", "topologies", "topologies"),
            ("workload", "workload_traces", "workloads"),
            ("failures", "failure_traces", "failureModels")  
        ]:
            entries = selection.get(key)

            if entries:  
                for entry in entries:
                    required_files.add(os.path.join(folder, entry))
            else:  
                entries = exp_data.get(json_path, [])
                for entry in entries:
                    path = entry.get("pathToFile")
                    if path:
                        required_files.add(path)

        for topo_entry in exp_data.get("topologies", []):
            topo_path = topo_entry.get("pathToFile")
            if topo_path and os.path.exists(topo_path):
                try:
                    with open(topo_path, 'r') as f:
                        topo_data = json.load(f)
                        for cluster in topo_data.get("clusters", []):
                            power_source = cluster.get("powerSource", {})
                            trace = power_source.get("carbonTracePath")
                            if trace and os.path.exists(trace):
                                required_files.add(trace)
                except Exception as e:
                    print(f"Warning: Failed to parse topology {topo_path}: {e}")


    return required_files

def recursive_zip(file_path, zipf):
    for root, _, files in os.walk(file_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path)
            zipf.write(full_path, arcname=rel_path)

def create_reproducibility_zip(queue, readme_path="README.md", output_name="reproducibility_capsule.zip"):
    files_to_zip = collect_experiment_files(queue)
    

    static_includes = ["main.ipynb", readme_path]
    source_dirs = ["src", "OpenDCExperimentRunner", "output"]

    with zipfile.ZipFile(output_name, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
        
        for file_path in files_to_zip:
            if os.path.isdir(file_path):
                recursive_zip(file_path, zipf)
            elif os.path.isfile(file_path):
                zipf.write(file_path, arcname=file_path)


        for file in static_includes:
            if os.path.exists(file):
                zipf.write(file, arcname=file)


        for file_path in source_dirs:
            recursive_zip(file_path, zipf)

    
def quick_export_all_zip(output_name="reproducibility_capsule.zip"):

    roots = [
        "experiments", "README.md",
        "topologies", "workload_traces", "failure_traces",
        "output", "src", "OpenDCExperimentRunner",
        "main.ipynb"
    ]

    with zipfile.ZipFile(output_name, "w", zipfile.ZIP_STORED) as z:
        for path in roots:
            if os.path.isfile(path):
                z.write(path, arcname=path)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        full = os.path.join(root, f)
                        z.write(full, arcname=full)

