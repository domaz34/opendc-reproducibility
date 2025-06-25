import os
import json
import platform
import psutil
import socket

# Cleans the selection list by adding all selections or keeping the original selections based on the user selected values
def clean_selection(selections, full_options):
    if not selections:
        return None

    def is_valid(opt):
        return opt not in ("[Keep original]", "[Select All]") and not opt.endswith(".gitkeep")

    if "[Select All]" in selections:
        return [opt for opt in full_options if is_valid(opt)]

    filtered = [s for s in selections if is_valid(s)]
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

# Helper function to parse input as a number, list, range, returns string and the casting is done later where convenient
def parse_input(input_str):
    input_str = input_str.strip()
    if not input_str:
        return []

    segments = [s.strip() for s in input_str.split('+')]
    result = []

    for segment in segments:
        if '-' in segment and ':' in segment:
            start_end, step = segment.split(':')
            start, end = start_end.split('-')
            result += [str(v) for v in frange(int(start), int(end), int(step))]

        elif ',' in segment:
            result += [s.strip() for s in segment.split(',')]

        else:
            result.append(segment)

    return result


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