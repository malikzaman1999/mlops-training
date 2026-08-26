# Production Deployment Patterns - Study Guide

## Table of Contents
1. [CI/CD for ML](#cicd-for-ml)
2. [Deployment Strategies](#deployment-strategies)
3. [Monitoring & Observability](#monitoring--observability)
4. [Model Drift Detection](#model-drift-detection)
5. [Continuous Training](#continuous-training)
6. [Production Architecture Patterns](#production-architecture-patterns)
7. [Interview Questions & Answers](#interview-questions--answers)

---

## CI/CD for ML

### The Two Pipelines

**Key Insight:** ML needs TWO CI/CD pipelines:

```
Pipeline 1: ML Pipeline CI/CD
├── Trigger: Code change to training pipeline
├── Tests: Data validation, model tests, integration tests
└── Output: Deployed training pipeline

Pipeline 2: Model CI/CD
├── Trigger: New trained model (from training pipeline)
├── Tests: Model validation, performance gates
└── Output: Deployed model to endpoint
```

---

### ML Pipeline CI/CD (GitHub Actions Example)

**.github/workflows/ml-pipeline-ci.yml**

```yaml
name: ML Pipeline CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'tests/**'
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run unit tests
        run: pytest tests/unit --cov=src

      - name: Run data validation tests
        run: pytest tests/data

      - name: Run model tests
        run: pytest tests/model

  deploy-pipeline:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy Training Pipeline
        run: |
          az ml job create \
            --file pipeline.yml \
            --resource-group ${{ secrets.RESOURCE_GROUP }} \
            --workspace-name ${{ secrets.WORKSPACE_NAME }}
```

---

### Model CI/CD Pattern

```python
# In training script: Automatic validation & registration

import mlflow
from azure.ai.ml import MLClient

# After training
with mlflow.start_run():
    # ... training code ...

    # Evaluate model
    predictions = model.predict(X_test)
    rmse = mean_squared_error(y_test, predictions, squared=False)

    # Load baseline model for comparison
    try:
        baseline = mlflow.pyfunc.load_model("models:/ProductionModel@champion")
        baseline_preds = baseline.predict(X_test)
        baseline_rmse = mean_squared_error(y_test, baseline_preds, squared=False)

        # Only register if better than baseline
        if rmse < baseline_rmse * 0.95:  # 5% improvement required
            mlflow.log_metric("rmse", rmse)
            mlflow.sklearn.log_model(
                model,
                "model",
                registered_model_name="ProductionModel"
            )
            print(f"✅ Model registered: RMSE {rmse:.4f} < Baseline {baseline_rmse:.4f}")
        else:
            print(f"❌ Model not registered: RMSE {rmse:.4f} >= Baseline {baseline_rmse:.4f}")

    except Exception as e:
        # No baseline exists yet—register first model
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, "model", registered_model_name="ProductionModel")
        print(f"✅ First model registered: RMSE {rmse:.4f}")
```

---

### Testing Pyramid for ML

```
           ╱╲
          ╱  ╲
         ╱ E2E╲         ← End-to-end: Full pipeline tests
        ╱──────╲
       ╱ Model ╲        ← Model: Quality gates, bias tests
      ╱  Tests  ╲
     ╱──────────╲
    ╱  Integration╲     ← Integration: Component compatibility
   ╱    Tests     ╲
  ╱──────────────╲
 ╱  Data Validation╲    ← Data: Schema, distributions, quality
╱     Unit Tests    ╲   ← Unit: Pure functions, transformations
────────────────────
```

#### Example Tests

```python
# tests/data/test_data_validation.py
import pytest
import pandas as pd
from src.data import validate_data_schema

def test_schema_validation():
    """Test that input data matches expected schema"""
    data = pd.read_csv("data/test_sample.csv")
    assert "feature1" in data.columns
    assert "feature2" in data.columns
    assert "target" in data.columns

def test_no_missing_values_in_key_columns():
    """Test no nulls in required columns"""
    data = pd.read_csv("data/test_sample.csv")
    assert data["target"].notna().all()

def test_feature_ranges():
    """Test features are within expected ranges"""
    data = pd.read_csv("data/test_sample.csv")
    assert (data["feature1"] >= 0).all()
    assert (data["feature1"] <= 100).all()


# tests/model/test_model_quality.py
from src.train import train_model
import pandas as pd

def test_model_minimum_accuracy():
    """Test model meets minimum quality threshold"""
    X_train, y_train, X_test, y_test = load_test_data()
    model = train_model(X_train, y_train)

    predictions = model.predict(X_test)
    rmse = mean_squared_error(y_test, predictions, squared=False)

    assert rmse < 1.0, f"Model RMSE {rmse} exceeds threshold 1.0"

def test_model_predictions_in_valid_range():
    """Test predictions are sensible"""
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)

    # For housing prices, shouldn't predict negative
    assert (predictions >= 0).all()


# tests/integration/test_preprocessing_parity.py
def test_training_serving_preprocessing_parity():
    """Test preprocessing gives same results in training vs serving"""
    from src.preprocessing import preprocess_for_training
    from src.api import preprocess_for_serving

    sample_data = pd.DataFrame({"feature1": [1, 2, 3]})

    train_result = preprocess_for_training(sample_data.copy())
    serve_result = preprocess_for_serving(sample_data.copy())

    pd.testing.assert_frame_equal(train_result, serve_result)
```

---

## Deployment Strategies

### 1. Blue-Green Deployment

**Concept:** Two identical environments, instant switch.

```
Production Traffic
        ↓
    [Load Balancer]
    ╱           ╲
[Blue: v1]   [Green: v2] ← New version
  90%           10%       ← Test with 10% traffic
```

**Azure ML Implementation:**

```python
# Create green deployment
green_deployment = ManagedOnlineDeployment(
    name="green",
    endpoint_name="production-endpoint",
    model=Model(name="ProductionModel", version="2"),
    instance_type="Standard_DS2_v2",
    instance_count=2
)
ml_client.online_deployments.begin_create_or_update(green_deployment).result()

# Test green (0% traffic initially)
test_endpoint(endpoint_name, deployment_name="green")

# Gradual rollout
endpoint.traffic = {"blue": 90, "green": 10}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Monitor for 1 hour
time.sleep(3600)
check_metrics()

# Full cutover
endpoint.traffic = {"blue": 0, "green": 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Delete blue after validation period
ml_client.online_deployments.begin_delete(name="blue", endpoint_name="production-endpoint")
```

**Pros:**
- ✅ Instant rollback
- ✅ Zero downtime
- ✅ Test production environment before switching

**Cons:**
- ❌ 2x infrastructure cost during transition
- ❌ Database schema changes require careful planning

---

### 2. Canary Deployment

**Concept:** Gradually increase traffic to new version.

```
Day 1:  [v1: 95%] [v2: 5%]
Day 2:  [v1: 80%] [v2: 20%]
Day 3:  [v1: 50%] [v2: 50%]
Day 4:  [v1: 20%] [v2: 80%]
Day 5:  [v1: 0%]  [v2: 100%]
```

**Azure ML Implementation:**

```python
def canary_rollout(endpoint_name, old_deployment, new_deployment, steps=5):
    """Gradually shift traffic with monitoring"""
    import time

    for i in range(1, steps + 1):
        new_traffic = int((i / steps) * 100)
        old_traffic = 100 - new_traffic

        print(f"Shifting traffic: {old_deployment}={old_traffic}%, {new_deployment}={new_traffic}%")

        endpoint.traffic = {old_deployment: old_traffic, new_deployment: new_traffic}
        ml_client.online_endpoints.begin_create_or_update(endpoint).result()

        # Monitor for 2 hours between shifts
        time.sleep(7200)

        # Check metrics
        if not check_canary_metrics(new_deployment):
            print("⚠️ Canary failed! Rolling back...")
            endpoint.traffic = {old_deployment: 100, new_deployment: 0}
            ml_client.online_endpoints.begin_create_or_update(endpoint).result()
            return False

    print("✅ Canary rollout successful!")
    return True
```

---

### 3. Shadow Deployment

**Concept:** Run new model in parallel, don't show predictions to users.

```
User Request
    ↓
[Production v1] ──→ Response to user
    ↓ (copy)
[Shadow v2] ──→ Log predictions (not served)
```

**Use Case:** Validate new model on real traffic before risking production.

**Implementation Pattern:**

```python
# In API code
@app.post("/predict")
async def predict(data: PredictionRequest):
    # Production model
    prod_model = load_model("models:/ProductionModel@production")
    prod_prediction = prod_model.predict(data)

    # Shadow model (async, doesn't block response)
    asyncio.create_task(shadow_predict(data, prod_prediction))

    return {"prediction": prod_prediction}

async def shadow_predict(data, prod_prediction):
    """Log shadow model predictions for comparison"""
    shadow_model = load_model("models:/ProductionModel@shadow")
    shadow_prediction = shadow_model.predict(data)

    # Log for later analysis
    log_prediction_comparison(
        input=data,
        prod=prod_prediction,
        shadow=shadow_prediction,
        timestamp=datetime.now()
    )
```

---

### 4. A/B Testing

**Concept:** Random traffic split for controlled experiment.

```
User Request
    ↓
[Random Assignment]
    ↙        ↘
[Model A]  [Model B]
  50%         50%
```

**Track:** Conversion rate, click-through, revenue per prediction.

**Azure ML Pattern:**

```python
# Equal traffic split for A/B test
endpoint.traffic = {"model_a": 50, "model_b": 50}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Track business metrics by deployment
# After 2 weeks, analyze results:
# - Model A: 5.2% conversion
# - Model B: 5.8% conversion → Winner!

# Promote winner
endpoint.traffic = {"model_a": 0, "model_b": 100}
```

---

## Monitoring & Observability

### The Four Golden Signals (Google SRE)

| Signal | What to Monitor | ML-Specific Examples |
|--------|----------------|----------------------|
| **Latency** | How long requests take | p50, p95, p99 prediction time |
| **Traffic** | How many requests | Requests/second, batch job throughput |
| **Errors** | Request failure rate | 4xx (bad input), 5xx (server errors) |
| **Saturation** | How full your system is | CPU%, memory%, queue depth |

---

### ML-Specific Monitoring Layers

#### Layer 1: Infrastructure

```python
# Azure Application Insights (auto-enabled for endpoints)

from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

# Custom metrics
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string="..."))

logger.info("Prediction made", extra={
    "custom_dimensions": {
        "model_version": "v2",
        "prediction_value": 42.5,
        "confidence": 0.85
    }
})
```

**Monitor:**
- Endpoint availability (uptime)
- Request latency (p50, p95, p99)
- Error rates (4xx, 5xx)
- CPU/memory usage

---

#### Layer 2: Input Data Quality

```python
def monitor_input_data(input_df, reference_stats):
    """Check if input data matches expected distribution"""
    from scipy import stats

    alerts = []

    for column in input_df.columns:
        # Kolmogorov-Smirnov test for distribution shift
        ks_statistic, p_value = stats.ks_2samp(
            input_df[column],
            reference_stats[column]
        )

        if p_value < 0.05:  # Significant drift detected
            alerts.append({
                "column": column,
                "ks_stat": ks_statistic,
                "p_value": p_value
            })

    if alerts:
        logger.warning(f"Input drift detected: {alerts}")
        send_alert_to_team(alerts)

    return alerts
```

**Monitor:**
- Missing values
- Out-of-range values
- Unexpected categories
- Distribution shifts

---

#### Layer 3: Model Predictions

```python
def monitor_predictions(predictions, reference_predictions):
    """Check if prediction distribution has changed"""
    import numpy as np

    # Prediction mean shift
    current_mean = np.mean(predictions)
    reference_mean = np.mean(reference_predictions)
    shift_percent = abs(current_mean - reference_mean) / reference_mean

    if shift_percent > 0.10:  # 10% shift threshold
        logger.warning(f"Prediction drift: {shift_percent:.1%} shift in mean")

    # Prediction range
    if np.max(predictions) > np.max(reference_predictions) * 1.5:
        logger.error("Predictions outside expected range!")
```

**Monitor:**
- Prediction distribution
- Confidence scores
- Class balance (classification)
- Outlier predictions

---

#### Layer 4: Model Performance (When Labels Arrive)

```python
def monitor_model_performance(model_id, predictions, actual_labels):
    """Track model accuracy with delayed labels"""
    from sklearn.metrics import mean_squared_error, r2_score

    rmse = mean_squared_error(actual_labels, predictions, squared=False)
    r2 = r2_score(actual_labels, predictions)

    # Log to MLflow for historical tracking
    with mlflow.start_run():
        mlflow.log_metric("production_rmse", rmse)
        mlflow.log_metric("production_r2", r2)
        mlflow.set_tag("model_id", model_id)
        mlflow.set_tag("evaluation_type", "production")

    # Alert if performance degrades
    baseline_rmse = get_baseline_metric("rmse")
    if rmse > baseline_rmse * 1.1:  # 10% degradation
        send_alert(f"Model performance degraded: RMSE {rmse} vs baseline {baseline_rmse}")
```

---

### Monitoring Dashboard (Application Insights + Azure Monitor)

**KQL Queries for Dashboards:**

```kusto
// Prediction latency p95
requests
| where name == "POST /predict"
| summarize percentile(duration, 95) by bin(timestamp, 5m)

// Error rate
requests
| where name == "POST /predict"
| summarize ErrorRate = (countif(success == false) * 100.0) / count() by bin(timestamp, 5m)

// Prediction distribution
customEvents
| where name == "Prediction"
| extend value = todouble(customDimensions["prediction_value"])
| summarize avg(value), stdev(value) by bin(timestamp, 1h)
```

---

## Model Drift Detection

### Types of Drift

| Type | Definition | Example | Detection |
|------|------------|---------|-----------|
| **Data Drift** | Input distribution changes | Age distribution shifts older | KS test, PSI |
| **Prediction Drift** | Output distribution changes | More high-value predictions | Distribution comparison |
| **Concept Drift** | Input-output relationship changes | Same features → different target | Performance metrics |

---

### Data Drift Detection (Evidently Example)

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
import pandas as pd

# Reference data (training data)
reference = pd.read_csv("training_data.csv")

# Current production data
current = pd.read_csv("production_data_week_10.csv")

# Generate drift report
drift_report = Report(metrics=[DataDriftPreset()])
drift_report.run(reference_data=reference, current_data=current)

# Check for drift
drift_detected = drift_report.as_dict()["metrics"][0]["result"]["dataset_drift"]

if drift_detected:
    print("⚠️ Data drift detected!")
    drift_report.save_html("drift_report.html")
    send_alert_to_team("drift_report.html")
else:
    print("✅ No drift detected")
```

---

### Population Stability Index (PSI)

```python
import numpy as np

def calculate_psi(expected, actual, bins=10):
    """Calculate PSI between two distributions"""

    # Create bins based on expected distribution
    breakpoints = np.quantile(expected, np.linspace(0, 1, bins + 1))

    # Calculate percentage in each bin
    expected_percents = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_percents = np.histogram(actual, bins=breakpoints)[0] / len(actual)

    # Calculate PSI
    psi = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))

    # Interpretation:
    # PSI < 0.1: No significant change
    # 0.1 < PSI < 0.2: Moderate change, investigate
    # PSI > 0.2: Significant change, retrain model

    return psi

# Example usage
psi_value = calculate_psi(training_data["age"], production_data["age"])

if psi_value > 0.2:
    print(f"⚠️ Significant drift detected! PSI = {psi_value:.3f}")
    trigger_retraining_pipeline()
```

---

## Continuous Training

### When to Retrain

| Trigger | Frequency | Example |
|---------|-----------|---------|
| **Schedule** | Fixed interval | Weekly/monthly for stable domains |
| **Data Volume** | N new samples | Retrain after 10,000 new labels |
| **Performance** | Metric threshold | RMSE > baseline * 1.1 |
| **Drift** | Statistical test | PSI > 0.2 on key features |
| **Manual** | On demand | After bug fix or new feature |

---

### Automated Retraining Pipeline (Azure ML)

```python
from azure.ai.ml import MLClient, Input, command
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import CronTrigger

# Define retraining pipeline
@pipeline
def retraining_pipeline(training_data, baseline_model):
    """Automated retraining with validation gates"""

    # Step 1: Validate data
    validate_step = data_validation_component(data=training_data)

    # Step 2: Train model
    train_step = training_component(
        data=validate_step.outputs.validated_data
    )

    # Step 3: Evaluate against baseline
    eval_step = evaluation_component(
        candidate_model=train_step.outputs.model,
        baseline_model=baseline_model,
        test_data=training_data
    )

    # Step 4: Conditional registration
    register_step = register_if_better_component(
        candidate=train_step.outputs.model,
        evaluation=eval_step.outputs.metrics
    )

    return register_step.outputs

# Create pipeline
pipeline_job = retraining_pipeline(
    training_data=Input(type="uri_file", path="azureml:latest-data:1"),
    baseline_model="models:/ProductionModel@production"
)

# Schedule weekly
schedule = CronTrigger(
    expression="0 2 * * 0",  # Sunday 2 AM
    time_zone="UTC"
)

ml_client.schedules.begin_create_or_update(
    schedule=schedule,
    job=pipeline_job,
    name="weekly-retraining"
)
```

---

### Validation Gates for Auto-Deployment

```python
def validate_candidate_model(candidate_model, baseline_model, test_data):
    """Only promote model if it passes all gates"""

    gates_passed = True

    # Gate 1: Better than baseline
    candidate_rmse = evaluate(candidate_model, test_data)
    baseline_rmse = evaluate(baseline_model, test_data)

    if candidate_rmse >= baseline_rmse * 0.95:  # Must be 5% better
        print(f"❌ Gate 1 failed: RMSE {candidate_rmse} not better than {baseline_rmse}")
        gates_passed = False

    # Gate 2: No regressions on important segments
    for segment in ["age_under_30", "age_30_50", "age_over_50"]:
        candidate_segment_rmse = evaluate_segment(candidate_model, test_data, segment)
        baseline_segment_rmse = evaluate_segment(baseline_model, test_data, segment)

        if candidate_segment_rmse > baseline_segment_rmse * 1.05:  # Max 5% worse
            print(f"❌ Gate 2 failed: Segment {segment} regressed")
            gates_passed = False

    # Gate 3: Meets minimum business threshold
    if candidate_rmse > 10.0:
        print(f"❌ Gate 3 failed: RMSE {candidate_rmse} exceeds business threshold 10.0")
        gates_passed = False

    # Gate 4: Latency requirement
    avg_latency = measure_inference_latency(candidate_model)
    if avg_latency > 100:  # 100ms max
        print(f"❌ Gate 4 failed: Latency {avg_latency}ms exceeds 100ms")
        gates_passed = False

    if gates_passed:
        print("✅ All gates passed! Promoting to production...")
        promote_to_production(candidate_model)

    return gates_passed
```

---

## Production Architecture Patterns

### Pattern 1: Batch Inference

**When:** Millions of predictions, results not needed immediately.

**Example:** Nightly scoring of all customers for churn risk.

```
Azure Data Lake (customer data)
        ↓
Azure ML Batch Endpoint
        ├── Parallel jobs on compute cluster
        └── Scale: Process 10M rows in 30 mins
        ↓
Azure SQL Database (predictions)
        ↓
Power BI Dashboard (next day)
```

**Code:**

```python
from azure.ai.ml.entities import BatchEndpoint, BatchDeployment

# Create batch endpoint
batch_endpoint = BatchEndpoint(
    name="churn-batch-scoring",
    description="Nightly churn prediction batch job"
)
ml_client.batch_endpoints.begin_create_or_update(batch_endpoint).result()

# Deploy model
batch_deployment = BatchDeployment(
    name="production",
    endpoint_name="churn-batch-scoring",
    model=Model(name="ChurnModel", version="3"),
    compute="batch-cluster",  # Auto-scaling cluster
    instance_count=10,  # Parallel workers
    max_concurrency_per_instance=2,
    mini_batch_size=100
)
ml_client.batch_deployments.begin_create_or_update(batch_deployment).result()

# Invoke batch job
job = ml_client.batch_endpoints.invoke(
    endpoint_name="churn-batch-scoring",
    deployment_name="production",
    input=Input(type="uri_folder", path="azureml://datastores/blobstore/paths/customers/")
)
```

---

### Pattern 2: Real-Time Inference

**When:** Low latency required (< 1 second).

**Example:** Fraud detection API for payment processing.

```
Payment Gateway
    ↓ (HTTPS POST)
Azure ML Online Endpoint
    ├── Auto-scaling (2-10 instances)
    └── Latency: p95 < 200ms
    ↓
Response: {"fraud_probability": 0.15}
```

---

### Pattern 3: Streaming Inference

**When:** Process continuous event stream.

**Example:** Real-time anomaly detection on IoT sensor data.

```
IoT Devices → Azure Event Hub
                    ↓
            Azure Stream Analytics
                    ↓
            ML Model (real-time)
                    ↓
            Alert if anomaly detected
```

---

## Interview Questions & Answers

### Q1: "Explain the difference between blue-green and canary deployment."

**Answer:**
> "Blue-green deployment maintains two complete environments and switches traffic all at once, while canary deployment gradually increases traffic to the new version. Blue-green is faster to rollback—just flip a switch—but costs more because you run two full environments. Canary is more gradual and lower risk because you start with 5% traffic and monitor before increasing, but rollback means gradually shifting traffic back. For ML models, I prefer canary because it lets me validate on real traffic patterns before committing fully, and I can catch issues that only appear at scale."

---

### Q2: "How would you detect data drift in production?"

**Answer:**
> "I'd use statistical tests to compare production input distributions against training data. For numerical features, I'd use the Kolmogorov-Smirnov test or calculate Population Stability Index. For categorical features, I'd compare frequency distributions using chi-square tests. I'd compute these daily and alert if PSI exceeds 0.2, which indicates significant drift. I'd also visualize distributions in dashboards so the team can investigate which specific features are drifting. For implementation, I'd use libraries like Evidently or build custom tests, and integrate drift detection into my monitoring pipeline alongside model performance metrics."

---

### Q3: "Walk through your automated retraining process."

**Answer:**
> "My retraining pipeline has four stages with validation gates. First, data validation: check schema, null rates, and distributions against expected ranges—fail fast if data is corrupted. Second, training: run the pipeline on validated data, logging all experiments to MLflow. Third, evaluation: compare the candidate model against the current production baseline using the same holdout test set—the candidate must improve RMSE by at least 5% and can't regress on any key segment. Fourth, conditional registration: only if all gates pass, register the new version with an alias like @challenger. Deployment is separate—I manually review the challenger and gradually promote via canary. The pipeline runs weekly via schedule, or on-demand when drift alerts trigger."

---

### Q4: "How do you monitor a model in production?"

**Answer:**
> "I monitor at four levels. Infrastructure: endpoint uptime, request latency percentiles, error rates, and resource usage via Application Insights. Input data: track distributions, missing values, and unexpected categories—alert on statistical drift. Model predictions: monitor output distributions and flag outliers—sudden shifts indicate issues. Model performance: when labels arrive, compute actual accuracy metrics and compare to baseline—degradation triggers retraining. I use Azure Monitor dashboards with KQL queries for real-time metrics and weekly automated reports. I also set up alerts: page for endpoint downtime or error spikes, email for drift, Slack notification for performance degradation."

---

### Q5: "What tests would you add to an ML pipeline's CI/CD?"

**Answer:**
> "I follow a testing pyramid. At the base: unit tests for pure functions like feature transformations, ensuring they handle edge cases. Next: data validation tests checking schema, null rates, and value ranges on sample data. Middle layer: model quality tests ensuring trained models meet minimum accuracy thresholds and predictions are in valid ranges. Integration tests verifying that training preprocessing matches serving preprocessing—preventing training-serving skew. Top: end-to-end tests running a full training iteration and checking that artifacts are correctly logged. I'd also add smoke tests for the deployed endpoint and contract tests to ensure API schemas don't break. All these run in GitHub Actions before merging to main."

---

### Q6: "How do you handle schema changes to input data?"

**Answer:**
> "Schema changes require coordinated updates across the full pipeline. For backward-compatible changes like adding optional fields, I update the model signature to accept but not require them, deploy the new API version, then update upstream producers. For breaking changes like renaming or removing fields, I use a phased approach: deploy a new model version that handles both schemas, gradually migrate producers, verify in production, then remove old schema support. I'd also implement schema versioning: clients send a schema version header, and the API routes to the appropriate model. Finally, I add schema validation tests to catch incompatibilities before deployment."

---

### Q7: "Explain how you'd implement shadow deployment."

**Answer:**
> "Shadow deployment runs the new model in parallel with production, logging predictions but not serving them to users. I'd modify the prediction API to call both models asynchronously: the production model's result is returned immediately, while the shadow model's prediction is logged for later analysis. In Azure ML, I'd deploy the shadow model to the same endpoint with 0% traffic allocation, then use custom logging in the API layer to invoke it explicitly. After collecting a week of shadow predictions, I'd compare them against production and eventual labels to validate accuracy, then use the data to test for biases or edge cases before promoting the shadow model to replace production."

---

### Q8: "What metrics would you track for a deployed model?"

**Answer:**
> "I'd track both operational and ML-specific metrics. Operational: request volume, latency p50/p95/p99, error rate, throughput, and infrastructure costs. ML input metrics: feature distributions, null rates, out-of-range values, and data drift scores. ML output metrics: prediction distribution, confidence scores, and prediction drift. When labels arrive: accuracy, precision, recall, RMSE—whatever aligns with the business goal. Business metrics: conversion rate, revenue per prediction, or other downstream KPIs that the model influences. I'd also track metadata: model version, deployment timestamp, and A/B test assignments. All logged to Application Insights and visualized in dashboards."

---

### Q9: "How do you ensure reproducibility in production retraining?"

**Answer:**
> "I control all sources of randomness and version all inputs. I fix random seeds in training code, pin exact dependency versions in conda.yaml, version datasets using MLflow data assets with immutable IDs, log the git commit SHA as a tag, use Docker images for environment consistency, and log all hyperparameters to MLflow. When retraining, I reference the exact data version and environment. Azure ML's job system helps—it hashes the environment and data inputs, so identical inputs always produce identical executions. For validation, I have a reproducibility test: retrain twice with the same inputs and assert the models produce identical predictions."

---

### Q10: "Design a complete production ML architecture on Azure."

**Answer:**
> "I'd build around Azure ML Workspace as the hub. For data: Azure Data Lake stores raw data, Azure ML Data Assets provide versioned references, and Azure ML Pipelines orchestrate preprocessing. For training: Azure ML Compute Clusters autoscale for parallel jobs, code lives in Azure Repos with GitHub Actions CI/CD, MLflow tracks all experiments. For deployment: models go to Azure ML Registry, then to Managed Online Endpoints with blue-green deployments and autoscaling. For monitoring: Application Insights captures endpoint telemetry, custom middleware logs predictions and drift metrics, Azure Monitor dashboards visualize everything, and alerts trigger retraining pipelines. For orchestration: Azure ML Pipelines with event-based and scheduled triggers. For security: Key Vault for secrets, managed identities for authentication, VNet integration for private endpoints."

---

## Summary: Key Takeaways

✅ **Two CI/CD Pipelines**: One for ML code, one for models

✅ **Deployment Strategies**:
- Blue-Green: Fast rollback, 2x cost
- Canary: Gradual, lower risk
- Shadow: Test on real traffic, zero user impact

✅ **Monitoring Layers**: Infrastructure, input data, predictions, performance

✅ **Drift Detection**: PSI, KS test, statistical comparisons

✅ **Continuous Training**: Schedule + drift + performance triggers

✅ **Validation Gates**: Only promote models that pass all checks

✅ **Testing Pyramid**: Unit → Data → Model → Integration → E2E

---

**Time to Complete:** 4-5 hours
**Next:** Study Guide 05 - Interview Questions Bank
**Hands-On:** Code Example - Production Deployment
