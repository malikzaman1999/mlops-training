"""
Model Registration Script

Registers models from MLflow runs into Azure ML Model Registry.
"""

import argparse
import mlflow
from mlflow.tracking import MlflowClient

from utils import get_mlflow_tracking_uri


def register_model(run_id, model_name="HousingPriceModel", alias=None):
    """
    Register a model from an MLflow run.

    Args:
        run_id: MLflow run ID containing the model
        model_name: Name to register model under
        alias: Optional alias to set (@champion, @challenger, etc.)

    Returns:
        Model version object
    """
    print("="*70)
    print("Registering Model")
    print("="*70)

    # Set up MLflow
    tracking_uri = get_mlflow_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)

    print(f"\n✓ Connected to MLflow")
    print(f"  URI: {tracking_uri}")

    # Get run details
    run = mlflow.get_run(run_id)
    rmse = run.data.metrics.get("rmse", "N/A")
    r2 = run.data.metrics.get("r2", "N/A")

    print(f"\nRun Details:")
    print(f"  Run ID: {run_id}")
    print(f"  RMSE: {rmse}")
    print(f"  R2: {r2}")

    # Register model
    model_uri = f"runs:/{run_id}/model"

    print(f"\nRegistering model from: {model_uri}")

    model_version = mlflow.register_model(
        model_uri=model_uri,
        name=model_name,
        tags={
            "rmse": str(rmse),
            "r2": str(r2),
            "run_id": run_id
        }
    )

    print(f"\n✓ Model registered!")
    print(f"  Name: {model_version.name}")
    print(f"  Version: {model_version.version}")

    # Set alias if provided
    if alias:
        client = MlflowClient()
        client.set_registered_model_alias(
            name=model_name,
            alias=alias,
            version=str(model_version.version)
        )
        print(f"  Alias: @{alias}")

    print(f"\nView in Azure ML Studio:")
    print(f"  https://ml.azure.com")
    print(f"  Navigate to: Models > {model_name}")

    print("\n" + "="*70)
    print("Registration Complete!")
    print("="*70)

    return model_version


def list_models(model_name="HousingPriceModel"):
    """
    List all versions of a model.
    """
    tracking_uri = get_mlflow_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()

    print("="*70)
    print(f"Model Versions: {model_name}")
    print("="*70)

    versions = client.search_model_versions(f"name='{model_name}'")
    versions = sorted(versions, key=lambda x: int(x.version))

    if not versions:
        print(f"\nNo versions found for model: {model_name}")
        return

    print(f"\nFound {len(versions)} versions:\n")

    for mv in versions:
        # Get run to fetch metrics
        run = mlflow.get_run(mv.run_id)
        rmse = run.data.metrics.get("rmse", "N/A")
        r2 = run.data.metrics.get("r2", "N/A")

        # Get aliases
        aliases = mv.aliases if hasattr(mv, 'aliases') else []

        print(f"Version {mv.version}:")
        print(f"  RMSE: {rmse}")
        print(f"  R2: {r2}")
        print(f"  Run ID: {mv.run_id}")
        if aliases:
            print(f"  Aliases: {', '.join(['@' + a for a in aliases])}")
        print()


def update_alias(model_name, version, alias):
    """
    Update model alias.
    """
    tracking_uri = get_mlflow_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()

    print(f"Setting @{alias} → v{version} for {model_name}")

    client.set_registered_model_alias(
        name=model_name,
        alias=alias,
        version=str(version)
    )

    print(f"✓ Alias updated!")


def main():
    parser = argparse.ArgumentParser(description="Register model in Azure ML")
    parser.add_argument("--run-id", type=str, help="MLflow run ID")
    parser.add_argument("--model-name", type=str, default="HousingPriceModel",
                       help="Model name")
    parser.add_argument("--alias", type=str, help="Alias to set (champion, challenger, staging)")
    parser.add_argument("--list", action="store_true", help="List all model versions")
    parser.add_argument("--update-alias", action="store_true",
                       help="Update alias for existing version")
    parser.add_argument("--version", type=str, help="Version number (for --update-alias)")

    args = parser.parse_args()

    if args.list:
        list_models(args.model_name)
    elif args.update_alias:
        if not args.version or not args.alias:
            print("Error: --update-alias requires --version and --alias")
            return
        update_alias(args.model_name, args.version, args.alias)
    else:
        if not args.run_id:
            print("Error: --run-id required for registration")
            print("Usage: python register.py --run-id abc123 --alias champion")
            return
        register_model(args.run_id, args.model_name, args.alias)


if __name__ == "__main__":
    main()
