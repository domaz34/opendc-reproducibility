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

    return required_files

def recursive_zip(file_path, zipf):
    for root, _, files in os.walk(file_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path)
            zipf.write(full_path, arcname=rel_path)

def create_reproducibility_zip(queue, output_name="reproducibility_capsule.zip"):
    files_to_zip = collect_experiment_files(queue)
    readme_path = generate_readme_from_queue(queue)

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

    
