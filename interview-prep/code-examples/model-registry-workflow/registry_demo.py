"""
MLflow Model Registry Workflow Example

This script demonstrates the complete Model Registry workflow:
- Registering models
- Versioning
- Using aliases (champion, challenger, staging)
- Loading models for deployment
- Comparing versions

For interview prep: Understand the model lifecycle in the registry.
"""

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from mlflow.models import infer_signature

import numpy as np
import pandas as pd
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, r2_score


def setup_mlflow(tracking_uri="http://127.0.0.1:5000"):
    """
    Set up MLflow tracking server.

    Interview tip: In production, this would be Azure ML workspace URI
    or a centralized MLflow server.
    """
    mlflow.set_tracking_uri(tracking_uri)
    print(f"✓ MLflow Tracking URI: {tracking_uri}")
    return MlflowClient()


def train_and_log_model(model_name, alpha, l1_ratio, experiment_name="model-registry-demo"):
    """
    Train a model and log it to MLflow.

    Interview tip: This demonstrates logging models for later registration.

    Args:
        model_name: Name to give the model
        alpha: ElasticNet alpha parameter
        l1_ratio: ElasticNet l1_ratio parameter

    Returns:
        run_id: The MLflow run ID
        rmse: Model performance metric
    """
    print("\n" + "="*60)
    print(f"Training Model: alpha={alpha}, l1_ratio={l1_ratio}")
    print("="*60)

    mlflow.set_experiment(experiment_name)

    # Generate data
    X, y = make_regression(n_samples=1000, n_features=10, noise=10.0, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with mlflow.start_run(run_name=f"elasticnet_alpha_{alpha}") as run:
        # Train
        model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate
        predictions = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)

        # Log
        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        # Log model WITH signature
        # Interview tip: Signature enables automatic validation!
        signature = infer_signature(X_train, predictions)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=X_train[:5]
        )

        print(f"✓ Model trained and logged")
        print(f"  Run ID: {run.info.run_id}")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  R2: {r2:.4f}")

        return run.info.run_id, rmse


def register_model_from_run(client, run_id, model_name, tags=None):
    """
    Register a model from a logged run.

    Interview tip: This is how you move a model from experiments to the registry.
    The registry is the "source of truth" for production-ready models.

    Args:
        client: MlflowClient
        run_id: Run ID containing the model
        model_name: Name to register the model under
        tags: Optional dict of tags

    Returns:
        ModelVersion object
    """
    print("\n" + "="*60)
    print(f"Registering Model: {model_name}")
    print("="*60)

    # Interview tip: Two ways to register:
    # 1. During training: mlflow.sklearn.log_model(..., registered_model_name="MyModel")
    # 2. After training: mlflow.register_model() (demonstrated here)

    model_uri = f"runs:/{run_id}/model"

    print(f"Source: {model_uri}")

    # Register the model
    model_version = mlflow.register_model(
        model_uri=model_uri,
        name=model_name,
        tags=tags or {}
    )

    print(f"✓ Model registered!")
    print(f"  Name: {model_version.name}")
    print(f"  Version: {model_version.version}")
    print(f"  Run ID: {model_version.run_id}")

    return model_version


def set_model_alias(client, model_name, version, alias):
    """
    Set an alias for a model version.

    Interview tip: Aliases are the MODERN way to manage model lifecycle.
    Replaced the old "stages" system (Staging, Production, Archived).

    Common aliases:
    - "champion" → Current production model
    - "challenger" → New model being tested
    - "staging" → Model in pre-production validation

    Args:
        client: MlflowClient
        model_name: Name of registered model
        version: Version number to alias
        alias: Alias name (e.g., "champion")
    """
    print(f"\n→ Setting alias '{alias}' for {model_name} version {version}")

    client.set_registered_model_alias(
        name=model_name,
        alias=alias,
        version=str(version)
    )

    print(f"  ✓ Alias set: {model_name}@{alias} → v{version}")


def load_model_by_alias(model_name, alias):
    """
    Load a model using its alias.

    Interview tip: This is how you deploy models in production!
    Your deployment code references @champion, not a specific version.
    You can update the champion by just changing the alias.

    Args:
        model_name: Name of registered model
        alias: Alias to load (e.g., "champion")

    Returns:
        Loaded model
    """
    print(f"\n→ Loading model: {model_name}@{alias}")

    # Interview tip: Different model URI formats
    # - runs:/RUN_ID/model → Load from run
    # - models:/NAME/VERSION → Load specific version
    # - models:/NAME@ALIAS → Load by alias (recommended for production!)

    model_uri = f"models:/{model_name}@{alias}"
    model = mlflow.pyfunc.load_model(model_uri)

    print(f"  ✓ Model loaded from: {model_uri}")

    return model


def compare_model_versions(client, model_name, version1, version2):
    """
    Compare two model versions.

    Interview tip: This demonstrates how to decide which model to promote.
    In real scenarios, you'd compare on a holdout test set.
    """
    print("\n" + "="*60)
    print(f"Comparing Model Versions: v{version1} vs v{version2}")
    print("="*60)

    # Get model version details
    mv1 = client.get_model_version(model_name, str(version1))
    mv2 = client.get_model_version(model_name, str(version2))

    # Get metrics from runs
    run1 = mlflow.get_run(mv1.run_id)
    run2 = mlflow.get_run(mv2.run_id)

    # Extract metrics
    rmse1 = run1.data.metrics.get("rmse", float('inf'))
    rmse2 = run2.data.metrics.get("rmse", float('inf'))

    r2_1 = run1.data.metrics.get("r2", 0)
    r2_2 = run2.data.metrics.get("r2", 0)

    # Display comparison
    comparison_df = pd.DataFrame({
        'Metric': ['RMSE', 'R2'],
        f'Version {version1}': [f'{rmse1:.4f}', f'{r2_1:.4f}'],
        f'Version {version2}': [f'{rmse2:.4f}', f'{r2_2:.4f}'],
        'Better': [
            f'v{version1}' if rmse1 < rmse2 else f'v{version2}',
            f'v{version1}' if r2_1 > r2_2 else f'v{version2}'
        ]
    })

    print("\n" + comparison_df.to_string(index=False))

    # Determine winner
    if rmse2 < rmse1:
        print(f"\n→ Version {version2} performs better!")
        return version2
    else:
        print(f"\n→ Version {version1} is still better.")
        return version1


def list_all_versions(client, model_name):
    """
    List all versions of a model with their aliases.

    Interview tip: This shows the complete history of a model.
    """
    print("\n" + "="*60)
    print(f"All Versions of {model_name}")
    print("="*60)

    # Get all versions
    versions = client.search_model_versions(f"name='{model_name}'")

    # Sort by version number
    versions = sorted(versions, key=lambda x: int(x.version))

    print(f"\nFound {len(versions)} versions:\n")

    for mv in versions:
        # Get aliases for this version
        aliases = mv.aliases if hasattr(mv, 'aliases') else []

        print(f"  Version {mv.version}:")
        print(f"    Run ID: {mv.run_id}")
        print(f"    Created: {mv.creation_timestamp}")
        if aliases:
            print(f"    Aliases: {', '.join(aliases)}")
        else:
            print(f"    Aliases: (none)")
        print()


def demonstrate_champion_challenger_pattern():
    """
    Demonstrate the champion/challenger deployment pattern.

    Interview tip: This is a common production ML pattern!

    The flow:
    1. Train new model → v2
    2. Current production → champion (v1)
    3. New model → challenger (v2)
    4. Test challenger in production (canary, shadow, A/B)
    5. If better, promote: challenger → champion
    6. Old champion becomes archived or deleted
    """
    print("\n" + "="*70)
    print("CHAMPION/CHALLENGER PATTERN DEMO")
    print("="*70)

    client = setup_mlflow()
    model_name = "HousingPriceModel"

    # === Step 1: Train and register first model (champion) ===
    print("\n--- Step 1: Deploy Initial Champion ---")
    run_id_v1, rmse_v1 = train_and_log_model(model_name, alpha=0.5, l1_ratio=0.5)
    mv1 = register_model_from_run(client, run_id_v1, model_name, tags={"purpose": "initial_champion"})
    set_model_alias(client, model_name, mv1.version, "champion")

    # === Step 2: Train new model (challenger) ===
    print("\n--- Step 2: Train Challenger Model ---")
    run_id_v2, rmse_v2 = train_and_log_model(model_name, alpha=0.3, l1_ratio=0.7)
    mv2 = register_model_from_run(client, run_id_v2, model_name, tags={"purpose": "challenger"})
    set_model_alias(client, model_name, mv2.version, "challenger")

    # === Step 3: Compare models ===
    print("\n--- Step 3: Compare Champion vs Challenger ---")
    better_version = compare_model_versions(client, model_name, mv1.version, mv2.version)

    # === Step 4: Promote if better ===
    if int(better_version) == int(mv2.version):
        print("\n--- Step 4: Promote Challenger to Champion ---")
        set_model_alias(client, model_name, mv2.version, "champion")
        # Old champion becomes previous
        set_model_alias(client, model_name, mv1.version, "previous")
        print("✓ Challenger is now the champion!")
    else:
        print("\n--- Step 4: Keep Current Champion ---")
        print("✓ Challenger did not beat champion. Keeping v1.")

    # === Step 5: Show final state ===
    print("\n--- Step 5: Final Model Registry State ---")
    list_all_versions(client, model_name)

    # === Step 6: Demonstrate loading for deployment ===
    print("\n--- Step 6: Loading Models for Deployment ---")
    champion_model = load_model_by_alias(model_name, "champion")

    # Make prediction
    X_sample = np.random.randn(1, 10)
    prediction = champion_model.predict(X_sample)
    print(f"  Sample prediction: {prediction[0]:.4f}")

    print("\n" + "="*70)
    print("Champion/Challenger pattern complete!")
    print("="*70)


def demonstrate_model_lifecycle():
    """
    Demonstrate complete model lifecycle in registry.

    Interview tip: This shows how models move through their lifecycle.
    """
    print("\n" + "="*70)
    print("MODEL LIFECYCLE DEMO")
    print("="*70)

    client = setup_mlflow()
    model_name = "LifecycleDemo"

    # Train 3 models
    print("\n--- Training Multiple Model Versions ---")

    run_id_1, _ = train_and_log_model(model_name, alpha=1.0, l1_ratio=0.5)
    run_id_2, _ = train_and_log_model(model_name, alpha=0.5, l1_ratio=0.5)
    run_id_3, _ = train_and_log_model(model_name, alpha=0.1, l1_ratio=0.5)

    # Register all
    print("\n--- Registering All Versions ---")
    mv1 = register_model_from_run(client, run_id_1, model_name)
    mv2 = register_model_from_run(client, run_id_2, model_name)
    mv3 = register_model_from_run(client, run_id_3, model_name)

    # Set aliases to show lifecycle
    print("\n--- Setting Aliases (Lifecycle) ---")
    set_model_alias(client, model_name, mv3.version, "champion")  # Best model in production
    set_model_alias(client, model_name, mv2.version, "staging")   # Being validated
    # v1 has no alias (archived/experimental)

    # Show state
    list_all_versions(client, model_name)

    print("\nLifecycle interpretation:")
    print(f"  v{mv3.version} (@champion) → Production model serving traffic")
    print(f"  v{mv2.version} (@staging) → Validation/testing before production")
    print(f"  v{mv1.version} (no alias) → Experimental/archived")


def main():
    """
    Main demo.
    """
    print("\n" + "="*70)
    print("MLflow Model Registry Workflow Demo")
    print("="*70)

    print("\nMake sure MLflow server is running:")
    print("  mlflow server --host 127.0.0.1 --port 5000")
    print("\nThen view at: http://127.0.0.1:5000")
    print("="*70)

    import sys
    if len(sys.argv) > 1:
        demo = sys.argv[1]
    else:
        demo = "champion"

    if demo == "champion":
        demonstrate_champion_challenger_pattern()
    elif demo == "lifecycle":
        demonstrate_model_lifecycle()
    elif demo == "all":
        demonstrate_champion_challenger_pattern()
        print("\n\n")
        demonstrate_model_lifecycle()
    else:
        print(f"Unknown demo: {demo}")
        print("Usage: python registry_demo.py [champion|lifecycle|all]")

    print("\n" + "="*70)
    print("✓ View results in MLflow UI:")
    print("  http://127.0.0.1:5000")
    print("  Navigate to 'Models' tab to see the registry")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
