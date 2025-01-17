import os
import re
from pathlib import Path
import subprocess


def add_shared_code_to_toml(shared_code_name):
    script = f"poetry add ./shared/{shared_code_name}"
    subprocess.call(script.split(" "))


def create_scraper_class(scraper_name):
    scraper_name_snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', scraper_name).lower()
    scraper_class_name = f"{scraper_name}Scraper"
    scraper_snake_case_name = f"{scraper_name_snake_case}_scraper"
    website_snake_case_name = scraper_name_snake_case

    os.mkdir(Path("shared", scraper_snake_case_name))

    with open(Path("shared", scraper_snake_case_name, "__init__.py"), "w") as file:
        pass

    # make pyproject.toml
    # first read the template file
    with open(Path("automations", "templates", "scraper", "pyproject.toml"), "r") as file:
        content = file.read()

    # replace placeholders
    content = content.replace("{{scraper_snake_case_name}}", scraper_snake_case_name)

    # write the content to the new file
    with open(Path("shared", scraper_snake_case_name, "pyproject.toml"), "w") as file:
        file.write(content)

    # make scraper class file
    with open(Path("automations", "templates", "scraper", "scraper_class.pyt"), "r") as file:
        content = file.read()

    content = content.replace("{{scraper_class_name}}", scraper_class_name)
    content = content.replace("{{scraper_snake_case_name}}", scraper_snake_case_name)
    content = content.replace("{{website_snake_case_name}}", website_snake_case_name)

    with open(Path("shared", scraper_snake_case_name, f"{scraper_snake_case_name}.py"), "w") as file:
        file.write(content)


def create_scraper_pipeline(scraper_name):
    scraper_name_snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', scraper_name).lower()
    scraper_class_name = f"{scraper_name}Scraper"
    scraper_snake_case_pipeline_name = f"{scraper_name_snake_case}_pipeline"
    website_snake_case_name = scraper_name_snake_case
    pipeline_dash_name = scraper_snake_case_pipeline_name.replace("_", "-")
    website_name = scraper_name
    scraper_download_function_name = f"download_{website_snake_case_name}_data"
    scraper_class_python_file = f"{scraper_name_snake_case}_scraper"

    os.mkdir(Path("pipelines", scraper_snake_case_pipeline_name))

    # make __init__.py empty file
    with open(Path("pipelines", scraper_snake_case_pipeline_name, "__init__.py"), "w") as file:
        pass

    # make prefect.yaml
    with open(Path("automations", "templates", "pipeline", "prefect.yaml"), "r") as file:
        content = file.read()

    content = content.replace("{{pipeline_dash_name}}", pipeline_dash_name)
    content = content.replace("{{website_name}}", website_name)
    content = content.replace("{{scraper_download_function_name}}", scraper_download_function_name)
    content = content.replace("{{scraper_class_name}}", scraper_class_name)
    content = content.replace("{{scraper_snake_case_name}}", scraper_name_snake_case)
    content = content.replace("{{website_snake_case_name}}", website_snake_case_name)
    content = content.replace("{{scraper_snake_case_pipeline_name}}", scraper_snake_case_pipeline_name)

    with open(Path("pipelines", scraper_snake_case_pipeline_name, "prefect.yaml"), "w") as file:
        file.write(content)

    # make pipeline file
    with open(Path("automations", "templates", "pipeline", "pipeline_name.pyt"), "r") as file:
        content = file.read()

    content = content.replace("{{scraper_class_python_file}}", scraper_class_python_file)
    content = content.replace("{{website_name}}", website_name)
    content = content.replace("{{scraper_class_name}}", scraper_class_name)
    content = content.replace("{{scraper_download_function_name}}", scraper_download_function_name)

    with open(Path("pipelines", scraper_snake_case_pipeline_name, f"{scraper_snake_case_pipeline_name}.py"),
              "w") as file:
        file.write(content)


def check_scraper_name_is_alphanumeric(scraper_name):
    if not re.match(r'^[a-zA-Z0-9]+$', scraper_name):
        raise Exception(
            f"Scraper name '{scraper_name}' should only contain alphanumeric characters")


def check_scraper_name_does_not_exist(scraper_name):
    scraper_names = [d.replace("_scraper_pipeline", "").lower() for d in os.listdir("pipelines") if
                     os.path.isdir(os.path.join(f"pipelines", d))]
    if scraper_name.lower() in scraper_names:
        raise Exception(f"Scraper name '{scraper_name}' Already exists!")


def check_scraper_name_validity(scraper_name):
    check_scraper_name_is_alphanumeric(scraper_name)
    check_scraper_name_does_not_exist(scraper_name)


def get_scraper_name():
    scraper_name = input("Enter the scraper name should be camelcase (e.g. Sreality, RealityIdnes, ArcherReality): ")
    check_scraper_name_validity(scraper_name)
    return scraper_name


if __name__ == "__main__":
    name = get_scraper_name()
    create_scraper_class(name)
    create_scraper_pipeline(name)

    scraper_name_snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    add_shared_code_to_toml(f"{scraper_name_snake_case}_scraper")
    print(f"Scraper {name} created successfully!")
