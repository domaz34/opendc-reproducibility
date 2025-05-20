import os
import zipfile
import json


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
            # Carbon when figure out how     
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


def create_reproducibility_zip(queue, output_name="reproducibility_capsule.zip"):
    files_to_zip = collect_experiment_files(queue)

    static_includes = ["main.ipynb"]
    source_dirs = ["src", "OpenDCExperimentRunner"]

    with zipfile.ZipFile(output_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        for file_path in files_to_zip:
            if os.path.isdir(file_path):
                for root, _, files in os.walk(file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path)
                        zipf.write(full_path, arcname=rel_path)
            elif os.path.isfile(file_path):
                zipf.write(file_path, arcname=file_path)


        for file in static_includes:
            if os.path.exists(file):
                zipf.write(file, arcname=file)


        for src in source_dirs:
            for root, _, files in os.walk(src):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path)
                    zipf.write(full_path, arcname=rel_path)

    
