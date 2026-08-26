"""
Azure ML + MLflow Integration Example

This script demonstrates how to use MLflow with Azure ML:
- Connecting to Azure ML workspace
- Using Azure ML's built-in MLflow tracking
- Submitting training jobs to Azure ML compute
- Accessing models from Azure ML Model Registry

For interview prep: Understand how Azure ML provides MLflow-compatible API.
"""

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Model
import mlflow
import os


def connect_to_workspace(subscription_id, resource_group, workspace_name):
    """
    Connect to Azure ML workspace and get MLflow tracking URI.

    Interview tip: Azure ML provides a built-in MLflow tracking server!
    You don't need to run your own MLflow server.

    Args:
        subscription_id: Your Azure subscription ID
        resource_group: Name of the resource group
        workspace_name: Name of the Azure ML workspace

    Returns:
        ml_client: Azure ML client
        tracking_uri: MLflow tracking URI for the workspace
    """
    print("="*60)
    print("Connecting to Azure ML Workspace")
    print("="*60)

    # Authenticate using DefaultAzureCredential
    # Interview tip: This tries multiple auth methods in order:
    # 1. Environment variables (for CI/CD)
    # 2. Managed identity (for Azure compute)
    # 3. Azure CLI (for local development)
    # 4. Interactive browser (fallback)
    credential = DefaultAzureCredential()

    # Create MLClient
    ml_client = MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name
    )

    print(f"✓ Connected to workspace: {workspace_name}")

    # Get workspace details
    workspace = ml_client.workspaces.get(name=workspace_name)
    print(f"  Resource Group: {resource_group}")
    print(f"  Location: {workspace.location}")

    # Get MLflow tracking URI
    # Interview tip: This is the key integration point!
    tracking_uri = workspace.mlflow_tracking_uri
    print(f"\n✓ MLflow Tracking URI: {tracking_uri}")
    print(f"  (Azure ML provides this built-in MLflow server)")

    return ml_client, tracking_uri


def use_azure_mlflow_tracking(tracking_uri, experiment_name="azure-mlflow-demo"):
    """
    Use MLflow tracking with Azure ML backend.

    Interview tip: Once you set the tracking URI, standard MLflow code works!
    No changes needed to your existing MLflow code.
    """
    print("\n" + "="*60)
    print("Using MLflow with Azure ML Backend")
    print("="*60)

    # Set tracking URI to Azure ML workspace
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    print(f"✓ Experiment set to: {experiment_name}")

    # Now use MLflow normally—it's stored in Azure ML!
    with mlflow.start_run(run_name="azure-demo-run") as run:
        # Log parameters
        mlflow.log_param("learning_rate", 0.01)
        mlflow.log_param("batch_size", 32)
        mlflow.log_param("optimizer", "adam")

        # Log metrics
        mlflow.log_metric("accuracy", 0.95)
        mlflow.log_metric("loss", 0.12)

        # Log tags
        mlflow.set_tag("environment", "azure-ml")
        mlflow.set_tag("team", "ml-engineering")

        print(f"\n✓ Logged run to Azure ML")
        print(f"  Run ID: {run.info.run_id}")
        print(f"  Experiment: {experiment_name}")

        # Interview tip: This data is now stored in Azure ML!
        # - Parameters/metrics → Azure ML backend store
        # - Artifacts/models → Azure ML default storage account

    return run.info.run_id


def list_experiments(ml_client):
    """
    List all experiments in the Azure ML workspace.

    Interview tip: Experiments in Azure ML are the same as MLflow experiments.
    You can view them in:
    1. Azure ML Studio UI
    2. MLflow UI (if you run it locally pointing to Azure)
    3. Programmatically via SDK
    """
    print("\n" + "="*60)
    print("Listing Experiments")
    print("="*60)

    # Using MLflow client
    experiments = mlflow.search_experiments()

    print(f"Found {len(experiments)} experiments:\n")
    for exp in experiments[:5]:  # Show first 5
        print(f"  - {exp.name}")
        print(f"    Experiment ID: {exp.experiment_id}")
        print(f"    Artifact Location: {exp.artifact_location}")
        print()


def search_runs_example(experiment_name="azure-mlflow-demo"):
    """
    Search and filter runs using MLflow search API.

    Interview tip: This demonstrates how to programmatically find runs.
    Very useful for finding best models, comparing experiments, etc.
    """
    print("="*60)
    print("Searching Runs")
    print("="*60)

    # Search all runs in experiment
    runs = mlflow.search_runs(
        experiment_names=[experiment_name],
        order_by=["metrics.accuracy DESC"],
        max_results=5
    )

    if len(runs) > 0:
        print(f"\nFound {len(runs)} runs:")
        print(runs[['run_id', 'params.learning_rate', 'metrics.accuracy', 'metrics.loss']].to_string())
    else:
        print(f"\nNo runs found in experiment: {experiment_name}")

    # Search with filter
    print("\n" + "-"*60)
    print("Filtering runs where accuracy > 0.9:")
    filtered_runs = mlflow.search_runs(
        experiment_names=[experiment_name],
        filter_string="metrics.accuracy > 0.9"
    )
    print(f"Found {len(filtered_runs)} runs")


def register_model_example(ml_client, run_id, model_name="demo-model"):
    """
    Register a model in Azure ML Model Registry using MLflow.

    Interview tip: Azure ML Model Registry is compatible with MLflow Model Registry.
    Models registered via MLflow appear in Azure ML Studio and vice versa.
    """
    print("\n" + "="*60)
    print("Registering Model")
    print("="*60)

    # Note: In a real scenario, you'd have logged a model during training
    # This demonstrates the registration concept

    # Using MLflow to register
    # model_uri = f"runs:/{run_id}/model"
    # model_version = mlflow.register_model(model_uri, model_name)

    print(f"To register a model:")
    print(f"  1. Log model during training:")
    print(f"     mlflow.sklearn.log_model(model, 'model')")
    print(f"  2. Register from run:")
    print(f"     mlflow.register_model('runs:/{run_id}/model', '{model_name}')")
    print(f"\n  Model will appear in both:")
    print(f"    - MLflow Model Registry")
    print(f"    - Azure ML Studio > Models")


def get_workspace_info(ml_client):
    """
    Get information about Azure ML workspace resources.

    Interview tip: Know what Azure ML auto-creates with a workspace:
    - Storage Account (for artifacts)
    - Key Vault (for secrets)
    - Container Registry (for Docker images)
    - Application Insights (for monitoring)
    """
    print("\n" + "="*60)
    print("Azure ML Workspace Resources")
    print("="*60)

    workspace = ml_client.workspaces.get(name=ml_client.workspace_name)

    print(f"Workspace: {workspace.name}")
    print(f"\nAuto-created resources:")
    print(f"  Storage Account:      {workspace.storage_account}")
    print(f"  Key Vault:            {workspace.key_vault}")
    print(f"  Container Registry:   {workspace.container_registry}")
    print(f"  Application Insights: {workspace.application_insights}")

    print(f"\nMLflow Integration:")
    print(f"  Tracking URI: {workspace.mlflow_tracking_uri}")
    print(f"  (This is your MLflow server—managed by Azure!)")


def demonstrate_local_vs_azure():
    """
    Show the difference between local MLflow and Azure ML MLflow.

    Interview tip: This is a common interview question!
    """
    print("\n" + "="*60)
    print("Local MLflow vs Azure ML MLflow")
    print("="*60)

    comparison = """
    ┌─────────────────────┬─────────────────────────┬─────────────────────────┐
    │ Feature             │ Local MLflow            │ Azure ML MLflow         │
    ├─────────────────────┼─────────────────────────┼─────────────────────────┤
    │ Tracking Server     │ You run it              │ Azure manages it        │
    │                     │ mlflow server ...       │ Always available        │
    ├─────────────────────┼─────────────────────────┼─────────────────────────┤
    │ Backend Store       │ SQLite or PostgreSQL    │ Azure ML backend        │
    │ (metadata)          │ You manage              │ Fully managed           │
    ├─────────────────────┼─────────────────────────┼─────────────────────────┤
    │ Artifact Store      │ Local filesystem or S3  │ Azure Storage Account   │
    │ (models, plots)     │ You configure           │ Auto-configured         │
    ├─────────────────────┼─────────────────────────┼─────────────────────────┤
    │ UI Access           │ http://localhost:5000   │ Azure ML Studio         │
    │                     │                         │ (cloud-based)           │
    ├─────────────────────┼─────────────────────────┼─────────────────────────┤
    │ Collaboration       │ Share server URL        │ Built-in via workspace  │
    │                     │ Manual permissions      │ Azure RBAC              │
    ├─────────────────────┼─────────────────────────┼─────────────────────────┤
    │ Code Changes        │ Standard MLflow         │ Standard MLflow         │
    │                     │                         │ (just change URI!)      │
    ├─────────────────────┼─────────────────────────┼─────────────────────────┤
    │ Cost                │ Infrastructure costs    │ Workspace + storage     │
    │                     │                         │ (pay for what you use)  │
    ├─────────────────────┼─────────────────────────┼─────────────────────────┤
    │ Best For            │ Local dev, prototyping  │ Team collaboration,     │
    │                     │                         │ production workloads    │
    └─────────────────────┴─────────────────────────┴─────────────────────────┘

    Key Takeaway:
    - Same MLflow API for both!
    - Azure ML provides managed infrastructure
    - Zero code changes when moving from local to Azure
    """
    print(comparison)


def main():
    """
    Main demonstration function.

    NOTE: This requires an Azure ML workspace to be set up.
    If you don't have one, read through the code to understand concepts.
    """
    print("\n" + "="*70)
    print("Azure ML + MLflow Integration Demo")
    print("="*70)

    # ===== CONFIGURATION =====
    # Update these with your Azure ML workspace details
    SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "YOUR_SUBSCRIPTION_ID")
    RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "rg-mlops-demo")
    WORKSPACE_NAME = os.getenv("AZURE_WORKSPACE_NAME", "mlw-demo")

    print("\nConfiguration:")
    print(f"  Subscription ID:  {SUBSCRIPTION_ID}")
    print(f"  Resource Group:   {RESOURCE_GROUP}")
    print(f"  Workspace Name:   {WORKSPACE_NAME}")

    if SUBSCRIPTION_ID == "YOUR_SUBSCRIPTION_ID":
        print("\n" + "="*70)
        print("⚠️  SETUP REQUIRED")
        print("="*70)
        print("\nThis demo requires an Azure ML workspace.")
        print("\nOptions:")
        print("  1. Set environment variables:")
        print("     export AZURE_SUBSCRIPTION_ID='your-sub-id'")
        print("     export AZURE_RESOURCE_GROUP='your-rg'")
        print("     export AZURE_WORKSPACE_NAME='your-workspace'")
        print("\n  2. Or modify the variables in this script")
        print("\n  3. Or just read through the code to understand concepts!")
        print("\n" + "="*70)

        # Show conceptual demo without actual Azure connection
        demonstrate_local_vs_azure()

        print("\n✓ Read through the code comments to learn the concepts!")
        print("  Even without Azure, you'll understand the integration.\n")
        return

    try:
        # Connect to workspace
        ml_client, tracking_uri = connect_to_workspace(
            SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME
        )

        # Get workspace info
        get_workspace_info(ml_client)

        # Use MLflow with Azure backend
        run_id = use_azure_mlflow_tracking(tracking_uri)

        # List experiments
        list_experiments(ml_client)

        # Search runs
        search_runs_example()

        # Show registration example
        register_model_example(ml_client, run_id)

        # Show comparison
        demonstrate_local_vs_azure()

        print("\n" + "="*70)
        print("✓ DEMO COMPLETE!")
        print("="*70)
        print("\nWhat you learned:")
        print("  ✓ How to connect to Azure ML workspace")
        print("  ✓ How to use MLflow with Azure ML backend")
        print("  ✓ How Azure ML provides managed MLflow infrastructure")
        print("  ✓ How to search runs and experiments")
        print("  ✓ Difference between local and Azure ML MLflow")
        print("\nView your run in Azure ML Studio:")
        print(f"  https://ml.azure.com")
        print(f"  Navigate to: {WORKSPACE_NAME} > Experiments")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Run 'az login' to authenticate")
        print("  2. Verify workspace exists: az ml workspace show -n {WORKSPACE_NAME}")
        print("  3. Check permissions: you need Contributor or Owner role")
        print("  4. Install Azure CLI: https://docs.microsoft.com/cli/azure/install-azure-cli")


if __name__ == "__main__":
    main()
