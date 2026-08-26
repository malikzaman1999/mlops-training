# MLflow Core Concepts - Interview Study Guide

## Table of Contents
1. [What is MLflow?](#what-is-mlflow)
2. [MLflow Tracking](#mlflow-tracking)
3. [MLflow Models](#mlflow-models)
4. [MLflow Model Registry](#mlflow-model-registry)
5. [MLflow Projects](#mlflow-projects)
6. [Tracking Server Architecture](#tracking-server-architecture)
7. [Interview Questions & Answers](#interview-questions--answers)

---

## What is MLflow?

### Definition

**MLflow** is an open-source platform for managing the complete machine learning lifecycle. Think of it as **"Version control + packaging + deployment"** for ML.

### The Four Components

| Component | Purpose | Interview Analogy |
|-----------|---------|-------------------|
| **Tracking** | Log experiments, params, metrics | "Git commits for ML runs" |
| **Models** | Package models in standard format | "Docker for ML models" |
| **Registry** | Manage model versions & lifecycle | "GitHub releases for models" |
| **Projects** | Reproducible runs | "Makefiles for ML pipelines" |

### Key Philosophy

**Library-agnostic:** Works with scikit-learn, TensorFlow, PyTorch, XGBoost, or custom code.

**Format-agnostic:** Supports multiple storage backends (local files, S3, Azure Blob, databases).

**Language-agnostic:** Python, R, Java, REST API.

---

## MLflow Tracking

### Core Concepts

```
Tracking Server
├── Experiment (project-level grouping)
│   ├── Run 1 (one training execution)
│   │   ├── Parameters (hyperparameters)
│   │   ├── Metrics (loss, accuracy, RMSE)
│   │   ├── Tags (metadata)
│   │   └── Artifacts (models, plots, data)
│   ├── Run 2
│   └── Run 3...
└── Experiment 2...
```

### The Hierarchy

1. **Tracking Server**: Where all experiments live
2. **Experiment**: Logical grouping (e.g., "Housing Price Prediction")
3. **Run**: One execution of training code (one model)
4. **Logged Data**: Parameters, metrics, tags, artifacts

---

### Basic Tracking Pattern

```python
import mlflow
import mlflow.sklearn
from sklearn.linear_model import ElasticNet

# 1. Set tracking server (optional, defaults to ./mlruns)
mlflow.set_tracking_uri("http://localhost:5000")

# 2. Set/create experiment
mlflow.set_experiment("housing-price-prediction")

# 3. Start a run
with mlflow.start_run():
    # 4. Log parameters
    mlflow.log_param("alpha", 0.5)
    mlflow.log_param("l1_ratio", 0.5)

    # 5. Train model
    model = ElasticNet(alpha=0.5, l1_ratio=0.5)
    model.fit(X_train, y_train)

    # 6. Log metrics
    predictions = model.predict(X_test)
    rmse = mean_squared_error(y_test, predictions, squared=False)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2_score(y_test, predictions))

    # 7. Log the model
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="HousingPriceModel"  # Optional: auto-register
    )

    # 8. Log any files (plots, datasets, etc.)
    mlflow.log_artifact("confusion_matrix.png")
```

---

### Tracking API Reference

#### Experiment Management

```python
# Create experiment (returns experiment_id)
experiment_id = mlflow.create_experiment(
    name="my-experiment",
    artifact_location="s3://my-bucket/mlflow",  # Optional
    tags={"team": "ml-team", "project": "churn"}
)

# Set active experiment (auto-creates if missing)
mlflow.set_experiment("my-experiment")

# Get experiment details
experiment = mlflow.get_experiment("experiment_id")
# experiment.name, experiment.experiment_id, experiment.artifact_location
```

#### Run Management

```python
# Start run (context manager - recommended)
with mlflow.start_run(run_name="elasticnet-alpha-0.5") as run:
    mlflow.log_param("alpha", 0.5)
    # run.info.run_id available here

# Manual run control (less common)
run = mlflow.start_run()
mlflow.log_param("alpha", 0.5)
mlflow.end_run()

# Get current active run
active_run = mlflow.active_run()

# Get last completed run
last_run = mlflow.last_active_run()
```

#### Logging Functions

```python
# Parameters (hyperparameters, config)
mlflow.log_param("learning_rate", 0.01)
mlflow.log_params({
    "alpha": 0.5,
    "l1_ratio": 0.5,
    "max_iter": 1000
})

# Metrics (numbers that change over time)
mlflow.log_metric("rmse", 0.75)
mlflow.log_metric("loss", 0.5, step=10)  # For tracking per epoch/iteration
mlflow.log_metrics({
    "rmse": 0.75,
    "mae": 0.60,
    "r2": 0.85
})

# Tags (metadata, searchable)
mlflow.set_tag("model_type", "regression")
mlflow.set_tags({
    "dataset": "housing",
    "git_commit": "abc123",
    "environment": "production"
})

# Artifacts (files: models, plots, data)
mlflow.log_artifact("plot.png")  # Single file
mlflow.log_artifacts("outputs/")  # Entire directory
mlflow.log_dict({"config": "value"}, "config.json")  # Dict → JSON
mlflow.log_text("Some text", "notes.txt")  # String → file
```

---

### Autologging

**Automatically log parameters, metrics, and models** for supported frameworks.

```python
import mlflow

# Enable autologging for all supported libraries
mlflow.autolog()

# OR library-specific
mlflow.sklearn.autolog(
    log_input_examples=True,  # Log sample input data
    log_model_signatures=True,  # Log input/output schema
    log_models=True,  # Log the trained model
    registered_model_name="MyModel"  # Auto-register
)

# Now just train—everything is logged automatically
model = ElasticNet(alpha=0.5)
model.fit(X_train, y_train)
# ↑ Automatically logs: alpha, fit_intercept, predictions, model, metrics
```

**What gets logged:**
- ✅ All model hyperparameters
- ✅ Training metrics (RMSE, MAE, R² for regression; accuracy, precision, recall for classification)
- ✅ Model artifact
- ✅ Model signature (input/output schema)
- ✅ Input example (if enabled)

**Supported Libraries:**
- scikit-learn, XGBoost, LightGBM
- TensorFlow, Keras, PyTorch
- Spark MLlib, Statsmodels, Fastai

---

### System Tags

MLflow automatically creates these tags (prefix: `mlflow.`):

| Tag | Description |
|-----|-------------|
| `mlflow.runName` | Human-readable run name |
| `mlflow.source.name` | Source file (e.g., train.py) |
| `mlflow.source.type` | Execution type (local, cloud) |
| `mlflow.user` | User who ran the code |
| `mlflow.source.git.commit` | Git commit SHA |
| `mlflow.source.git.branch` | Git branch |
| `mlflow.source.git.repoURL` | Git repository URL |

---

### Comparing Multiple Runs

```python
# Example: Grid search over hyperparameters
from sklearn.model_selection import ParameterGrid

param_grid = {
    'alpha': [0.1, 0.5, 1.0],
    'l1_ratio': [0.2, 0.5, 0.8]
}

mlflow.set_experiment("elasticnet-tuning")

for params in ParameterGrid(param_grid):
    with mlflow.start_run():
        mlflow.log_params(params)

        model = ElasticNet(**params)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        rmse = mean_squared_error(y_test, predictions, squared=False)

        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, "model")
```

**Result:** 9 runs logged (3 alphas × 3 l1_ratios), easily comparable in MLflow UI.

---

## MLflow Models

### What is an MLflow Model?

A **standardized package format** for ML models that can be deployed anywhere.

### Model Storage Format

When you save a model, MLflow creates this structure:

```
model/
├── MLmodel                    # Metadata file (YAML)
├── model.pkl                  # Serialized model
├── conda.yaml                 # Conda environment
├── python_env.yaml            # Python venv environment
├── requirements.txt           # Pip requirements
└── input_example.json         # Sample input (optional)
```

### The MLmodel File

```yaml
artifact_path: model
flavors:
  python_function:
    env: conda.yaml
    loader_module: mlflow.sklearn
    model_path: model.pkl
    predict_fn: predict
    python_version: 3.10.0
  sklearn:
    pickled_model: model.pkl
    serialization_format: cloudpickle
    sklearn_version: 1.2.2
mlflow_version: 2.9.0
model_uuid: 12345abc
run_id: abc123def456
signature:
  inputs: '[{"name": "feature1", "type": "double"}, ...]'
  outputs: '[{"type": "double"}]'
```

---

### Model Flavors

**Flavor = a way to save/load a model**

Every MLflow model has ≥1 flavor:

1. **Library-Specific Flavor** (e.g., `sklearn`, `tensorflow`, `pytorch`)
   - Uses library's native save/load
   - Preserves all library-specific functionality

2. **Python Function Flavor** (`pyfunc`)
   - Generic Python function interface
   - Works with ANY Python model
   - Standard interface: `model.predict(data)`

**Example:** An sklearn model has TWO flavors:
- `sklearn`: Load with `mlflow.sklearn.load_model()` → full sklearn API
- `python_function`: Load with `mlflow.pyfunc.load_model()` → generic `.predict()`

---

### Model API: Save vs Log

```python
# save_model: Save to LOCAL filesystem
mlflow.sklearn.save_model(
    sk_model=model,
    path="my_model",  # Local directory path
    conda_env="conda.yaml",
    signature=signature
)
# Result: ./my_model/ directory created
# NOT visible in MLflow UI

# log_model: Log to TRACKING SERVER
with mlflow.start_run():
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",  # Relative to run's artifact root
        registered_model_name="MyModel",  # Optional: register immediately
        signature=signature,
        input_example=X_test[:5]
    )
# Result: Model visible in MLflow UI under this run's artifacts
```

**Key Difference:**
- `save_model`: Just saves to disk (no tracking)
- `log_model`: Saves AND links to a run (full lineage)

---

### Model Signatures

**Defines the input/output schema** for your model.

```python
from mlflow.models import infer_signature

# Automatic inference (recommended)
predictions = model.predict(X_train)
signature = infer_signature(X_train, predictions)

# Manual definition
from mlflow.types import Schema, ColSpec

input_schema = Schema([
    ColSpec("double", "feature1"),
    ColSpec("double", "feature2"),
    ColSpec("string", "category")
])
output_schema = Schema([ColSpec("double")])
signature = ModelSignature(inputs=input_schema, outputs=output_schema)

# Log with signature
mlflow.sklearn.log_model(model, "model", signature=signature)
```

**Why Signatures Matter:**

✅ Validates inputs at serving time (prevents crashes)
✅ Auto-generates API documentation
✅ Enables schema evolution tracking
✅ Required for some deployment targets (e.g., SageMaker)

---

### Loading Models

```python
# Load from a run
model = mlflow.sklearn.load_model("runs:/abc123/model")

# Load from registry
model = mlflow.pyfunc.load_model("models:/MyModel/1")  # Version 1
model = mlflow.pyfunc.load_model("models:/MyModel/Production")  # Stage
model = mlflow.pyfunc.load_model("models:/MyModel@champion")  # Alias

# Load from local path
model = mlflow.sklearn.load_model("./my_model")

# Load from S3/Azure Blob
model = mlflow.pyfunc.load_model("s3://bucket/path/to/model")
```

**Model URI Formats:**

| Format | Example | Use Case |
|--------|---------|----------|
| Local path | `./my_model` | Testing locally |
| Run-relative | `runs:/abc123/model` | Load from specific run |
| Registry version | `models:/MyModel/1` | Load specific version |
| Registry stage | `models:/MyModel/Production` | Load current prod model |
| Registry alias | `models:/MyModel@champion` | Load aliased model |
| Cloud storage | `s3://bucket/model` | Load from S3/Azure/GCS |

---

### Custom Python Models

For **unsupported libraries** or **custom inference logic**:

```python
import mlflow.pyfunc

class MyCustomModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        # Load model and dependencies
        import joblib
        self.model = joblib.load(context.artifacts["model_path"])

    def predict(self, context, model_input):
        # Custom inference logic
        preprocessed = self.preprocess(model_input)
        predictions = self.model.predict(preprocessed)
        return self.postprocess(predictions)

    def preprocess(self, data):
        # Custom preprocessing
        return data * 2

    def postprocess(self, predictions):
        # Custom postprocessing
        return predictions.tolist()

# Log custom model
with mlflow.start_run():
    mlflow.pyfunc.log_model(
        artifact_path="custom_model",
        python_model=MyCustomModel(),
        artifacts={"model_path": "model.pkl"},
        conda_env="conda.yaml"
    )
```

---

## MLflow Model Registry

### What is the Model Registry?

A **centralized hub for managing model versions, stages, and deployments**.

Think: **"GitHub releases for ML models"**

### Key Concepts

1. **Registered Model**: A named model (e.g., "HousingPriceModel")
2. **Model Version**: Specific instance (Version 1, 2, 3...)
3. **Stage/Alias**: Deployment status (Staging, Production, or custom aliases)
4. **Description & Tags**: Metadata for discoverability

---

### Registering Models

#### Option 1: During Training

```python
with mlflow.start_run():
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="HousingPriceModel"  # Auto-registers
    )
# Creates Version 1 (or next version if name exists)
```

#### Option 2: After Training

```python
# Register an already-logged model
mlflow.register_model(
    model_uri="runs:/abc123/model",
    name="HousingPriceModel",
    tags={"dataset": "housing-v2", "algorithm": "elasticnet"}
)
```

#### Option 3: Via MLflow UI

1. Navigate to a run
2. Click on the model in Artifacts
3. Click "Register Model"
4. Select existing name or create new

---

### Model Versioning

```python
# First registration
mlflow.sklearn.log_model(model, "model", registered_model_name="MyModel")
# → Creates "MyModel" Version 1

# Train again with same name
mlflow.sklearn.log_model(model, "model", registered_model_name="MyModel")
# → Creates "MyModel" Version 2

# Versions are immutable—can't overwrite Version 1
```

---

### Stages vs Aliases (Modern Approach)

#### Old Way: Fixed Stages

```
Stages (Legacy):
- Staging: Model under evaluation
- Production: Live model
- Archive: Retired model
```

#### New Way: Flexible Aliases

```python
# Assign custom aliases
client = mlflow.MlflowClient()

# Set Version 3 as production champion
client.set_registered_model_alias("MyModel", "champion", "3")

# Set Version 4 as challenger for A/B testing
client.set_registered_model_alias("MyModel", "challenger", "4")

# Load by alias
champion = mlflow.pyfunc.load_model("models:/MyModel@champion")
challenger = mlflow.pyfunc.load_model("models:/MyModel@challenger")
```

**Benefits of Aliases:**
- Unlimited custom names (not just 3 stages)
- Better for A/B testing (`@control`, `@variant_a`, `@variant_b`)
- Team-specific workflows (`@qa_approved`, `@security_reviewed`)

---

### Model Lifecycle Management

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Create a registered model
client.create_registered_model(
    name="MyModel",
    tags={"team": "ml-team"},
    description="Production housing price predictor"
)

# Add version-level metadata
client.update_model_version(
    name="MyModel",
    version=1,
    description="ElasticNet with alpha=0.5, l1_ratio=0.5"
)

# Set tags on a version
client.set_model_version_tag("MyModel", "1", "validation_status", "passed")

# Delete a version (only if not in Staging/Production)
client.delete_model_version("MyModel", "1")

# Delete entire model
client.delete_registered_model("MyModel")
```

---

### Loading Registered Models

```python
# By version number
model = mlflow.pyfunc.load_model("models:/MyModel/3")

# By alias
model = mlflow.pyfunc.load_model("models:/MyModel@champion")

# By stage (legacy)
model = mlflow.pyfunc.load_model("models:/MyModel/Production")

# Get model details
client = MlflowClient()
model_version = client.get_model_version("MyModel", "3")
# model_version.run_id, model_version.status, model_version.source
```

---

## MLflow Projects

### What is an MLflow Project?

A **format for packaging reusable, reproducible ML code**.

Think: **"Dockerfile for ML training pipelines"**

---

### MLproject File

```yaml
name: HousingPricePrediction

conda_env: conda.yaml  # or python_env: python_env.yaml, or docker_env: ...

entry_points:
  main:
    parameters:
      alpha: {type: float, default: 0.5}
      l1_ratio: {type: float, default: 0.5}
      data_path: {type: path, default: "data/train.csv"}
    command: "python train.py --alpha {alpha} --l1_ratio {l1_ratio} --data {data_path}"

  evaluate:
    parameters:
      model_uri: {type: string}
      test_data: {type: path}
    command: "python evaluate.py --model {model_uri} --data {test_data}"
```

### conda.yaml (Environment Spec)

```yaml
name: housing-env
channels:
  - conda-forge
dependencies:
  - python=3.10
  - pip
  - pip:
    - mlflow==2.9.0
    - scikit-learn==1.2.2
    - pandas==2.0.0
    - numpy==1.24.0
```

---

### Running Projects

#### Via CLI

```bash
# Run locally
mlflow run . -P alpha=0.8 -P l1_ratio=0.3

# Run from Git
mlflow run https://github.com/user/repo -v main

# Run specific entry point
mlflow run . --entry-point evaluate -P model_uri=models:/MyModel/1
```

#### Via Python API

```python
import mlflow

mlflow.projects.run(
    uri=".",  # Current directory, or Git URL
    entry_point="main",
    parameters={"alpha": 0.8, "l1_ratio": 0.3},
    experiment_name="housing-price-tuning",
    env_manager="conda"  # or "virtualenv", "local"
)
```

---

## Tracking Server Architecture

### Storage Components

```
MLflow Tracking Server
├── Backend Store (metadata)
│   └── Experiments, runs, params, metrics, tags
│       Options: FileStore (local), SQLite, PostgreSQL, MySQL, Azure SQL
│
└── Artifact Store (large files)
    └── Models, plots, datasets
        Options: Local filesystem, S3, Azure Blob, GCS, HDFS
```

---

### Deployment Scenarios

#### Scenario 1: Local Development

```python
# No server needed—everything stored locally
mlflow.set_tracking_uri("./mlruns")  # or just don't set (default)
```

**Storage:**
- Backend: `./mlruns/` (FileStore)
- Artifacts: `./mlruns/<exp_id>/<run_id>/artifacts/`

---

#### Scenario 2: Localhost + SQLite

```python
mlflow.set_tracking_uri("sqlite:///mlflow.db")
```

**Storage:**
- Backend: `mlflow.db` (SQLite)
- Artifacts: `./mlruns/` (local files)

---

#### Scenario 3: Remote Server

```bash
# Start server
mlflow server \
  --backend-store-uri postgresql://user:pass@host:5432/mlflowdb \
  --default-artifact-root s3://my-bucket/mlflow \
  --host 0.0.0.0 \
  --port 5000
```

```python
# Client code
mlflow.set_tracking_uri("http://my-server:5000")
```

**Storage:**
- Backend: PostgreSQL (remote DB)
- Artifacts: S3 (cloud storage)

---

#### Scenario 4: Artifact Proxy (Secure)

**Problem:** Clients need S3 credentials to upload artifacts.

**Solution:** Tracking server proxies artifact uploads.

```bash
mlflow server \
  --backend-store-uri postgresql://... \
  --default-artifact-root s3://bucket/mlflow \
  --serve-artifacts  # ← Enable proxy
```

Now clients upload to tracking server, which forwards to S3.

---

## Interview Questions & Answers

### Q1: "What are the four components of MLflow?"

**Answer:**
> "MLflow has four components: Tracking, which logs experiments, parameters, metrics, and artifacts; Models, which packages models in a standard format for deployment; Registry, which manages model versions and lifecycle stages; and Projects, which makes training code reproducible with environment specifications. Together, they cover the full ML lifecycle from experimentation to production."

---

### Q2: "Explain the difference between `log_param` and `log_metric`."

**Answer:**
> "Parameters are hyperparameters or configuration values that don't change during a run—like learning rate, tree depth, or alpha in ElasticNet. They're logged once per run with `log_param`. Metrics are numbers that measure model performance or training progress—like loss, accuracy, or RMSE. They can be logged multiple times per run, often with a step number to track changes over epochs, using `log_metric`. The key difference: params define the run, metrics evaluate it."

---

### Q3: "What's the purpose of model signatures?"

**Answer:**
> "Model signatures define the expected input and output schema for a model—like a function signature in code. They specify column names, data types, and shapes. This is critical for production because it enables automatic validation: if someone sends the wrong input format, the error happens before prediction, not during or after. Signatures also auto-generate API documentation, enable schema evolution tracking, and are required for some deployment targets like SageMaker. I always use `infer_signature` during training to capture them automatically."

---

### Q4: "How would you compare 50 different hyperparameter combinations?"

**Answer:**
> "I'd use MLflow Tracking with a loop over a parameter grid. I'd set one experiment name for all runs, then iterate through combinations, logging each as a separate run with `mlflow.start_run`. Inside each run, I'd log the parameters, train the model, compute metrics, and log the model artifact. After all runs complete, I'd use the MLflow UI to sort by the key metric—like RMSE—to find the best. For programmatic selection, I'd use the MLflow search API with a filter like `metrics.rmse < 0.5` and sort by rmse ascending."

---

### Q5: "What's the difference between `save_model` and `log_model`?"

**Answer:**
> "`save_model` saves a model to the local filesystem in MLflow format, but it's not linked to any run—it's just a directory of files. `log_model` saves the model AND associates it with an MLflow run, creating full lineage: you can trace the model back to the exact code, data, and parameters that created it. For production systems, I always use `log_model` because reproducibility and auditability require that linkage. `save_model` is useful for quick local testing or when you need a model file outside the tracking context."

---

### Q6: "Walk me through registering and deploying a model."

**Answer:**
> "After training, I log the model with `mlflow.sklearn.log_model`, passing `registered_model_name` to auto-register it in the Model Registry. This creates Version 1. Before promoting to production, I'd add metadata: a description of what changed, tags for the dataset version and validation metrics. I'd assign an alias like `@champion` to mark it for deployment. In the deployment step, I'd load the model using `mlflow.pyfunc.load_model('models:/MyModel@champion')`, which always points to the current champion regardless of version number. This decouples deployment code from specific versions, making rollbacks as simple as reassigning the alias."

---

### Q7: "How does MLflow handle different ML frameworks?"

**Answer:**
> "MLflow uses a flavor system. Every model is saved with at least two flavors: a framework-specific flavor like `sklearn`, `tensorflow`, or `pytorch`, and a generic `python_function` flavor. The framework flavor preserves all native functionality—like PyTorch's state dict or sklearn's `predict_proba`. The python_function flavor provides a universal interface: every model has a `.predict()` method, making deployment code framework-agnostic. When I load a model for serving, I usually use `mlflow.pyfunc.load_model` to get the generic interface, which works with any deployment target."

---

### Q8: "What's the purpose of MLflow Projects?"

**Answer:**
> "MLflow Projects make training code reproducible and portable. An `MLproject` file specifies the environment (conda, docker, or virtualenv), entry points (like `train` or `evaluate`), and parameters. This means anyone can run `mlflow run <repo>` and get the exact same environment and results, without manually setting up dependencies or figuring out command-line arguments. It's especially useful for: sharing code with teammates, running the same code across different environments like local and cloud, and automating pipelines where one step's output feeds into another."

---

### Q9: "How would you set up MLflow for a team of 10 data scientists?"

**Answer:**
> "I'd deploy a central MLflow Tracking Server with a PostgreSQL backend store for metadata and Azure Blob Storage or S3 for artifacts. I'd enable artifact proxying so data scientists don't need cloud credentials—they just point to the tracking server. For access control, I'd put the server behind a VPN or use authentication middleware. I'd create a shared conda environment with mlflow and common libraries. For organization, I'd establish naming conventions: experiment names by project, tags for dataset versions and model types. I'd also set up regular cleanup jobs to archive old experiments and free up storage."

---

### Q10: "Explain autologging and when you wouldn't use it."

**Answer:**
> "Autologging automatically captures parameters, metrics, and models for supported frameworks like sklearn, XGBoost, and TensorFlow. You call `mlflow.autolog()` once before training, and everything is logged without manual log_param calls. I use it for rapid experimentation and baseline models—it's fast and comprehensive. However, I'd avoid it for: custom models with non-standard interfaces that autolog can't understand; situations where I need custom metrics that autolog doesn't capture; or production pipelines where I want explicit control over what's logged for compliance reasons. In those cases, I fall back to manual logging."

---

## Study Tips

### Practice This

Write the basic tracking pattern from memory:
```python
import mlflow
mlflow.set_experiment("...")
with mlflow.start_run():
    mlflow.log_param(...)
    # train model
    mlflow.log_metric(...)
    mlflow.sklearn.log_model(...)
```

### Memorize Model URI Formats

- `runs:/abc123/model` → load from run
- `models:/MyModel/1` → load version 1
- `models:/MyModel@champion` → load aliased model

### Understand the Tradeoffs

- Local vs remote tracking server
- `save_model` vs `log_model`
- Manual logging vs autologging
- Stages vs aliases

---

## Summary: Key Takeaways

✅ **Tracking = logging runs** (params, metrics, artifacts)
✅ **Models = standardized packaging** (deploy anywhere)
✅ **Registry = version control for models** (stages/aliases)
✅ **Projects = reproducible environments** (conda, docker)
✅ **Signatures define I/O schemas** (prevent serving errors)
✅ **Autologging = automatic tracking** (fast, but less control)

---

**Time to Complete:** 3-4 hours
**Next:** Study Guide 02 - Azure ML Fundamentals
