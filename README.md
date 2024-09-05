# Overview

This repository contains a demo Prefect flow that clones a dbt project and runs dbt Core commands as Prefect tasks. 

The flow at `duckdb-flow.py` clones a fork of dbt Labs' Jaffle Shop example, but with duckdb so it doesn't require connecting to a data warehouse.  

![Flow Run](images/flow.png)

## Setup and installation

Clone the repository
I used `uv` for this demo.

After creating a virtual environment, install the requirements.
`uv pip install -r requirements.txt`

## Usage

Once installed, run `python duckdb-flow.py` to run the flow and dbt tasks. 

The cloned repository, https://github.com/seanpwlms/jaffle_shop_duckdb.git has another branch, `model_error` so you can see what a failure looks like as a Prefect artifact. Cloning different branches can also be combined with prefect web hooks as the basis for dbt Core CI jobs

![Example Artifact](images/artifact.png)

To use this with your own dbt project repository, replace the URL in the `clone_dbt_repo` function and add [credentials](https://docs-3.prefect.io/integrations/prefect-github/index)

### Deploying 

Let's use Prefect's serverless execution environment.  First, create a Prefect Managed work pool.  

`prefect work-pool create managed-pool --type prefect:managed`

We could modify `duckdb-flow.py` to deploy via Python:

```python
if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/seanpwlms/prefect-dbt-deployment.git",
        entrypoint="duckdb-flow.py:dbt_build_flow",
    ).deploy(
        name="test-managed-flow",
        work_pool_name="managed-pool",
        job_variables = {
    "pip_packages": [
        "prefect==3.0.0",
        "prefect-dbt==0.6.0",
        "prefect-github==0.3.0",
        "dbt-duckdb==1.8.3",
        "google-auth==2.34.0",
        "duckdb==1.0.0"
    ]
}
    )
```

But, because the repo has a `requirements.txt` file, it's easier to install the requirements as a part of the pull step in `prefect.yaml`.

Create a deployment without a schedule:

`prefect deploy --name dbt_flow_ad_hoc`

Or, deploy the flow with a daily schedule:

`prefect deploy --name dbt_flow_daily`

Then, have a look at the deployments in Prefect Cloud.

![deployments](images/deployments.png)