from etl_web_to_gcs import etl_web_to_gcs
from prefect.deployments import Deployment
from prefect.filesystems import GitHub



if __name__=="__main__":
    storage = github_block = GitHub.load("git")  # load a pre-defined block

    deployment = Deployment.build_from_flow(
        flow=etl_web_to_gcs,
        name="example-git-deployment",
        version=2,
        work_queue_name="example",
        storage=storage)

    deployment.apply()