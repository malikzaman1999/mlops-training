"""
Basic MLflow Tracking Example

This script demonstrates core MLflow tracking concepts:
- Setting up tracking server
- Creating experiments
- Logging parameters, metrics, and models
- Using autologging
- Model signatures

For interview prep: Understand each mlflow.log_* call and why we use it.
"""

import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.datasets import make_regression
import argparse


def generate_sample_data(n_samples=1000, n_features=10, noise=10.0, random_state=42):
    """
    Generate synthetic regression data for demonstration.
    In real projects, you'd load your actual dataset here.
    """
    X, y = make_regression(
        n_samples=n_samples,
        n_features=n_features,
        noise=noise,
        random_state=random_state
    )

    # Convert to DataFrame for better readability
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y

    return df


def evaluate_model(model, X_test, y_test):
    """
    Evaluate model and return metrics.

    Interview tip: Know these metrics!
    - RMSE: Root Mean Squared Error (lower is better)
    - MAE: Mean Absolute Error (lower is better)
    - R2: Coefficient of determination (higher is better, max 1.0)
    """
    predictions = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    return rmse, mae, r2, predictions


def train_model(alpha=0.5, l1_ratio=0.5, tracking_uri="http://127.0.0.1:5000"):
    """
    Train an ElasticNet model with MLflow tracking.

    Args:
        alpha: Regularization strength (hyperparameter)
        l1_ratio: Mix of L1 and L2 regularization (hyperparameter)
        tracking_uri: MLflow tracking server URI
    """

    # ========== 1. Set up MLflow ==========
    # Point to your MLflow tracking server
    # For local: http://127.0.0.1:5000
    # For Azure ML: get URI from workspace
    mlflow.set_tracking_uri(tracking_uri)

    # Create or set experiment
    # Interview tip: Experiments group related runs together
    mlflow.set_experiment("basic-tracking-demo")

    print(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")
    print(f"Experiment: {mlflow.get_experiment_by_name('basic-tracking-demo').name}")

    # ========== 2. Prepare data ==========
    print("\nGenerating sample data...")
    df = generate_sample_data(n_samples=1000, n_features=10, noise=10.0)

    X = df.drop('target', axis=1)
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

    # ========== 3. Start MLflow Run ==========
    # Everything logged inside this context is tracked together
    with mlflow.start_run(run_name=f"elasticnet_alpha_{alpha}_l1_{l1_ratio}"):

        # Get run info
        run = mlflow.active_run()
        print(f"\nActive run ID: {run.info.run_id}")

        # ========== 4. Log Parameters ==========
        # Parameters are hyperparameters that define the model
        # They don't change during training
        # Interview tip: log_param for single, log_params for dict
        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_param("test_size", 0.2)

        # Can also log as dict
        mlflow.log_params({
            "model_type": "ElasticNet",
            "n_features": X_train.shape[1],
            "n_samples": X_train.shape[0]
        })

        # ========== 5. Log Tags ==========
        # Tags are metadata for organizing runs
        mlflow.set_tag("dataset", "synthetic_regression")
        mlflow.set_tag("team", "ml-engineering")
        mlflow.set_tag("environment", "development")

        # ========== 6. Train Model ==========
        print(f"\nTraining ElasticNet model with alpha={alpha}, l1_ratio={l1_ratio}...")
        model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        model.fit(X_train, y_train)

        # ========== 7. Evaluate and Log Metrics ==========
        # Metrics are performance measurements
        # They measure how well the model performs
        # Interview tip: Can log multiple times with step parameter
        rmse, mae, r2, predictions = evaluate_model(model, X_test, y_test)

        print(f"Model Performance:")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE:  {mae:.4f}")
        print(f"  R2:   {r2:.4f}")

        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)

        # Can also log as dict
        mlflow.log_metrics({
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        })

        # ========== 8. Log Model with Signature ==========
        # Signature defines expected input/output schema
        # Interview tip: This enables automatic validation at serving time!
        signature = infer_signature(X_train, predictions)

        # Log model to MLflow
        # Interview tip: Use log_model (not save_model) for production!
        # log_model links the model to this run for full lineage
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",  # Path within the run's artifact store
            signature=signature,
            input_example=X_train.iloc[:5],  # Example input for documentation
            registered_model_name=None  # Set this to auto-register to Model Registry
        )

        print(f"\nModel logged to MLflow!")
        print(f"View in UI: {mlflow.get_tracking_uri()}")

        # ========== 9. Log Artifacts (Optional) ==========
        # Artifacts are files: plots, datasets, configs, etc.

        # Save predictions to CSV and log
        predictions_df = pd.DataFrame({
            'actual': y_test,
            'predicted': predictions
        })
        predictions_df.to_csv("predictions.csv", index=False)
        mlflow.log_artifact("predictions.csv", artifact_path="results")

        print(f"\nRun complete! Run ID: {run.info.run_id}")

        return run.info.run_id


def demonstrate_autologging():
    """
    Demonstrate MLflow autologging feature.

    Interview tip: Autologging automatically captures:
    - Parameters from model initialization
    - Metrics from model.fit()
    - Model itself

    But you lose fine-grained control. Use for rapid experimentation.
    """
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("autolog-demo")

    # Enable autologging for sklearn
    mlflow.sklearn.autolog(
        log_input_examples=True,
        log_model_signatures=True,
        log_models=True
    )

    print("\n" + "="*60)
    print("AUTOLOGGING DEMO")
    print("="*60)

    # Generate data
    df = generate_sample_data(n_samples=500, n_features=5)
    X = df.drop('target', axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Just train normally—MLflow captures everything automatically!
    with mlflow.start_run(run_name="autolog_elasticnet"):
        model = ElasticNet(alpha=0.3, l1_ratio=0.3, random_state=42)
        model.fit(X_train, y_train)

        # Autologging captures training metrics automatically
        # But you can still log custom metrics
        predictions = model.predict(X_test)
        custom_metric = np.mean(np.abs(y_test - predictions))
        mlflow.log_metric("custom_mae", custom_metric)

        print(f"\nAutologging captured everything automatically!")
        print(f"Custom metric logged: {custom_metric:.4f}")

    # Disable autologging to avoid affecting other code
    mlflow.sklearn.autolog(disable=True)


def load_and_predict_example(run_id):
    """
    Demonstrate loading a logged model and making predictions.

    Interview tip: Know the different model URI formats!
    - runs:/RUN_ID/model → Load from a specific run
    - models:/MODEL_NAME/VERSION → Load from Model Registry
    """
    mlflow.set_tracking_uri("http://127.0.0.1:5000")

    print("\n" + "="*60)
    print("LOADING MODEL DEMO")
    print("="*60)

    # Load model using run ID
    model_uri = f"runs:/{run_id}/model"
    print(f"Loading model from: {model_uri}")

    loaded_model = mlflow.sklearn.load_model(model_uri)

    # Make predictions with loaded model
    sample_data = generate_sample_data(n_samples=5, n_features=10)
    X_sample = sample_data.drop('target', axis=1)

    predictions = loaded_model.predict(X_sample)

    print(f"\nPredictions on new data:")
    for i, pred in enumerate(predictions):
        print(f"  Sample {i+1}: {pred:.4f}")

    print(f"\nModel loaded and predictions made successfully!")


def hyperparameter_sweep():
    """
    Demonstrate logging multiple runs for hyperparameter tuning.

    Interview tip: This pattern shows how to track experiments systematically.
    You can then use mlflow.search_runs() to find the best model.
    """
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("hyperparameter-sweep")

    print("\n" + "="*60)
    print("HYPERPARAMETER SWEEP DEMO")
    print("="*60)

    # Generate data once
    df = generate_sample_data(n_samples=800, n_features=10)
    X = df.drop('target', axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Try different hyperparameter combinations
    alpha_values = [0.1, 0.5, 1.0]
    l1_ratio_values = [0.1, 0.5, 0.9]

    best_rmse = float('inf')
    best_params = {}

    for alpha in alpha_values:
        for l1_ratio in l1_ratio_values:
            with mlflow.start_run(run_name=f"sweep_alpha_{alpha}_l1_{l1_ratio}"):
                # Log hyperparameters
                mlflow.log_param("alpha", alpha)
                mlflow.log_param("l1_ratio", l1_ratio)

                # Train model
                model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
                model.fit(X_train, y_train)

                # Evaluate
                predictions = model.predict(X_test)
                rmse = np.sqrt(mean_squared_error(y_test, predictions))

                # Log metrics
                mlflow.log_metric("rmse", rmse)

                print(f"Alpha: {alpha}, L1 Ratio: {l1_ratio} → RMSE: {rmse:.4f}")

                # Track best
                if rmse < best_rmse:
                    best_rmse = rmse
                    best_params = {"alpha": alpha, "l1_ratio": l1_ratio}

    print(f"\nBest hyperparameters: {best_params}")
    print(f"Best RMSE: {best_rmse:.4f}")
    print(f"\nView all runs in MLflow UI to compare!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MLflow Tracking Demo")
    parser.add_argument("--alpha", type=float, default=0.5, help="ElasticNet alpha parameter")
    parser.add_argument("--l1-ratio", type=float, default=0.5, help="ElasticNet l1_ratio parameter")
    parser.add_argument("--tracking-uri", type=str, default="http://127.0.0.1:5000",
                       help="MLflow tracking server URI")
    parser.add_argument("--demo", type=str, choices=["basic", "autolog", "sweep", "all"],
                       default="basic", help="Which demo to run")

    args = parser.parse_args()

    print("="*60)
    print("MLflow Basic Tracking Example")
    print("="*60)
    print("\nMake sure MLflow server is running:")
    print("  mlflow server --host 127.0.0.1 --port 5000")
    print(f"\nThen view results at: {args.tracking_uri}")
    print("="*60)

    if args.demo == "basic" or args.demo == "all":
        # Run basic example
        run_id = train_model(
            alpha=args.alpha,
            l1_ratio=args.l1_ratio,
            tracking_uri=args.tracking_uri
        )

        # Demonstrate loading
        load_and_predict_example(run_id)

    if args.demo == "autolog" or args.demo == "all":
        # Run autologging demo
        demonstrate_autologging()

    if args.demo == "sweep" or args.demo == "all":
        # Run hyperparameter sweep
        hyperparameter_sweep()

    print("\n" + "="*60)
    print("COMPLETE! Check the MLflow UI for all logged runs.")
    print(f"UI URL: {args.tracking_uri}")
    print("="*60)
