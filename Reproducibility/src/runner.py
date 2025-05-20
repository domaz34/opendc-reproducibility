import subprocess
import os



# def run_experiment(path):
#     print("Running simulation...")

#     if not os.path.exists(path):
#         print(f"ERROR: Experiment file not found at {path}")
#         return

#     system = platform.system()
#     if system == "Windows":
#         runner_path = os.path.abspath("OpenDCExperimentRunner/bin/OpenDCExperimentRunner.bat")
#         command = f'"{runner_path}" --experiment-path "{path}"'

#     else:
#         runner_path = os.path.abspath("OpenDCExperimentRunner/bin/OpenDCExperimentRunner")
#         command = [runner_path, "--experiment-path", path]

#     if not os.path.exists(runner_path):
#         print(f"ERROR: Runner not found at {runner_path}")
#         return

#     try:
#         result = subprocess.run(
#             command,
#             capture_output=True,
#             text=True
#         )
#         print("Return code:", result.returncode)
#         print("STDOUT:\n", result.stdout)
#         print("STDERR:\n", result.stderr)
#     except Exception as e:
#         print(f"Failed to run experiment: {e}")

def run_experiment(path):
    print("Running simulation...")

    if not os.path.exists(path):
        print(f"ERROR: Experiment file not found at {path}")
        return

    experiment_path = os.path.abspath(path)
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
        print("Return code:", result.returncode)
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
    except Exception as e:
        print(f"Failed to run experiment: {e}")


def run_all_experiments(experiment_queue):
    if not experiment_queue:
        print("No experiments added")
        return
        
    print("Running all queued experiments...")
            
    for exp in experiment_queue:
                
        filename = exp["name"]
        print(f"Running: {filename}")
        exec_path = os.path.join("experiments", f"{filename}")
        run_experiment(exec_path)


    experiment_queue.clear()
    print("All experiments completed.")