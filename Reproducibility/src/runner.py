import subprocess
import json
import os



def run_experiment(path):
    print("Running simulation...")
    result = subprocess.run(
        ["OpenDCExperimentRunner/bin/OpenDCExperimentRunner", "--experiment-path", path],
        capture_output=True,
        text=True
    )
    print("Return code:", result.returncode)
    print("STDERR:\n", result.stderr)

