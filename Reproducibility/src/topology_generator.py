from src.utils import *
from itertools import product
import json

def generate_with_named_pairs(new_topology, pairs, inputs, other_params):
    """
    Generate and save topologies using zipped parameter pairs and Cartesian product with remaining parameters.
    It treats one pair as one distinct variable that is later combined with other variables using product.

    Args:
        new_topology: Base topology structure to clone and modify.
        pairs: List of parameter name pairs to zip together (e.g., [('carbon', 'starting_CI')]).
        inputs: Dictionary mapping parameter names to value lists.
        other_params : Constant or additional metadata fields passed to `build_one_topology`.
    """

    if not pairs:
        return

    zipped_groups = []
    zipped_keys = set()

    for param1, param2 in pairs:
        if param1 not in inputs or param2 not in inputs:
            print(f"[Skipped] Pair ({param1}, {param2}) not found in inputs.")
            continue
        list1, list2 = inputs[param1], inputs[param2]
        if len(list1) != len(list2):
            print(f"[Skipped] Pair ({param1}, {param2}) has unequal lengths.")
            continue
        zipped_groups.append(list(zip(list1, list2)))
        zipped_keys.update([param1, param2])

    zipped_product = list(product(*zipped_groups)) 

    product_inputs = {k: v for k, v in inputs.items() if k not in zipped_keys and v}
    product_keys = list(product_inputs.keys())
    product_values = [product_inputs[k] for k in product_keys]

    for zipped_combo in zipped_product:
        base_args = {}
        for (k1, k2), (v1, v2) in zip(pairs, zipped_combo):
            base_args[k1] = v1
            base_args[k2] = v2

        for combo in product(*product_values) if product_values else [()]:
            args = base_args.copy()
            args.update(dict(zip(product_keys, combo)))

            topology_copy = json.loads(json.dumps(new_topology))
            build_one_topology(
                new_topology=topology_copy,
                core_count=args.get("core_count"),
                core_speed=args.get("core_speed"),
                memory_size=args.get("memory_size"),
                carbon=args.get("carbon"),
                NoH=args.get("NoH"),
                battery_capacity=args.get("battery_capacity"),
                starting_CI=args.get("starting_CI"),
                charging_speed=args.get("charging_speed"),
                expected_lifetime=args.get("expected_lifetime"),
                include_battery=other_params.get("include_battery"),
                name=other_params.get("name"),
                power_model_type=other_params.get("power_model_type"),
                power_model_idle=other_params.get("power_model_idle"),
                power_model_max=other_params.get("power_model_max"),
                power_model_power=other_params.get("power_model_power"),
                add_power_model=other_params.get("add_power_model"),
                prepend=other_params.get("prepend")
            )



def update_topology_values(
    topo_template_path=None,
    topology_file=None,
    core_count_list=None, 
    core_speed_list=None, 
    memory_size_list=None,
    carbon_list=None,
    NoH_list=None,
    battery_capacity_list=None,
    starting_CI_list=None,
    charging_speed_list=None,
    expected_lifetime_list=None,
    include_battery=False,
    name=None,
    power_model_type=None,
    power_model_idle=None,
    power_model_max=None,
    power_model_power=None,
    add_power_model=False,
    generate_combinations=False,
    pairs=None,
    prepend=False
):
    """
    Generate and save new topology files based on provided variations.

    If a topology file is provided, it is used as the base template. Otherwise,
    a default one-cluster topology is generated. New topologies are created by 
    iterating over the provided lists or by generating combinations if enabled.

    - If generate_combinations is True, creates a topology for each unique combination.
    - If False, aligns values by index across lists.
    - Only non-empty inputs are used in combination generation.
    - Carbon traces and battery configs are added to clusters if provided.
    - Power model is added to hosts if enabled.

    Saves each generated topology under a structured path reflecting its parameters.
    """

    if topology_file:
        topology_path = f"{topo_template_path}{topology_file}"
        try:
            with open(topology_path, 'r') as f:
                original_topology = json.load(f)
        except Exception as e:
            print(f"Failed to load topology {topology_file}: {e}")
            return
    else:
        original_topology = {
            "clusters": [create_new_cluster(16, 2100, 100000, 1, 0)]
        }

    
    carbon_list = carbon_list or []
    NoH_list = NoH_list or []
    battery_capacity_list = battery_capacity_list or []
    starting_CI_list = starting_CI_list or []
    charging_speed_list = charging_speed_list or []
    expected_lifetime_list = expected_lifetime_list or []
    core_count_list = core_count_list or []
    core_speed_list = core_speed_list or []
    memory_size_list = memory_size_list or []

    if generate_combinations:
        inputs = {
            "carbon": carbon_list,
            "NoH": NoH_list,
            "battery_capacity": battery_capacity_list,
            "starting_CI": starting_CI_list,
            "charging_speed": charging_speed_list,
            "expected_lifetime": expected_lifetime_list,
            "core_count": core_count_list,
            "core_speed": core_speed_list,
            "memory_size": memory_size_list
        }

        if pairs:
            generate_with_named_pairs(
                new_topology=original_topology,
                pairs=pairs,
                inputs=inputs,
                other_params={
                    "include_battery": include_battery,
                    "name": name,
                    "power_model_type": power_model_type,
                    "power_model_idle": power_model_idle,
                    "power_model_max": power_model_max,
                    "power_model_power": power_model_power,
                    "add_power_model": add_power_model,
                    "prepend": prepend
                }
            )

        else:
            active = {key: value for key, value in inputs.items() if value}

            keys, lists = zip(*active.items())

            seen = set()
            for combo in product(*lists):
                if None in combo:
                    continue
                if combo in seen:
                    continue
                seen.add(combo)
            
                values = dict(zip(keys, combo))

                new_topology = json.loads(json.dumps(original_topology))
                build_one_topology(
                    new_topology=new_topology,
                    core_count=values.get("core_count"),
                    core_speed=values.get("core_speed"),
                    memory_size=values.get("memory_size"),
                    carbon=values.get("carbon"),
                    NoH=values.get("NoH"),
                    battery_capacity=values.get("battery_capacity"),
                    starting_CI=values.get("starting_CI"),
                    charging_speed=values.get("charging_speed"),
                    expected_lifetime=values.get("expected_lifetime"),
                    include_battery=include_battery,
                    name=name,
                    power_model_type=power_model_type,
                    power_model_idle=power_model_idle,
                    power_model_max=power_model_max,
                    power_model_power=power_model_power,
                    add_power_model=add_power_model,
                    prepend=prepend
                )
    else:
        max_len = max(
            len(core_count_list), len(core_speed_list), len(memory_size_list),
            len(carbon_list), len(NoH_list),
            len(battery_capacity_list), len(starting_CI_list), len(charging_speed_list),
            1
        )

        for i in range(max_len):
            core_count = get_val(core_count_list, i)
            core_speed = get_val(core_speed_list, i)
            memory_size = get_val(memory_size_list, i)
            NoH = get_val(NoH_list, i)
            carbon = get_val(carbon_list, i)
            battery_capacity = get_val(battery_capacity_list, i)
            starting_CI = get_val(starting_CI_list, i)
            charging_speed = get_val(charging_speed_list, i)
            expected_lifetime = get_val(expected_lifetime_list, i)

            new_topology = json.loads(json.dumps(original_topology))
            build_one_topology(
                new_topology=new_topology,
                core_count=core_count,
                core_speed=core_speed,
                memory_size=memory_size,
                carbon=carbon,
                NoH=NoH,
                battery_capacity=battery_capacity,
                starting_CI=starting_CI,
                charging_speed=charging_speed,
                expected_lifetime=expected_lifetime,
                include_battery=include_battery,
                name=name,
                power_model_type=power_model_type,
                power_model_idle=power_model_idle,
                power_model_max=power_model_max,
                power_model_power=power_model_power,
                add_power_model=add_power_model,
                prepend=prepend
            )

        
def build_one_topology(new_topology,
                        core_count, core_speed, memory_size,
                        carbon, NoH,
                        battery_capacity, starting_CI, charging_speed, expected_lifetime,
                        include_battery, name,
                        power_model_type, power_model_idle,
                        power_model_max, power_model_power, add_power_model, prepend):
    
    """
    Populate and save a single topology configuration based on inputs.

    Applies cluster-level and host-level settings including carbon trace, battery,
    power model, and compute specs. Naming is handled automatically.

    """
    
    if "clusters" in new_topology:
            for cluster in new_topology["clusters"]:
                if carbon:
                    cluster["powerSource"] = {
                    "carbonTracePath": f"carbon_traces/{carbon}"
                    }
                
                if include_battery:
                    bat = cluster.get("battery")
                    if bat:
                        if battery_capacity is not None:
                            bat["capacity"] = int(battery_capacity)
                        if charging_speed is not None:
                            bat["chargingSpeed"] = int(charging_speed) * bat.get("capacity", 0)
                        if expected_lifetime is not None:
                            bat["expectedLifetime"] = int(expected_lifetime)

                    elif battery_capacity is not None and starting_CI is not None and float(starting_CI) > 0:
                        cluster["battery"] = {
                            "capacity": int(battery_capacity),
                            "chargingSpeed": int(charging_speed) * int(battery_capacity) if charging_speed else 0,
                            "embodiedCarbon": 100 * int(battery_capacity),
                            "expectedLifetime": int(expected_lifetime) if int(expected_lifetime) is not None else 10
                        }

                    if "batteryPolicy" not in cluster["battery"]:
                            cluster["battery"]["batteryPolicy"] = {
                                "type": "runningMeanPlus",
                                "startingThreshold": float(starting_CI),
                                "windowSize": 168
                            }
                        
                    elif starting_CI is not None:
                        cluster["battery"]["batteryPolicy"]["startingThreshold"] = float(starting_CI)

                for host in cluster.get("hosts", []):
                    if core_count is not None:
                        host["cpu"]["coreCount"] = int(core_count)
                    if core_speed is not None: 
                        host["cpu"]["coreSpeed"] = int(core_speed)
                    if memory_size is not None:
                        host["memory"]["memorySize"] = int(memory_size)
                    if NoH is not None:
                        host["count"] = int(NoH)

                    if add_power_model:
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
                                    charging_speed=charging_speed,
                                    include_battery = include_battery,
                                    core_count = core_count,
                                    core_speed = core_speed,
                                    memory_size = memory_size,
                                    name = name,
                                    prepend=prepend
                                )
                                                

    save_topology(new_topology, path)
  
        

def build_topology_path(
    carbon,
    NoH,
    battery_capacity,
    charging_speed,
    include_battery,
    core_count,
    core_speed,
    memory_size,
    name,
    prepend=False
):
    
    """
    Construct a relative file path for a generated topology file.

    Path is built using the most relevant features (e.g. NoH, battery, carbon, CPU settings).
    File name is composed using name and other hardware specs.
    Feel free to adjust to your taste.

    Returns:
        Relative file path to use when saving the topology.
    """

    # Folder structure
    path_parts = []
    if prepend:
        path_parts.append(name)
    if NoH is not None:
        path_parts.append(f"hosts{NoH}")
    if include_battery and battery_capacity is not None and charging_speed is not None:
        path_parts.append(f"bat{battery_capacity}_{charging_speed}")
    if carbon:
        path_parts.append(f"carbon-{os.path.splitext(carbon)[0]}")
    
    
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



def create_new_cluster(core_count, core_speed, memory_size, host_count, index): 
    """
    Create a default cluster with a single host entry.

    Returns:
        A cluster dictionary structure to be included in the topology.
    """

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


def save_topology(topology: dict, rel_path: str):

    """
    Save a topology dictionary to disk under the topologies/ directory.

    Creates subfolders as necessary.
    """
    
    full_path = f"topologies/{rel_path}"
    os.makedirs(os.path.dirname(full_path), exist_ok=True)  
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(topology, f, indent=4)
    #print(f"Generated {rel_path}") disabled for large scale experiments