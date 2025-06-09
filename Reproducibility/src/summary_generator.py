# import os
# import json


# def generate_readme_from_queue(experiment_queue, output_path="README.md"):
#     readme_lines = [
#         "# Reproducibility Capsule",
#         "",
#         "This capsule contains all artifacts needed to reproduce the experiments listed below using OpenDC.",
#         "",
#         "## Experiments Overview",
#         ""
#     ]

#     for i, exp in enumerate(experiment_queue, start=1):
#         name = exp["name"]
#         readme_lines.append(f"### Experiment {i}: `{name}`")

#         topologies = exp.get("topology")
#         workloads = exp.get("workload")
#         failures = exp.get("failures")

#         readme_lines.append("- **Topologies**: " + ", ".join(topologies))
#         readme_lines.append("- **Workloads**: " + ", ".join(workloads))
#         if failures:
#             readme_lines.append("- **Failures**: " + ", ".join(failures))
#         readme_lines.append("")

#     readme_lines += [
#         "## How to Run",
#         "",
#         "1. Open `main.ipynb` in a Jupyter environment.",
#         "2. Click **'Run All Experiments'** to execute everything in the queue.",
#         "3. Outputs will appear in the `output/` directory.",
#         "",
#         "You can also customize and build on top of the experiments provided using the same notebook and following the instructions.",
#         "",
#         "## Folder Structure",
#         "",
#         "- `experiments/`: Contains the experiment JSON files.",
#         "- `topologies/`: Topology definitions.",
#         "- `workload_traces/`: Workload files.",
#         "- `failure_traces/`: Failure definitions.",
#         "- `output/`: Simulation outputs (auto-created).",
#         "- `main.ipynb`: Notebook interface to run and manage experiments.",
#         "- `src/`: Custom utility code.",
#         "- `OpenDCExperimentRunner/`: Compiled experiment runner.",
#         "",
#         "## License",
#         "",
#         "This capsule is intended for academic use and evaluation of OpenDC-based experiments."
#     ]

#     try:
#         with open(output_path, "w") as f:
#             f.write("\n".join(readme_lines))
#         print(f"README generated at {output_path}")
#     except Exception as e:
#         print(f"Failed to generate README: {e}")

#     return output_path

import os
import json

def generate_readme_from_queue(experiment_queue, output_path="README.md", experiments_dir="experiments"):
    readme_lines = [
        "# Reproducibility Capsule",
        "",
        "This capsule contains all artifacts needed to reproduce the experiments listed below using OpenDC.",
        "",
        "## Experiments Overview",
        ""
    ]

    for i, exp in enumerate(experiment_queue, start=1):
        name = exp["name"]
        readme_lines.append(f"### Experiment {i}: `{name}`")

        exp_path = f"{experiments_dir}/{name}"
        try:
            with open(exp_path) as f:
                data = json.load(f)
        except Exception as e:
            readme_lines.append("")
            continue

        topologies = [t["pathToFile"] for t in data.get("topologies", [])]
        workloads = [w["pathToFile"] for w in data.get("workloads", [])]
        failures = [f["pathToFile"] for f in data.get("failureModels", [])]

        if topologies:
            readme_lines.append("- **Topologies**: " + ", ".join(topologies))
        if workloads:
            readme_lines.append("- **Workloads**: " + ", ".join(workloads))
        if failures:
            readme_lines.append("- **Failures**: " + ", ".join(failures) if failures else "- **Failures**: []")
        readme_lines.append("")

    readme_lines += [
        "## How to Run",
        "",
        "1. Open `main.ipynb` in a Jupyter environment.",
        "2. Click **'Run All Experiments'** to execute everything in the queue.",
        "3. Outputs will appear in the `output/` directory.",
        "",
        "You can also customize and build on top of the experiments provided using the same notebook and following the instructions.",
        "",
        "## Folder Structure",
        "",
        "- `experiments/`: Contains the experiment JSON files.",
        "- `topologies/`: Topology definitions.",
        "- `workload_traces/`: Workload files.",
        "- `failure_traces/`: Failure definitions.",
        "- `output/`: Simulation outputs (auto-created).",
        "- `main.ipynb`: Notebook interface to run and manage experiments.",
        "- `src/`: Custom utility code.",
        "- `OpenDCExperimentRunner/`: Compiled experiment runner.",
        ""
    ]

    try:
        with open(output_path, "w") as f:
            f.write("\n".join(readme_lines))
        print(f"README generated at {output_path}")
    except Exception as e:
        print(f"Failed to generate README: {e}")

    return output_path
