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
    
    carbon_list = carbon_list or []
    NoH_list = NoH_list or []
    battery_capacity_list = battery_capacity_list or []
    starting_CI_list = starting_CI_list or []
    charging_speed_list = charging_speed_list or []
    
    max_len = max(len(carbon_list), len(NoH_list), len(battery_capacity_list), len(starting_CI_list), len(charging_speed_list))
    
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
        
        if include_battery and battery_capacity is not None and starting_CI is not None and float(starting_CI) > 0:
            new_topology["clusters"][0]["battery"] = {
                "capacity": battery_capacity,
                "chargingSpeed": int(charging_speed) * int(battery_capacity) if charging_speed else 0,
                "embodiedCarbon": 100 * int(battery_capacity),
                "expectedLifetime": 10,
                "batteryPolicy": {
                    "type": "runningMeanPlus",
                    "startingThreshold": starting_CI,
                    "windowSize": 168
                }
            }
  
        
        base_topo = os.path.splitext(topology_file)[0]
        base_carbon = os.path.splitext(carbon)[0] if carbon else ""
        hosts_str = f"hosts{NoH}" if NoH is not None else ""
        battery_str = f"bat{battery_capacity}" if battery_capacity is not None and include_battery else ""
        new_name = f"{base_topo}{base_carbon}{hosts_str}{battery_str}.json"
        
        save_topology(new_topology, new_name)


def update_topology_values(
    topology_file, 
    core_count_list, 
    core_speed_list, 
    memory_size_list, 
    host_count_list,
    apply_to_multiple_clusters
):

    topology_path = os.path.join("topologies", topology_file)

    try:
        with open(topology_path, 'r') as f:
            original_topology = json.load(f)
    except Exception as e:
        print(f"Failed to load topology {topology_file}: {e}")
        return
    
    core_count_list = core_count_list or []
    host_count_list = host_count_list or []
    core_speed_list = core_speed_list or []
    memory_size_list = memory_size_list or []

    max_len = max(len(core_count_list), len(core_speed_list), len(memory_size_list), len(host_count_list))

    if apply_to_multiple_clusters:
        new_topology = json.loads(json.dumps(original_topology))

        for i in range(max_len):
            core_count = get_val(core_count_list, i)
            core_speed = get_val(core_speed_list, i)
            memory_size = get_val(memory_size_list, i)
            host_count = get_val(host_count_list, i) 

            if i < len(new_topology["clusters"]):
                cluster = new_topology["clusters"][i]
            else:
                cluster = create_new_cluster(core_count, core_speed, memory_size, host_count)

            
            if core_count is not None:
                    cluster["hosts"][0]["cpu"]["coreCount"] = core_count 
            if core_speed is not None:
                cluster["hosts"][0]["cpu"]["coreSpeed"] = core_speed 
            if memory_size is not None:
                cluster["hosts"][0]["memory"]["memorySize"] = memory_size
            if host_count is not None: 
                cluster["hosts"][0]["count"] = host_count

            if i >= len(new_topology["clusters"]):
                new_topology["clusters"].append(cluster)

        base_topo = os.path.splitext(topology_file)[0]
        new_name = f"{base_topo}_multiple_clusters.json"
        save_topology(new_topology, new_name)

    
    else:
        
        for i in range(max_len):
            new_topology = json.loads(json.dumps(original_topology))

            core_count = get_val(core_count_list, i)
            core_speed = get_val(core_speed_list, i)
            memory_size = get_val(memory_size_list, i)
            host_count = get_val(host_count_list, i)  

            if "clusters" in new_topology:
                cluster = new_topology["clusters"][0]
                if core_count is not None:
                    cluster["hosts"][0]["cpu"]["coreCount"] = core_count 
                if core_speed is not None:
                    cluster["hosts"][0]["cpu"]["coreSpeed"] = core_speed 
                if memory_size is not None:
                    cluster["hosts"][0]["memory"]["memorySize"] = memory_size
                if host_count is not None: 
                    cluster["hosts"][0]["count"] = host_count
                
            else:
                new_topology["clusters"] = [create_new_cluster(core_count, core_speed, memory_size, host_count)]

            base_topo = os.path.splitext(topology_file)[0]
            cores_str = f"coreCount{core_count}_" if core_count is not None else ""
            speed_str = f"coreSpeed{core_speed}_" if core_speed is not None else ""
            memory_str = f"memSize{memory_size}_" if memory_size is not None else ""
            hosts_str = f"hosts{host_count}" if host_count is not None else ""

            new_name = f"{base_topo}{cores_str}{speed_str}{memory_str}{hosts_str}.json"
            save_topology(new_topology, new_name)



# -----------------------Helpers--------------------------------------------------------------------
# Creates a cluster with one host, could be further extended later based on specific topologies
def create_new_cluster(core_count, core_speed, memory_size, host_count): 
    return {
        "name": f"C1",
        "hosts": [
            {
                "name": "H1", 
                "cpu": {
                    "coreCount": core_count if core_count is not None else 16,
                    "coreSpeed": core_speed if core_speed is not None else 2100 
                },
                "memory": {
                    "memorySize": memory_size if memory_size is not None else 100000
                },
                "count": host_count if host_count else 1
            }
        ]
    }

# Refreshes the dropdown menu after file has been uploaded, currently used for experiment file update
def refresh_dropdown(dropdown, folder, selected=None, keep_original=True):
    files = os.listdir(folder)
    options = ['[Keep original]'] + files if keep_original else files
    dropdown.options = options
    if selected in files:
        dropdown.value = selected

def get_val(lst, idx):
    return lst[idx] if idx < len(lst) else None

# Helper function to parse input as a number, list, range
def parse_input(input_str):
    input_str = input_str.strip()
    if not input_str:
        return []
    
    if '-' in input_str and ':' in input_str:
        try:
            start_end, step = input_str.split(':')
            start, end = start_end.split('-')
            start, end, step = int(start), int(end), int(step)
            return frange(start, end, step)
        except Exception:
            return []
    

    elif ',' in input_str:
        parts = input_str.split(',')
        result = []
        for p in parts:
            p = p.strip()
            try:
                result.append(p)
            except ValueError:
                pass
        return result
    
    else:
        try:
            return [input_str]
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

#Saves topology
def save_topology(topology, new_name):

    new_path = os.path.join("topologies", new_name)
    try:
        with open(new_path, 'w') as f:
            json.dump(topology, f, indent=4)
        print(f"Generated {new_name}")
    except Exception as e:
        print(f"Error saving {new_name}: {e}")