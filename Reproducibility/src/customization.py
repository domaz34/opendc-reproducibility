import os
import json

#Builds experiment file entry based on folder and file. Can take original entry in order to keep its type. Can also take a default type if set
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


    return experiment

# Updates topology carbon field and batery field by taking a base topology, a list of carbons, number of hosts, lists of battery capacity and et.
# It will create different topology file for different carbon trace, if list lengths missmatch then it will just ignore the missing part
def update_topology_carbon_battery(
    topology_file,
    carbon_list,
    NoH_list,
    battery_capacity_list,
    starting_CI_list,
    charging_speed_list,
    include_battery
):
    topology_path = os.path.join("topologies", topology_file)
    
    try:
        with open(topology_path, 'r') as f:
            original_topology = json.load(f)
    except Exception as e:
        print(f"Failed to load topology {topology_file}: {e}")
        return
    
    max_len = max(len(carbon_list), len(NoH_list), len(battery_capacity_list), len(starting_CI_list), len(charging_speed_list))
    
    def get_val(lst, idx):
        return lst[idx] if idx < len(lst) else None

    for i in range(max_len):
        new_topology = json.loads(json.dumps(original_topology))
        
        NoH = get_val(NoH_list, i)
        if "clusters" in new_topology:
            for cluster in new_topology["clusters"]:
                for host in cluster.get("hosts", []):
                    if NoH is not None:
                        host["count"] = NoH             #Treats all the clusters equally
        

        carbon = get_val(carbon_list, i)
        if carbon:
            new_topology["clusters"][0]["powerSource"] = {
                "carbonTracePath": os.path.join("carbon_traces", carbon)
            }
        

        battery_capacity = get_val(battery_capacity_list, i)
        starting_CI = get_val(starting_CI_list, i)
        charging_speed = get_val(charging_speed_list, i)
        
        if include_battery and battery_capacity is not None and starting_CI and starting_CI > 0:
            new_topology["clusters"][0]["battery"] = {
                "capacity": battery_capacity,
                "chargingSpeed": charging_speed * battery_capacity if charging_speed else 0,
                "embodiedCarbon": 100 * battery_capacity,
                "expectedLifetime": 10,
                "batteryPolicy": {
                    "type": "runningMeanPlus",
                    "startingThreshold": starting_CI,
                    "windowSize": 168
                }
            }
  
        
        base_topo = os.path.splitext(topology_file)[0]
        base_carbon = os.path.splitext(carbon)[0] if carbon else "carbon-none"
        hosts_str = f"hosts{NoH}" if NoH is not None else "hostsNA"
        battery_str = f"bat{battery_capacity}" if battery_capacity is not None else "batNA"
        new_name = f"{base_topo}_{base_carbon}_{hosts_str}_{battery_str}.json"
        new_path = os.path.join("topologies", new_name)
        
        try:
            with open(new_path, 'w') as f:
                json.dump(new_topology, f, indent=4)
            print(f"Generated {new_name}")
        except Exception as e:
            print(f"Error saving {new_name}: {e}")




# Refreshes the dropdown menu after file has been uploaded, currently used for experiment file update
def refresh_dropdown(dropdown, folder, selected=None, keep_original=True):
    files = os.listdir(folder)
    options = ['[Keep original]'] + files if keep_original else files
    dropdown.options = options
    if selected in files:
        dropdown.value = selected



# Helper function to parse input as a number, list, range
def parse_input(input_str):
    input_str = input_str.strip()
    if not input_str:
        return []
    
    if '-' in input_str and ':' in input_str:
        try:
            start_end, step = input_str.split(':')
            start, end = start_end.split('-')
            start, end, step = float(start), float(end), float(step)
            return frange(start, end, step)
        except Exception:
            return []
    

    elif ',' in input_str:
        parts = input_str.split(',')
        result = []
        for p in parts:
            p = p.strip()
            try:
                result.append(float(p))
            except ValueError:
                pass
        return result
    
    else:
        try:
            return [float(input_str)]
        except ValueError:
            return []

# Function to create a list from range
def frange(start, end, step):
    result = []
    current = start
    while current <= end:
        result.append(round(current, 8))
        current += step
    return result