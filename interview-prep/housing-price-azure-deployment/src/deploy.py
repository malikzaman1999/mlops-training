"""
Model Deployment Script

Deploys models to Azure ML Online Endpoints.
"""

import argparse
import json
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, Model

from utils import get_ml_client


def create_endpoint(ml_client, endpoint_name):
    """
    Create Azure ML Online Endpoint.
    """
    print("="*70)
    print(f"Creating Endpoint: {endpoint_name}")
    print("="*70)

    endpoint = ManagedOnlineEndpoint(
        name=endpoint_name,
        description="Housing price prediction endpoint",
        auth_mode="key"
    )

    print(f"\nCreating endpoint (this may take a few minutes)...")

    endpoint = ml_client.online_endpoints.begin_create_or_update(endpoint).result()

    print(f"\n✓ Endpoint created!")
    print(f"  Name: {endpoint.name}")
    print(f"  Scoring URI: {endpoint.scoring_uri}")

    return endpoint


def deploy_model(
    ml_client,
    endpoint_name,
    model_name,
    model_version_or_alias,
    deployment_name="blue",
    instance_type="Standard_DS2_v2",
    instance_count=1
):
    """
    Deploy a model to an endpoint.
    """
    print("\n" + "="*70)
    print(f"Deploying Model")
    print("="*70)

    print(f"\nConfiguration:")
    print(f"  Endpoint: {endpoint_name}")
    print(f"  Deployment: {deployment_name}")
    print(f"  Model: {model_name}")
    print(f"  Version/Alias: {model_version_or_alias}")
    print(f"  Instance: {instance_type} x {instance_count}")

    # Check if version is an alias or number
    if model_version_or_alias.startswith("@"):
        # It's an alias
        alias = model_version_or_alias[1:]  # Remove @
        # Get the version for this alias
        from mlflow.tracking import MlflowClient
        from utils import get_mlflow_tracking_uri
        import mlflow

        mlflow.set_tracking_uri(get_mlflow_tracking_uri())
        client = MlflowClient()

        # Find version with this alias
        versions = client.search_model_versions(f"name='{model_name}'")
        version = None
        for mv in versions:
            if hasattr(mv, 'aliases') and alias in mv.aliases:
                version = mv.version
                break

        if not version:
            raise ValueError(f"No version found with alias @{alias}")

        print(f"  Resolved @{alias} → v{version}")
    else:
        version = model_version_or_alias

    deployment = ManagedOnlineDeployment(
        name=deployment_name,
        endpoint_name=endpoint_name,
        model=Model(name=model_name, version=version),
        instance_type=instance_type,
        instance_count=instance_count
    )

    print(f"\nDeploying (this may take 5-10 minutes)...")

    deployment = ml_client.online_deployments.begin_create_or_update(deployment).result()

    print(f"\n✓ Deployment complete!")
    print(f"  Deployment: {deployment_name}")

    return deployment


def set_traffic(ml_client, endpoint_name, traffic_dict):
    """
    Set traffic distribution across deployments.

    Args:
        traffic_dict: e.g., {"blue": 100} or {"blue": 80, "green": 20}
    """
    print("\n" + "="*70)
    print("Setting Traffic Distribution")
    print("="*70)

    print(f"\nTraffic allocation:")
    for deployment, percentage in traffic_dict.items():
        print(f"  {deployment}: {percentage}%")

    # Validate traffic sums to 100
    total = sum(traffic_dict.values())
    if total != 100:
        raise ValueError(f"Traffic must sum to 100%, got {total}%")

    endpoint = ml_client.online_endpoints.get(name=endpoint_name)
    endpoint.traffic = traffic_dict

    ml_client.online_endpoints.begin_create_or_update(endpoint).result()

    print(f"\n✓ Traffic updated!")


def main():
    parser = argparse.ArgumentParser(description="Deploy model to Azure ML")
    parser.add_argument("--endpoint-name", type=str, default="housing-endpoint",
                       help="Endpoint name")
    parser.add_argument("--model-name", type=str, default="HousingPriceModel",
                       help="Model name")
    parser.add_argument("--model-version", type=str, default="champion",
                       help="Model version or alias (e.g., '1' or '@champion')")
    parser.add_argument("--deployment-name", type=str, default="blue",
                       help="Deployment name (blue, green, etc.)")
    parser.add_argument("--instance-type", type=str, default="Standard_DS2_v2",
                       help="VM instance type")
    parser.add_argument("--instance-count", type=int, default=1,
                       help="Number of instances")
    parser.add_argument("--traffic", type=str,
                       help="Traffic distribution as JSON, e.g., '{\"blue\": 100}'")
    parser.add_argument("--create-endpoint-only", action="store_true",
                       help="Only create endpoint, don't deploy")

    args = parser.parse_args()

    ml_client = get_ml_client()

    print("="*70)
    print("Azure ML Model Deployment")
    print("="*70)
    print(f"\n✓ Connected to workspace: {ml_client.workspace_name}")

    # Handle version/alias format
    if not args.model_version.startswith("@"):
        model_version = f"@{args.model_version}" if args.model_version in ["champion", "challenger", "staging"] else args.model_version
    else:
        model_version = args.model_version

    # Create endpoint
    try:
        endpoint = ml_client.online_endpoints.get(name=args.endpoint_name)
        print(f"\n✓ Endpoint already exists: {args.endpoint_name}")
    except:
        endpoint = create_endpoint(ml_client, args.endpoint_name)

    if args.create_endpoint_only:
        print("\n✓ Endpoint created (skipping deployment)")
        return

    # Deploy model
    deployment = deploy_model(
        ml_client=ml_client,
        endpoint_name=args.endpoint_name,
        model_name=args.model_name,
        model_version_or_alias=model_version,
        deployment_name=args.deployment_name,
        instance_type=args.instance_type,
        instance_count=args.instance_count
    )

    # Set traffic
    if args.traffic:
        traffic_dict = json.loads(args.traffic)
        set_traffic(ml_client, args.endpoint_name, traffic_dict)
    else:
        # Default: 100% to this deployment
        set_traffic(ml_client, args.endpoint_name, {args.deployment_name: 100})

    print("\n" + "="*70)
    print("Deployment Complete!")
    print("="*70)
    print(f"\nEndpoint: {endpoint.scoring_uri}")
    print(f"\nTest prediction:")
    print(f"  python src/predict.py --endpoint {args.endpoint_name}")
    print("="*70)


if __name__ == "__main__":
    main()
