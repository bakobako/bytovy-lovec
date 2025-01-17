import subprocess
import toml


def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed with error: {e}")
        return None


def get_shared_dependencies(file_path):
    with open(file_path, "r") as file:
        data = toml.load(file)
        dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        shared_dependencies = [dep for dep, value in dependencies.items() if
                               isinstance(value, dict) and value.get("path", "").startswith("shared")]
        return shared_dependencies


def get_pipeline_dependencies(file_path):
    with open(file_path, "r") as file:
        data = toml.load(file)
        dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        pipeline_dependencies = [dep for dep, value in dependencies.items() if
                                 isinstance(value, dict) and value.get("path", "").startswith("pipelines")]
        return pipeline_dependencies


if __name__ == "__main__":
    shared_dependencies = get_shared_dependencies("pyproject.toml")
    for shared_dependency in shared_dependencies:
        print(f"Uninstalling {shared_dependency} ")
        execute_command(f"pip uninstall -y {shared_dependency}")
    pipeline_dependencies = get_pipeline_dependencies("pyproject.toml")
    for pipeline_dependency in pipeline_dependencies:
        print(f"Uninstalling {pipeline_dependency} ")
        execute_command(f"pip uninstall -y {pipeline_dependency}")
    print("Reinstalling everything...")
    execute_command("poetry install")
