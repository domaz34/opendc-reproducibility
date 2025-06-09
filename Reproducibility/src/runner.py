import os
import sys
import subprocess

def run_experiment(path):
    print("Running simulation...")

    if not os.path.exists(path):
        print(f"ERROR: Experiment file not found at {path}")
        return

    experiment_path = os.path.abspath(path)

    if sys.platform.startswith("win"):
        lib_dir = os.path.abspath("OpenDCExperimentRunner/lib")
        classpath = ";".join([
            os.path.join(lib_dir, f) for f in os.listdir(lib_dir) if f.endswith(".jar")
        ])

        java_cmd = [
            "java",
            "-classpath", classpath,
            "org.opendc.experiments.base.runner.ExperimentCli",
            "--experiment-path", experiment_path
        ]

        try:
            result = subprocess.run(java_cmd, capture_output=True, text=True)
            if result.stderr is not "":
                print("STDERR:\n", result.stderr)
        except Exception as e:
            print(f"Failed to run experiment: {e}")


    elif sys.platform.startswith("linux"):
        runner_path = "OpenDCExperimentRunner/bin/OpenDCExperimentRunner"
        if not os.path.exists(runner_path):
            print(f"ERROR: Runner not found at {runner_path}")
            return

        try:
            result = subprocess.run([runner_path, "--experiment-path", experiment_path], capture_output=True, text=True)
            if result.stderr:
                print("STDERR:\n", result.stderr)
                print("Experiment status: ")
        except Exception as e:
            print(f"Failed to run experiment: {e}")

    else:
        print("ERROR: Unsupported OS. This runner supports Windows and Linux")

def run_all_experiments(experiment_queue):
    if not experiment_queue:
        print("No experiments added")
        return
        
    print("Running all queued experiments...")
            
    for exp in experiment_queue:
                
        filename = exp["name"]
        print(f"Running: {filename}")
        exec_path = f"experiments/{filename}"
        run_experiment(exec_path)


    experiment_queue.clear()
    print("All experiments completed.")