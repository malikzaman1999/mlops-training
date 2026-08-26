# Basic MLflow Tracking Example

This example demonstrates core MLflow tracking concepts that are essential for interviews.

## What You'll Learn

✅ **Core Tracking API:**
- `mlflow.set_tracking_uri()` - Connect to tracking server
- `mlflow.set_experiment()` - Organize runs into experiments
- `mlflow.start_run()` - Begin tracking a training run

✅ **Logging:**
- `mlflow.log_param()` - Log hyperparameters
- `mlflow.log_metric()` - Log performance metrics
- `mlflow.log_artifact()` - Log files (plots, data, configs)
- `mlflow.sklearn.log_model()` - Log trained model

✅ **Model Signatures:**
- Why they matter for production
- How to infer them automatically

✅ **Autologging:**
- Automatic parameter/metric/model capture
- When to use it vs manual logging

✅ **Hyperparameter Sweeps:**
- Tracking multiple experiments systematically
- Finding the best model

## Prerequisites

1. **Python 3.8+**
2. **MLflow installed** (see requirements.txt)

## Setup

### Step 1: Install Dependencies

```bash
cd interview-prep/code-examples/basic-mlflow-tracking
pip install -r requirements.txt
```

### Step 2: Start MLflow Tracking Server

Open a **separate terminal** and run:

```bash
mlflow server --host 127.0.0.1 --port 5000
```

Keep this running! It stores all your experiments.

### Step 3: Open MLflow UI

Open your browser and go to:
```
http://127.0.0.1:5000
```

You'll see the MLflow UI where all your runs will appear.

## Running the Examples

### Example 1: Basic Tracking

Train a single model with MLflow tracking:

```bash
python train.py --demo basic
```

**What this does:**
- Generates synthetic regression data
- Trains an ElasticNet model
- Logs parameters: `alpha`, `l1_ratio`, `model_type`
- Logs metrics: `rmse`, `mae`, `r2`
- Logs the trained model with signature
- Demonstrates loading the model back

**Check the UI:**
- You'll see a run under the `basic-tracking-demo` experiment
- Click on it to see logged parameters, metrics, and artifacts
- The `model` artifact is the trained model

### Example 2: Autologging

See how autologging automatically captures everything:

```bash
python train.py --demo autolog
```

**What this does:**
- Enables `mlflow.sklearn.autolog()`
- Trains a model normally (no manual logging)
- MLflow automatically captures params, metrics, and model
- Shows you can still add custom metrics

**Interview Tip:** Explain when to use autolog vs manual logging:
- **Autolog:** Rapid experimentation, prototyping
- **Manual:** Production, need fine-grained control

### Example 3: Hyperparameter Sweep

Try multiple hyperparameter combinations:

```bash
python train.py --demo sweep
```

**What this does:**
- Tests 9 combinations of `alpha` and `l1_ratio`
- Logs each as a separate run
- Compares all runs to find the best

**Check the UI:**
- Go to the `hyperparameter-sweep` experiment
- Click "Chart" to visualize metrics across runs
- Sort by `rmse` to find the best model

**Interview Question:** "How would you find the best model from a sweep?"
```python
import mlflow

experiment = mlflow.get_experiment_by_name("hyperparameter-sweep")
runs = mlflow.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.rmse ASC"],
    max_results=1
)
best_run = runs.iloc[0]
print(f"Best run: {best_run.run_id}, RMSE: {best_run['metrics.rmse']}")
```

### Example 4: Run All Demos

```bash
python train.py --demo all
```

This runs all three demos sequentially.

### Example 5: Custom Hyperparameters

```bash
python train.py --demo basic --alpha 0.8 --l1-ratio 0.3
```

Try different values and see how metrics change!

## Understanding the Code

### Key Code Sections

**1. Setting up tracking:**
```python
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("my-experiment")
```

**2. Logging a training run:**
```python
with mlflow.start_run():
    mlflow.log_param("alpha", 0.5)
    mlflow.log_metric("rmse", 0.75)
    mlflow.sklearn.log_model(model, "model", signature=signature)
```

**3. Loading a model:**
```python
model = mlflow.sklearn.load_model("runs:/RUN_ID/model")
predictions = model.predict(X_new)
```

## Interview Practice

### Questions to Answer Out Loud

1. **What's the difference between a parameter and a metric?**
   - Parameters: Hyperparameters that define the model (logged once)
   - Metrics: Performance measurements (can log multiple times)

2. **What's the difference between `save_model` and `log_model`?**
   - `save_model`: Saves to local filesystem only
   - `log_model`: Saves AND links to a run for full lineage (use this!)

3. **What is a model signature and why does it matter?**
   - Defines expected input/output schema
   - Enables automatic validation at serving time
   - Prevents runtime errors in production

4. **When would you use autologging vs manual logging?**
   - Autologging: Rapid experimentation, quick prototyping
   - Manual: Production, custom metrics, fine-grained control

5. **How do you organize multiple experiments?**
   - Use experiments to group related runs
   - Use tags to add metadata (team, environment, etc.)
   - Use naming conventions for runs

### Hands-On Practice

Try these exercises:

1. **Modify hyperparameters:**
   - Run with different alpha values
   - Observe how RMSE changes in the UI

2. **Add custom metrics:**
   - Add logging for max error, median error
   - Compare across runs

3. **Log a plot:**
   - Create a scatter plot of actual vs predicted
   - Save as PNG and log with `mlflow.log_artifact()`

4. **Use tags:**
   - Add tags like `mlflow.set_tag("version", "v2")`
   - Filter runs by tags in the UI

5. **Search runs programmatically:**
   - Use `mlflow.search_runs()` to find runs where `rmse < 10`

## Common Issues

### Issue 1: "Connection refused" error
**Solution:** Make sure MLflow server is running:
```bash
mlflow server --host 127.0.0.1 --port 5000
```

### Issue 2: Can't find experiment
**Solution:** Check the tracking URI matches:
```python
print(mlflow.get_tracking_uri())  # Should be http://127.0.0.1:5000
```

### Issue 3: Model not appearing in UI
**Solution:** Make sure you're using `log_model` inside `start_run()` context:
```python
with mlflow.start_run():
    mlflow.sklearn.log_model(model, "model")  # Inside context!
```

## Next Steps

After mastering this example:

1. **Try with your own data:** Replace `generate_sample_data()` with real dataset
2. **Azure ML integration:** See `../azure-ml-integration/` example
3. **Model Registry:** See `../model-registry-workflow/` example
4. **Production deployment:** See `../production-deployment/` example

## Interview Cheat Sheet

**Quick answers for common questions:**

```python
# Set tracking server
mlflow.set_tracking_uri("http://localhost:5000")

# Create experiment
mlflow.set_experiment("my-exp")

# Log run
with mlflow.start_run():
    mlflow.log_param("alpha", 0.5)      # Hyperparameter
    mlflow.log_metric("rmse", 0.75)     # Performance metric
    mlflow.log_artifact("plot.png")     # File
    mlflow.sklearn.log_model(           # Model
        model,
        "model",
        signature=infer_signature(X, y)
    )

# Load model
model = mlflow.sklearn.load_model("runs:/RUN_ID/model")

# Search runs
runs = mlflow.search_runs(
    experiment_ids=["1"],
    filter_string="metrics.rmse < 0.5",
    order_by=["metrics.rmse ASC"]
)
```

Good luck with your interview! 🚀
