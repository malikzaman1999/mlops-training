"""
Housing Price Model Training Script

Trains an ElasticNet model with MLflow tracking on Azure ML.
"""

import argparse
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

from utils import get_mlflow_tracking_uri


def load_data(data_path="../data/housing_data.csv"):
    """
    Load and prepare housing data.

    In a real project, this would load from Azure ML Data Assets.
    For this demo, we generate synthetic data.
    """
    # For demo purposes, generate synthetic data
    # In production, you'd load real data:
    # df = pd.read_csv(data_path)

    print("Generating sample housing data...")
    np.random.seed(42)

    n_samples = 1000

    # Features
    sqft = np.random.randint(1000, 4000, n_samples)
    bedrooms = np.random.randint(1, 6, n_samples)
    bathrooms = np.random.randint(1, 4, n_samples)
    year_built = np.random.randint(1950, 2024, n_samples)
    has_garage = np.random.randint(0, 2, n_samples)
    has_pool = np.random.randint(0, 2, n_samples)
    location_score = np.random.randint(1, 11, n_samples)

    # Target (price) - synthetic formula
    base_price = 50000
    price_per_sqft = 150
    bedroom_value = 25000
    bathroom_value = 15000
    garage_value = 30000
    pool_value = 40000
    location_multiplier = 10000
    age_factor = -500

    price = (
        base_price
        + sqft * price_per_sqft
        + bedrooms * bedroom_value
        + bathrooms * bathroom_value
        + has_garage * garage_value
        + has_pool * pool_value
        + location_score * location_multiplier
        + (2024 - year_built) * age_factor
        + np.random.normal(0, 30000, n_samples)  # Noise
    )

    df = pd.DataFrame({
        'sqft': sqft,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'year_built': year_built,
        'has_garage': has_garage,
        'has_pool': has_pool,
        'location_score': location_score,
        'price': price
    })

    print(f"✓ Loaded {len(df)} housing records")
    print(f"  Features: {list(df.columns[:-1])}")
    print(f"  Target: price")
    print(f"  Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")

    return df


def preprocess_data(df):
    """
    Preprocess the data.

    Interview tip: In production, this would be more sophisticated:
    - Handle missing values
    - Feature engineering
    - Categorical encoding
    - Outlier removal
    """
    X = df.drop('price', axis=1)
    y = df['price']

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Standardize features
    # Interview tip: Always scale features for ElasticNet!
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Convert back to DataFrame to preserve feature names
    X_train_scaled = pd.DataFrame(
        X_train_scaled,
        columns=X.columns,
        index=X_train.index
    )
    X_test_scaled = pd.DataFrame(
        X_test_scaled,
        columns=X.columns,
        index=X_test.index
    )

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


def train_model(alpha, l1_ratio, X_train, y_train):
    """
    Train ElasticNet model.

    Interview tip: ElasticNet combines L1 (Lasso) and L2 (Ridge) regularization.
    - alpha: overall regularization strength
    - l1_ratio: mix of L1 vs L2 (1.0 = pure Lasso, 0.0 = pure Ridge)
    """
    print(f"\nTraining ElasticNet model...")
    print(f"  alpha: {alpha}")
    print(f"  l1_ratio: {l1_ratio}")

    model = ElasticNet(
        alpha=alpha,
        l1_ratio=l1_ratio,
        random_state=42,
        max_iter=10000
    )

    model.fit(X_train, y_train)

    print(f"✓ Model trained")

    return model


def evaluate_model(model, X_test, y_test):
    """
    Evaluate model performance.
    """
    predictions = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print(f"\nModel Performance:")
    print(f"  RMSE: ${rmse:,.2f}")
    print(f"  MAE:  ${mae:,.2f}")
    print(f"  R2:   {r2:.4f}")

    return rmse, mae, r2, predictions


def main():
    parser = argparse.ArgumentParser(description="Train housing price model")
    parser.add_argument("--alpha", type=float, default=0.5, help="ElasticNet alpha")
    parser.add_argument("--l1-ratio", type=float, default=0.5, help="ElasticNet l1_ratio")
    parser.add_argument("--experiment", type=str, default="housing-price-prediction",
                       help="MLflow experiment name")
    args = parser.parse_args()

    print("="*70)
    print("Housing Price Model Training")
    print("="*70)

    # Setup MLflow
    tracking_uri = get_mlflow_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(args.experiment)

    print(f"\n✓ Connected to Azure ML workspace")
    print(f"  MLflow URI: {tracking_uri}")
    print(f"  Experiment: {args.experiment}")

    # Load and prepare data
    df = load_data()
    X_train, X_test, y_train, y_test, scaler = preprocess_data(df)

    # Start MLflow run
    with mlflow.start_run(run_name=f"elasticnet_alpha_{args.alpha}") as run:

        # Log parameters
        mlflow.log_param("alpha", args.alpha)
        mlflow.log_param("l1_ratio", args.l1_ratio)
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))
        mlflow.log_param("n_features", X_train.shape[1])

        # Log tags
        mlflow.set_tag("model_type", "regression")
        mlflow.set_tag("dataset", "housing_synthetic")
        mlflow.set_tag("framework", "sklearn")

        # Train model
        model = train_model(args.alpha, args.l1_ratio, X_train, y_train)

        # Evaluate
        rmse, mae, r2, predictions = evaluate_model(model, X_test, y_test)

        # Log metrics
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)

        # Log model with signature
        # Interview tip: Signature enables automatic input validation!
        signature = infer_signature(X_train, predictions)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=X_train.iloc[:5],
            registered_model_name=None  # Register separately for control
        )

        # Log feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'coefficient': model.coef_
        }).sort_values('coefficient', ascending=False)

        print(f"\nTop 5 Important Features:")
        for idx, row in feature_importance.head().iterrows():
            print(f"  {row['feature']}: {row['coefficient']:,.2f}")

        # Save feature importance as artifact
        feature_importance.to_csv("feature_importance.csv", index=False)
        mlflow.log_artifact("feature_importance.csv")

        print(f"\n✓ Model logged to MLflow")
        print(f"  Run ID: {run.info.run_id}")
        print(f"\nView in Azure ML Studio:")
        print(f"  https://ml.azure.com")
        print(f"  Navigate to: Experiments > {args.experiment}")

        print("\n" + "="*70)
        print("Training Complete!")
        print("="*70)
        print(f"\nNext steps:")
        print(f"  1. Register model:")
        print(f"     python src/register.py --run-id {run.info.run_id}")
        print(f"  2. Deploy model:")
        print(f"     python src/deploy.py --model-name HousingPriceModel")
        print("="*70)

        return run.info.run_id


if __name__ == "__main__":
    main()
