"""
Submit Training Job to Azure ML Compute

This script demonstrates how to submit a training job to Azure ML compute.
The job will run on cloud compute and automatically log to MLflow.

For interview prep: Understand the job submission workflow and how
Azure ML integrates with MLflow automatically.
"""

from azure.ai.ml import MLClient, command, Input
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Environment
import os


def submit_training_job(
    ml_client,
    compute_name="training-cluster",
    experiment_name="azure-training-demo"
):
    """
    Submit a training job to Azure ML compute.

    Interview tip: This is how you run training at scale in Azure ML!
    - Your code runs on cloud compute (not your laptop)
    - MLflow tracking is automatic
    - Results appear in Azure ML Studio

    Args:
        ml_client: Azure ML client
        compute_name: Name of compute cluster to use
        experiment_name: Name of experiment for organization
    """
    print("="*60)
    print("Submitting Training Job to Azure ML")
    print("="*60)

    # Define the training job
    # Interview tip: The 'command' function defines what to run and where
    job = command(
        # Code to run
        code="./src",  # Local directory with your training code
        command="python train.py --epochs 10 --lr 0.01",

        # Environment
        # Option 1: Use curated environment (recommended for interviews)
        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",

        # Option 2: Use custom environment (more control)
        # environment=Environment(
        #     name="custom-sklearn",
        #     conda_file="conda.yaml",
        #     image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04"
        # ),

        # Compute target
        # Interview tip: This is where the job runs!
        # Compute Instance = single-user dev VM
        # Compute Cluster = auto-scaling multi-node (recommended for training)
        compute=compute_name,

        # Experiment name
        # Interview tip: Groups related runs together
        experiment_name=experiment_name,

        # Display name for the run
        display_name="elasticnet-training-run",

        # Description
        description="Training ElasticNet model with MLflow tracking"
    )

    print(f"Job configuration:")
    print(f"  Code location: ./src")
    print(f"  Command: python train.py --epochs 10 --lr 0.01")
    print(f"  Compute: {compute_name}")
    print(f"  Experiment: {experiment_name}")

    # Submit the job
    print(f"\nSubmitting job...")
    returned_job = ml_client.jobs.create_or_update(job)

    print(f"\n✓ Job submitted!")
    print(f"  Job name: {returned_job.name}")
    print(f"  Status: {returned_job.status}")

    # Get job URL
    studio_url = returned_job.studio_url
    print(f"\n  View in Azure ML Studio:")
    print(f"  {studio_url}")

    return returned_job


def submit_job_with_data(ml_client, compute_name="training-cluster"):
    """
    Submit a training job that uses registered Data Assets.

    Interview tip: Data Assets provide versioning and lineage for datasets.
    Much better than hardcoded file paths!
    """
    print("\n" + "="*60)
    print("Submitting Job with Data Asset")
    print("="*60)

    job = command(
        code="./src",
        command="python train.py --data ${{inputs.training_data}}",

        # Input data from Azure ML Data Assets
        # Interview tip: Reference data by name:version for reproducibility
        inputs={
            "training_data": Input(
                type="uri_file",
                path="azureml:housing-data:1"  # azureml:NAME:VERSION
            )
        },

        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
        compute=compute_name,
        experiment_name="azure-training-with-data"
    )

    print(f"Job configuration:")
    print(f"  Input data: azureml:housing-data:1")
    print(f"  (This references a versioned Data Asset)")

    returned_job = ml_client.jobs.create_or_update(job)

    print(f"\n✓ Job submitted: {returned_job.name}")
    print(f"  {returned_job.studio_url}")

    return returned_job


def submit_sweep_job(ml_client, compute_name="training-cluster"):
    """
    Submit a hyperparameter sweep job.

    Interview tip: Azure ML has built-in hyperparameter tuning!
    Automatically runs multiple trials with different parameters.
    """
    from azure.ai.ml.sweep import Choice, Uniform

    print("\n" + "="*60)
    print("Submitting Hyperparameter Sweep Job")
    print("="*60)

    # Define job with parameter sweeps
    job = command(
        code="./src",
        command="python train.py --alpha ${{inputs.alpha}} --l1_ratio ${{inputs.l1_ratio}}",

        inputs={
            # Interview tip: Choice for categorical, Uniform for continuous
            "alpha": Choice([0.1, 0.5, 1.0]),
            "l1_ratio": Uniform(0.1, 0.9)
        },

        environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
        compute=compute_name
    )

    # Configure sweep
    from azure.ai.ml.sweep import SweepJob

    sweep = SweepJob(
        trial=job,
        sampling_algorithm="random",  # or "grid", "bayesian"

        # Objective: what to optimize
        objective={
            "goal": "minimize",
            "primary_metric": "rmse"
        },

        # Limits
        limits={
            "max_total_trials": 10,
            "max_concurrent_trials": 4,
            "timeout": 7200  # 2 hours
        },

        experiment_name="hyperparameter-sweep"
    )

    print(f"Sweep configuration:")
    print(f"  Algorithm: random")
    print(f"  Objective: minimize rmse")
    print(f"  Max trials: 10")
    print(f"  Concurrent: 4")

    returned_sweep = ml_client.jobs.create_or_update(sweep)

    print(f"\n✓ Sweep job submitted: {returned_sweep.name}")
    print(f"  {returned_sweep.studio_url}")

    return returned_sweep


def stream_job_logs(ml_client, job_name):
    """
    Stream logs from a running job.

    Interview tip: This is how you monitor jobs in real-time.
    """
    print("\n" + "="*60)
    print("Streaming Job Logs")
    print("="*60)

    print(f"Streaming logs for job: {job_name}")
    print("(Press Ctrl+C to stop)\n")

    try:
        ml_client.jobs.stream(job_name)
    except KeyboardInterrupt:
        print("\nLog streaming stopped.")


def monitor_job_status(ml_client, job_name):
    """
    Check job status without streaming logs.

    Interview tip: Useful for polling job status in CI/CD pipelines.
    """
    job = ml_client.jobs.get(job_name)

    print(f"\nJob Status: {job.status}")
    print(f"  Name: {job.name}")
    print(f"  Created: {job.creation_context.created_at}")

    if job.status == "Completed":
        print(f"  ✓ Job completed successfully!")
    elif job.status == "Failed":
        print(f"  ✗ Job failed. Check logs in Azure ML Studio.")
    elif job.status in ["Running", "Preparing", "Queued"]:
        print(f"  ... Job is still running")

    return job.status


def main():
    """
    Main demonstration.
    """
    print("\n" + "="*70)
    print("Azure ML Training Job Submission Demo")
    print("="*70)

    # Configuration
    SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "YOUR_SUBSCRIPTION_ID")
    RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "rg-mlops-demo")
    WORKSPACE_NAME = os.getenv("AZURE_WORKSPACE_NAME", "mlw-demo")
    COMPUTE_NAME = os.getenv("AZURE_COMPUTE_NAME", "training-cluster")

    if SUBSCRIPTION_ID == "YOUR_SUBSCRIPTION_ID":
        print("\n⚠️  This demo requires an Azure ML workspace and compute cluster.")
        print("\nTo run:")
        print("  1. Set up Azure ML workspace")
        print("  2. Create a compute cluster named 'training-cluster'")
        print("  3. Set environment variables or modify this script")
        print("\nFor interview prep: Read the code to understand the concepts!\n")
        return

    try:
        # Connect to workspace
        credential = DefaultAzureCredential()
        ml_client = MLClient(
            credential=credential,
            subscription_id=SUBSCRIPTION_ID,
            resource_group_name=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME
        )

        print(f"✓ Connected to workspace: {WORKSPACE_NAME}")

        # Submit basic training job
        job = submit_training_job(ml_client, COMPUTE_NAME)

        print("\n" + "="*70)
        print("Next Steps:")
        print("="*70)
        print("\n1. Monitor job:")
        print(f"   python submit_training_job.py --monitor {job.name}")
        print("\n2. Stream logs:")
        print(f"   python submit_training_job.py --stream {job.name}")
        print("\n3. View in Azure ML Studio:")
        print(f"   {job.studio_url}")
        print("\n" + "="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure compute cluster exists:")
        print(f"     az ml compute show -n {COMPUTE_NAME}")
        print("  2. Check ./src/train.py exists")
        print("  3. Verify Azure CLI login: az login")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--monitor", type=str, help="Monitor job status")
    parser.add_argument("--stream", type=str, help="Stream job logs")
    args = parser.parse_args()

    if args.monitor:
        # Monitor specific job
        credential = DefaultAzureCredential()
        ml_client = MLClient(
            credential=credential,
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
            resource_group_name=os.getenv("AZURE_RESOURCE_GROUP"),
            workspace_name=os.getenv("AZURE_WORKSPACE_NAME")
        )
        monitor_job_status(ml_client, args.monitor)

    elif args.stream:
        # Stream job logs
        credential = DefaultAzureCredential()
        ml_client = MLClient(
            credential=credential,
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
            resource_group_name=os.getenv("AZURE_RESOURCE_GROUP"),
            workspace_name=os.getenv("AZURE_WORKSPACE_NAME")
        )
        stream_job_logs(ml_client, args.stream)

    else:
        # Run main demo
        main()
