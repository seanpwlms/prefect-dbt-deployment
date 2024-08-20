from prefect import flow, task
from prefect_github import GitHubRepository
from prefect_dbt.cli.commands import trigger_dbt_cli_command
from pathlib import Path
from enum import Enum
from typing import Optional
import os

from pathlib import Path


class Branch(Enum):
    MAIN = "duckdb"
    FAIL = "model_error"


@task(name="clone the repo")
def clone_dbt_repo(destination_path: str, reference: str = "duckdb"):
    """Clones public repo. Specify branch or reference and where to store it locally"""
    dbt_repo_url = "https://github.com/seanpwlms/jaffle_shop_duckdb.git"
    repository = GitHubRepository(repository_url=dbt_repo_url, reference=reference)
    repository.get_directory(local_path=destination_path)


def dbt_deps():
    """install dependencies"""
    trigger_dbt_cli_command(command="dbt deps", project_dir="./dbt", profiles_dir=".")


def get_dbt_paths(profiles_dir: str = "./dbt", project_dir: str = "./dbt"):
    """resolve paths and validate profiles.yml is found"""
    profiles_dir = str(Path(profiles_dir).resolve())
    project_dir = str(Path(project_dir).resolve())
    assert os.path.exists(f"{profiles_dir}/profiles.yml")
    return profiles_dir, project_dir


@flow
def dbt_build_flow(
    branch: Optional[Branch] = Branch.MAIN, destination_path: Optional[str] = "./dbt"
):
    """Clone and run dbt project"""
    if not os.path.isdir(destination_path):
        clone_dbt_repo(destination_path=destination_path, reference=branch)

    profiles_dir, project_dir = get_dbt_paths()
    trigger_dbt_cli_command(
        command="dbt seed",
        project_dir=project_dir,
        profiles_dir=profiles_dir,
    )
    trigger_dbt_cli_command(
        command="dbt deps",
        project_dir=project_dir,
        profiles_dir=profiles_dir,
    )
    trigger_dbt_cli_command(
        command="dbt build",
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        create_summary_artifact=True,
        summary_artifact_key="dbt-build-task-summary",
    )


if __name__ == "__main__":
    dbt_build_flow()
