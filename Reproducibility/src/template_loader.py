import json
import os

def load_experiment_template(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading template: {e}")
        return None


def save_json_file(fileinfo, filename, folder):
    path = f"{folder}{filename}.json"
    with open(path, "w") as f:
        json.dump(fileinfo, f, indent=4)
    return filename

def save_uploaded_file(upload_widget, folder, extract_if_zip=False):
    if not upload_widget.value:
        return None

    os.makedirs(folder, exist_ok=True)
    fileinfo = upload_widget.value[0]
    fname = fileinfo['name']
    
    path = os.path.join(folder, fname)

    with open(path, "wb") as f:
        f.write(fileinfo['content'])
    
    return fname
