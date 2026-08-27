"""
train.py -- Phase 4: train a real model and log it to the Azure-backed
MLflow tracking server we built in Phases 2/3.

This is deliberately the SAME dataset and model family (ElasticNet on the
wine-quality dataset) as your MLflow course notes -- the goal of this phase
isn't to learn a new ML problem, it's to prove the same
mlflow.start_run()/log_param/log_metric/log_model pattern you already know
now works end-to-end against real Azure infrastructure instead of local
SQLite, and to produce a real registered model we can containerize next.

Prerequisites to actually run this:
  1. The MLflow tracking server container must be running
     (terraform/mlflow-server/run.sh), reachable at http://localhost:5000
  2. This process needs its OWN Azure Blob credentials to upload the model
     artifact directly (see terraform/mlflow-server/.env.example --
     the "non-proxied artifact access" lesson from Phase 3) --
     export AZURE_STORAGE_CONNECTION_STRING before running this script.
  3. pip install -r requirements.txt (in this same folder)

Usage:
  export AZURE_STORAGE_CONNECTION_STRING="<see terraform/mlflow-server/.env>"
  python3 train.py --alpha 0.5 --l1-ratio 0.5
"""

import argparse
import os

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Resolved relative to this file so the script works regardless of which
# directory it's invoked from -- avoids a common "works on my machine, not
# in CI" bug caused by relative paths depending on the caller's cwd.
DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "MLFLow_courser", "red-wine-quality.csv"
)

# Where the MLflow tracking server lives. In a later phase, once this
# server moves onto AKS, this would become an internal cluster DNS name
# instead of localhost -- everything else in this script stays identical,
# which is the whole point of separating "where is the server" from
# "how do I use it" via set_tracking_uri.
TRACKING_URI = "http://localhost:5000"

EXPERIMENT_NAME = "wine-quality-elasticnet"


def eval_metrics(actual, predicted):
    """Same three metrics the MLflow course used: RMSE, MAE, R2."""
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mae = mean_absolute_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    return rmse, mae, r2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--l1-ratio", type=float, default=0.5)
    args = parser.parse_args()

    # index_col=0 drops the CSV's leading unnamed index column (visible as
    # a bare "," at the start of the header row) so it isn't mistaken for
    # a real feature.
    data = pd.read_csv(DATA_PATH, index_col=0)

    train, test = train_test_split(data, test_size=0.25, random_state=42)

    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    # Pointing the client at our real tracking server -- this one line is
    # the entire difference between "logs to local ./mlruns" and "logs to
    # Azure Postgres + Blob Storage." Everything below is unchanged from
    # what you already know from the course.
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run():
        model = ElasticNet(alpha=args.alpha, l1_ratio=args.l1_ratio, random_state=42)
        model.fit(train_x, train_y)

        predicted_qualities = model.predict(test_x)
        rmse, mae, r2 = eval_metrics(test_y, predicted_qualities)

        print(f"ElasticNet(alpha={args.alpha}, l1_ratio={args.l1_ratio})")
        print(f"  RMSE: {rmse}")
        print(f"  MAE:  {mae}")
        print(f"  R2:   {r2}")

        mlflow.log_param("alpha", args.alpha)
        mlflow.log_param("l1_ratio", args.l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)

        # infer_signature reads the actual training data's shape/dtypes to
        # build the model's input/output schema automatically, instead of
        # hand-writing a ColSpec/Schema like the manual approach covered in
        # the course notes -- this is the "preferred, less error-prone"
        # method mentioned there.
        signature = mlflow.models.infer_signature(train_x, predicted_qualities)

        # registered_model_name registers this exact run's model as a new
        # version under "wine-quality-elasticnet" in the Model Registry --
        # this is what makes it loadable later (by the container we build
        # next) via a stable models:/wine-quality-elasticnet/<version> URI,
        # rather than having to know this specific run's ID.
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=train_x.head(3),
            registered_model_name="wine-quality-elasticnet",
        )


if __name__ == "__main__":
    main()
