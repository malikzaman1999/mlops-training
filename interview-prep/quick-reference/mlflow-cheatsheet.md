# MLflow Quick Reference Cheatsheet

**Print this! Review it the night before your interview.**

---

## Core Tracking API

```python
import mlflow

# Set tracking server
mlflow.set_tracking_uri("http://localhost:5000")  # or Azure ML workspace URI

# Create/set experiment
mlflow.set_experiment("experiment-name")

# Start run
with mlflow.start_run(run_name="my-run") as run:
    # Log parameters
    mlflow.log_param("alpha", 0.5)
    mlflow.log_params({"alpha": 0.5, "l1_ratio": 0.5})

    # Log metrics
    mlflow.log_metric("rmse", 0.75)
    mlflow.log_metrics({"rmse": 0.75, "mae": 0.60})
    mlflow.log_metric("loss", 0.5, step=10)  # With step for per-epoch

    # Log artifacts
    mlflow.log_artifact("plot.png")
    mlflow.log_artifacts("outputs/")  # Directory

    # Log tags
    mlflow.set_tag("model_type", "regression")
    mlflow.set_tags({"dataset": "housing", "version": "v2"})

    # Get run info
    run_id = run.info.run_id
```

---

## Autologging

```python
# Enable for all supported frameworks
mlflow.autolog()

# sklearn-specific
mlflow.sklearn.autolog(
    log_input_examples=True,
    log_model_signatures=True,
    log_models=True,
    registered_model_name="MyModel"
)

# Then just train—everything logged automatically
model = ElasticNet(alpha=0.5)
model.fit(X_train, y_train)
```

---

## Models API

```python
from mlflow.models import infer_signature

# Create signature
signature = infer_signature(X_train, predictions)

# Log model
mlflow.sklearn.log_model(
    sk_model=model,
    artifact_path="model",
    signature=signature,
    input_example=X_train[:5],
    registered_model_name="MyModel"  # Auto-register
)

# Save model (local only, no tracking)
mlflow.sklearn.save_model(model, "my_model")

# Load model
model = mlflow.sklearn.load_model("runs:/RUN_ID/model")
model = mlflow.pyfunc.load_model("models:/MyModel/1")  # From registry
```

---

## Model Registry

```python
# Register during logging
mlflow.sklearn.log_model(model, "model", registered_model_name="MyModel")

# Register after logging
mlflow.register_model(
    model_uri="runs:/RUN_ID/model",
    name="MyModel",
    tags={"dataset": "v2"}
)

# Load from registry
model = mlflow.pyfunc.load_model("models:/MyModel/1")  # Version
model = mlflow.pyfunc.load_model("models:/MyModel@champion")  # Alias

# Set alias (modern approach)
from mlflow.tracking import MlflowClient
client = MlflowClient()
client.set_registered_model_alias("MyModel", "champion", "3")
```

---

## Custom Python Models

```python
import mlflow.pyfunc

class MyModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        import joblib
        self.model = joblib.load(context.artifacts["model_path"])

    def predict(self, context, model_input):
        return self.model.predict(model_input)

# Log custom model
mlflow.pyfunc.log_model(
    artifact_path="custom_model",
    python_model=MyModel(),
    artifacts={"model_path": "model.pkl"},
    conda_env="conda.yaml"
)
```

---

## MLflow Projects

**MLproject file:**
```yaml
name: MyProject
conda_env: conda.yaml

entry_points:
  main:
    parameters:
      alpha: {type: float, default: 0.5}
      data: {type: path}
    command: "python train.py --alpha {alpha} --data {data}"
```

**Run:**
```bash
mlflow run . -P alpha=0.8

# From Git
mlflow run https://github.com/user/repo -v main
```

---

## Search & Compare

```python
# Search runs
runs = mlflow.search_runs(
    experiment_ids=["1"],
    filter_string="metrics.rmse < 0.5",
    order_by=["metrics.rmse ASC"],
    max_results=10
)

# Get best run
best_run = runs.iloc[0]
```

---

## MLflow Tracking Server

```bash
# Start server
mlflow server \
  --backend-store-uri postgresql://user:pass@host/db \
  --default-artifact-root s3://bucket/mlflow \
  --host 0.0.0.0 \
  --port 5000
```

---

## Model URI Formats

| Format | Example | Use Case |
|--------|---------|----------|
| Local path | `./my_model` | Testing |
| Run | `runs:/RUN_ID/model` | Load from run |
| Registry version | `models:/MyModel/1` | Specific version |
| Registry alias | `models:/MyModel@champion` | Current champion |
| Cloud storage | `s3://bucket/model` | S3/Azure Blob |

---

## Quick Interview Answers

**Q: What's MLflow?**
> "An open-source platform for the ML lifecycle with four components: Tracking logs experiments, Models packages models standardly, Registry manages versions, Projects ensures reproducibility."

**Q: log_param vs log_metric?**
> "Params are hyperparameters that define the run and don't change—logged once. Metrics are performance numbers that measure results—can log multiple times with steps."

**Q: save_model vs log_model?**
> "save_model writes to local filesystem only. log_model writes AND links to a run for full lineage—use this for production."

**Q: What are flavors?**
> "Different ways to save/load a model. Every model has a framework flavor (sklearn, pytorch) and a pyfunc flavor for universal deployment."

**Q: Purpose of signatures?**
> "Define expected input/output schema. Enables automatic validation at serving time, generates API docs, prevents runtime errors."

---

## Common Patterns

**Hyperparameter sweep:**
```python
from sklearn.model_selection import ParameterGrid

mlflow.set_experiment("tuning")

for params in ParameterGrid({"alpha": [0.1, 0.5, 1.0]}):
    with mlflow.start_run():
        mlflow.log_params(params)
        model = ElasticNet(**params)
        model.fit(X_train, y_train)
        rmse = evaluate(model, X_test, y_test)
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(model, "model")
```

**Load best model:**
```python
experiment = mlflow.get_experiment_by_name("tuning")
best_run = mlflow.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.rmse ASC"],
    max_results=1
).iloc[0]

best_model = mlflow.pyfunc.load_model(f"runs:/{best_run.run_id}/model")
```

---

## Pro Tips

✅ Always use `log_model` not `save_model` for production
✅ Infer signatures automatically: `infer_signature(X, predictions)`
✅ Use aliases (@champion) not stages for deployment
✅ Set tracking URI once at the start of scripts
✅ Log git commit SHA: `mlflow.set_tag("git_sha", sha)`
✅ Use `autolog()` for rapid experimentation
✅ Pin exact package versions in conda.yaml
✅ Test model loading in a clean environment before claiming reproducibility

---

**Last-Minute Review:**
- MLflow = Tracking + Models + Registry + Projects
- Tracking = experiments → runs → params/metrics/artifacts
- Models = framework flavor + pyfunc flavor
- Registry = versioned models with aliases for deployment
- Always log models WITH runs for lineage

Good luck! 🚀
