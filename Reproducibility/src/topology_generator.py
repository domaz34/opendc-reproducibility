from src.utils import *

# Updates topology carbon field and batery field by taking a base topology, a list of carbons, number of hosts, lists of battery capacity and et.
# It will create different topology file for different carbon trace, if list lengths missmatch then it will just ignore the missing part
def update_topology_values(
    topology_file=None,
    core_count_list=None, 
    core_speed_list=None, 
    memory_size_list=None,
    multiple_clusters=False,
    carbon_list=None,
    NoH_list=None,
    battery_capacity_list=None,
    starting_CI_list=None,
    charging_speed_list=None,
    include_battery=False,
    name=None,
    power_model_type=None,
    power_model_idle=None,
    power_model_max=None,
    power_model_power=None
):
    if topology_file:
        topology_path = f"templates/topologies/{topology_file}"
        
        try:
            with open(topology_path, 'r') as f:
                original_topology = json.load(f)
        except Exception as e:
            print(f"Failed to load topology {topology_file}: {e}")
            return
    else:
        original_topology = {
                "clusters": [create_new_cluster(16, 2100,
                                               100000, 1, 0)]
            }
        
    
    carbon_list = carbon_list or []
    NoH_list = NoH_list or []
    battery_capacity_list = battery_capacity_list or []
    starting_CI_list = starting_CI_list or []
    charging_speed_list = charging_speed_list or []
    core_count_list = core_count_list or []
    core_speed_list = core_speed_list or []
    memory_size_list = memory_size_list or []
    
    max_len = max(
            len(core_count_list), len(core_speed_list), len(memory_size_list),
            len(carbon_list), len(NoH_list),
            len(battery_capacity_list), len(starting_CI_list), len(charging_speed_list),
            1
        )    

    # if multiple_clusters:
    #     for i in max_len:
    #         new_topology["clusters"].append(create_new_cluster(None, None, None, None, i))
    
    for i in range(max_len):
        new_topology = json.loads(json.dumps(original_topology))

        core_count = get_val(core_count_list, i)
        core_speed = get_val(core_speed_list, i)
        memory_size = get_val(memory_size_list, i)
        NoH = get_val(NoH_list, i)
        carbon = get_val(carbon_list, i)
        battery_capacity = get_val(battery_capacity_list, i)
        starting_CI = get_val(starting_CI_list, i)
        charging_speed = get_val(charging_speed_list, i)
        
        if "clusters" in new_topology:
            for cluster in new_topology["clusters"]:
                if carbon:
                    cluster["powerSource"] = {
                    "carbonTracePath": f"carbon_traces/{carbon}"
                    }
                
                if include_battery and battery_capacity is not None and starting_CI is not None and float(starting_CI) > 0:
                    cluster["battery"] = {
                    "capacity": int(battery_capacity),
                    "chargingSpeed": int(charging_speed) * int(battery_capacity) if charging_speed else 0,
                    "embodiedCarbon": 100 * int(battery_capacity),
                    "expectedLifetime": 10,
                    "batteryPolicy": {
                        "type": "runningMeanPlus",
                        "startingThreshold": float(starting_CI),
                        "windowSize": 168
                        }
                    }

                for host in cluster.get("hosts", []):
                    if core_count is not None:
                        host["cpu"]["coreCount"] = int(core_count)
                    if core_speed is not None: 
                        host["cpu"]["coreSpeed"] = int(core_speed)
                    if memory_size is not None:
                        host["memory"]["memorySize"] = int(memory_size)
                    if NoH is not None:
                        host["count"] = int(NoH)
                    if power_model_type is not None:
                        power_model = {"modelType": power_model_type}

                        if power_model_power is not None:
                            power_model["power"] = float(power_model_power)
                        if power_model_idle is not None:
                            power_model["idlePower"] = float(power_model_idle)
                        if power_model_max:
                            power_model["maxPower"] = float(power_model_max)
                        
                        host["powerModel"] = power_model

        
        path = build_topology_path(carbon = carbon,
                                    NoH = NoH,
                                    battery_capacity = battery_capacity,
                                    include_battery = include_battery,
                                    core_count = core_count,
                                    core_speed = core_speed,
                                    memory_size = memory_size,
                                    name = name
                                )
                                                

        save_topology(new_topology, path)
  
        

# Function that is responsible for naming, feel free to adjust based on your taste
def build_topology_path(
    carbon,
    NoH,
    battery_capacity,
    include_battery,
    core_count,
    core_speed,
    memory_size,
    name
):
    # Folder structure
    path_parts = []
    if carbon:
        path_parts.append(f"carbon-{os.path.splitext(carbon)[0]}")
    if NoH is not None:
        path_parts.append(f"hosts{NoH}")
    if include_battery and battery_capacity is not None:
        path_parts.append(f"bat{battery_capacity}")

    # Filename
    feature_bits = []
    if core_count is not None:
        feature_bits.append(f"core{core_count}")
    if core_speed is not None:
        feature_bits.append(f"speed{core_speed}")
    if memory_size is not None:
        feature_bits.append(f"mem{memory_size}")

    
    if name:
        default_name = f"{name}.json"
    else:
        default_name = "topology.json"
    fname = "_".join(feature_bits) + f"_{default_name}" if feature_bits else default_name

    return "/".join(path_parts + [fname])

def update_topology_values_old(
    topology_file, 
    core_count_list, 
    core_speed_list, 
    memory_size_list, 
    host_count_list,
    apply_to_multiple_clusters
):

    topology_path = f"topologies/{topology_file}"

    try:
        with open(topology_path, 'r') as f:
            original_topology = json.load(f)
    except Exception as e:
        print(f"Failed to load topology {topology_file}: {e}")
        return
    

    max_len = max()

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
                cluster = create_new_cluster(core_count, core_speed, memory_size, host_count, i)

            
            if core_count is not None:
                    cluster["hosts"][0]["cpu"]["coreCount"] = int(core_count) 
            if core_speed is not None:
                cluster["hosts"][0]["cpu"]["coreSpeed"] = int(core_speed)
            if memory_size is not None:
                cluster["hosts"][0]["memory"]["memorySize"] = int(memory_size)
            if host_count is not None: 
                cluster["hosts"][0]["count"] = int(host_count)

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
                new_topology["clusters"] = [create_new_cluster(core_count, core_speed, memory_size, host_count, i)]

            base_topo = os.path.splitext(topology_file)[0]
            cores_str = f"coreCount{core_count}_" if core_count is not None else ""
            speed_str = f"coreSpeed{core_speed}_" if core_speed is not None else ""
            memory_str = f"memSize{memory_size}_" if memory_size is not None else ""
            hosts_str = f"hosts{host_count}" if host_count is not None else ""

            new_name = f"{base_topo}_{cores_str}{speed_str}{memory_str}{hosts_str}.json"
            save_topology(new_topology, new_name)


# Creates a cluster with one host, could be further extended later based on specific topologies
def create_new_cluster(core_count, core_speed, memory_size, host_count, index): 
    return {
        "name": f"C{index}",
        "hosts": [
            {
                "name": f"H{index}", 
                "cpu": {
                    "coreCount": core_count,
                    "coreSpeed": core_speed,
                },
                "memory": {
                    "memorySize": memory_size,
                },
                "count": host_count
            }
        ]
    }

# Saves topology on provided path
def save_topology(topology: dict, rel_path: str):
    full_path = f"topologies/{rel_path}"
    os.makedirs(os.path.dirname(full_path), exist_ok=True)  
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(topology, f, indent=4)
    print(f"Generated {rel_path}")