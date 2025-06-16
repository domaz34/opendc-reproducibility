import os
import json
import platform
import psutil
import socket

# Cleans the selection list by adding all selections or keeping the original selections based on the user selected values
def clean_selection(selections, full_options):
    if not selections:
        return None

    if "[Select All]" in selections:
        return [opt for opt in full_options if opt not in ("[Keep original]", "[Select All]")]

    filtered = [s for s in selections if s not in ("[Keep original]", "[Select All]")]
    return filtered if filtered else None   


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

def list_topology_files(root="topologies"):
    topo_files = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".json"):
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                topo_files.append(rel)
    return topo_files

# Function to create a list from range
def frange(start, end, step):
    result = []
    current = start
    while current <= end:
        result.append(round(current, 8))
        current += step
    return result

# Lists directory only if it exists
def safe_listdir(path):
    return os.listdir(path) if os.path.exists(path) else []

# Gets system info for readme
def get_system_info():
    cpu_info = {
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cores": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True),
        "memory_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
    }

    return cpu_info