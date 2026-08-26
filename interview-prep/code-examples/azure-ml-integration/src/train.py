"""
Sample training script for Azure ML job submission.

This would run on Azure ML compute and automatically log to MLflow.
"""

import argparse
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--l1_ratio", type=float, default=0.5)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--data", type=str, default=None, help="Path to training data")
    return parser.parse_args()


def main():
    args = parse_args()

    print("Training configuration:")
    print(f"  alpha: {args.alpha}")
    print(f"  l1_ratio: {args.l1_ratio}")

    # Generate synthetic data (in real scenario, load from args.data)
    X, y = make_regression(n_samples=1000, n_features=10, noise=10.0, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Azure ML auto-configures MLflow!
    # No need to set tracking URI—it's already set
    mlflow.sklearn.autolog()

    with mlflow.start_run():
        # Train model
        model = ElasticNet(alpha=args.alpha, l1_ratio=args.l1_ratio, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate
        predictions = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)

        # Log metrics (autolog captures most, but we can add custom)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)

        print(f"\nResults:")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  R2: {r2:.4f}")

    print("\n✓ Training complete! Results logged to MLflow.")


if __name__ == "__main__":
    main()
