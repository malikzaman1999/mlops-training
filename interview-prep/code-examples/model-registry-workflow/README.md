# MLflow Model Registry Workflow Example

This example demonstrates the complete MLflow Model Registry workflow, including versioning, aliases, and the champion/challenger pattern.

## What You'll Learn

✅ **Model Registration:**
- How to register models in MLflow Registry
- Automatic versioning
- Adding tags and metadata

✅ **Model Aliases:**
- Modern approach to model lifecycle (`@champion`, `@challenger`, `@staging`)
- Replacing old stage-based system
- Loading models by alias

✅ **Champion/Challenger Pattern:**
- Industry-standard deployment pattern
- Safe model promotion workflow
- Comparing model versions

✅ **Model Lifecycle:**
- From experimentation to production
- Version management
- Rollback strategies

## Prerequisites

1. **Python 3.8+**
2. **MLflow installed** (see requirements.txt)
3. **MLflow server running**

## Setup

### Step 1: Install Dependencies

```bash
cd interview-prep/code-examples/model-registry-workflow
pip install -r requirements.txt
```

### Step 2: Start MLflow Server

Open a **separate terminal** and run:

```bash
mlflow server --host 127.0.0.1 --port 5000
```

Keep this running throughout the demos.

### Step 3: Open MLflow UI

Browser: http://127.0.0.1:5000

The **Models** tab shows the registry.

## Running the Examples

### Example 1: Champion/Challenger Pattern (Recommended)

This demonstrates the industry-standard deployment pattern:

```bash
python registry_demo.py champion
```

**What this does:**

1. **Trains initial model** (alpha=0.5)
   - Registers as version 1
   - Sets alias `@champion`

2. **Trains challenger model** (alpha=0.3)
   - Registers as version 2
   - Sets alias `@challenger`

3. **Compares versions**
   - Evaluates metrics (RMSE, R2)
   - Determines which is better

4. **Promotes winner**
   - If v2 is better: `@champion` → v2, `@previous` → v1
   - If v1 is better: keeps current champion

5. **Shows final state**
   - Lists all versions with aliases

**Check the UI:**
- Go to http://127.0.0.1:5000
- Click "Models" tab
- Click "HousingPriceModel"
- You'll see versions with their aliases

**Interview Question:** "Explain the champion/challenger pattern"
> "It's a safe model deployment strategy. The current production model is the 'champion'. When you train a new model, you register it as the 'challenger'. You test the challenger in production (via canary, shadow, or A/B testing). If it performs better, you promote it to champion. The old champion becomes 'previous' for easy rollback."

### Example 2: Model Lifecycle

Shows how models progress through their lifecycle:

```bash
python registry_demo.py lifecycle
```

**What this does:**
- Trains 3 model versions
- Assigns lifecycle aliases:
  - `@champion` → Production model
  - `@staging` → Pre-production validation
  - No alias → Experimental/archived

**Interview Question:** "How do you manage model lifecycle?"
> "I use MLflow Model Registry with aliases. Production models get @champion, models being validated get @staging, and experimental models have no alias. To deploy a new model, I promote from staging to champion. The registry maintains full version history for rollback."

### Example 3: Run All Demos

```bash
python registry_demo.py all
```

Runs both demos sequentially.

## Understanding the Code

### Key Concepts

#### 1. Registering Models

```python
# Option 1: During training (automatic)
mlflow.sklearn.log_model(
    model,
    "model",
    registered_model_name="MyModel"  # Auto-registers!
)

# Option 2: After training (manual)
mlflow.register_model(
    model_uri="runs:/RUN_ID/model",
    name="MyModel"
)
```

**Interview tip:** Both create a new version automatically. You can't overwrite versions—registry is immutable!

#### 2. Model Aliases (Modern Approach)

```python
from mlflow.tracking import MlflowClient
client = MlflowClient()

# Set alias
client.set_registered_model_alias(
    name="MyModel",
    alias="champion",
    version="3"
)

# Load by alias (for deployment)
model = mlflow.pyfunc.load_model("models:/MyModel@champion")
```

**Interview tip:** Aliases replace the old stage system (Staging, Production, Archived). Aliases are more flexible!

#### 3. Model URI Formats

| Format | Example | Use Case |
|--------|---------|----------|
| Run | `runs:/abc123/model` | Load from specific run |
| Version | `models:/MyModel/3` | Load specific version |
| Alias | `models:/MyModel@champion` | Load current production model |

**Interview tip:** In production, always use aliases! Never hardcode version numbers.

#### 4. Comparing Versions

```python
# Get model version metadata
mv1 = client.get_model_version("MyModel", "1")
mv2 = client.get_model_version("MyModel", "2")

# Get metrics from original runs
run1 = mlflow.get_run(mv1.run_id)
run2 = mlflow.get_run(mv2.run_id)

rmse1 = run1.data.metrics["rmse"]
rmse2 = run2.data.metrics["rmse"]

# Decide which to promote
if rmse2 < rmse1:
    client.set_registered_model_alias("MyModel", "champion", "2")
```

## Workflow Patterns

### Pattern 1: Champion/Challenger

**Use case:** Safely deploying new models to production

```
Training → Register as challenger → Test in production → Promote to champion
```

**Code:**
```python
# Initial deployment
register_model(..., name="MyModel")
set_alias("MyModel", version="1", alias="champion")

# New model
register_model(..., name="MyModel")  # Auto v2
set_alias("MyModel", version="2", alias="challenger")

# Test challenger (canary deployment, etc.)
# ...

# Promote if better
if challenger_is_better:
    set_alias("MyModel", version="2", alias="champion")
    set_alias("MyModel", version="1", alias="previous")  # For rollback
```

### Pattern 2: Multi-Environment

**Use case:** Separate dev, staging, production environments

```python
# Development
set_alias("MyModel", version="5", alias="dev")

# Staging (for QA)
set_alias("MyModel", version="4", alias="staging")

# Production
set_alias("MyModel", version="3", alias="champion")
```

Each environment loads by alias:
```python
# In staging deployment code
model = mlflow.pyfunc.load_model("models:/MyModel@staging")

# In production deployment code
model = mlflow.pyfunc.load_model("models:/MyModel@champion")
```

### Pattern 3: Rollback

**Use case:** Quick rollback if new model fails

```python
# Before promoting new model, tag current champion
set_alias("MyModel", current_champion_version, "previous")

# Promote new model
set_alias("MyModel", new_version, "champion")

# If problems, instant rollback!
set_alias("MyModel", previous_version, "champion")
```

## Interview Practice

### Questions to Answer Out Loud

1. **What is the MLflow Model Registry?**
   > "A centralized hub for managing ML model versions. It provides versioning, metadata, lifecycle management, and lineage tracking. Models move from experiments to the registry when they're production-ready."

2. **How does versioning work?**
   > "Every time you register a model with the same name, it creates a new version automatically. Versions are immutable—you can't modify them, only create new ones. Each version links back to the MLflow run that created it."

3. **What are model aliases? How do they differ from stages?**
   > "Aliases are labels you assign to model versions, like @champion or @staging. They're flexible and you can have multiple per model. Stages were the old approach (Staging, Production, Archived) with only one model per stage. Aliases are more flexible."

4. **Explain the champion/challenger pattern.**
   > "The champion is the current production model. When you train a new model, you register it as the challenger. You test the challenger in production (canary, shadow, or A/B testing) while champion serves most traffic. If challenger performs better, you promote it to champion. The old champion becomes 'previous' for easy rollback."

5. **How do you load a model for deployment?**
   > "Use `mlflow.pyfunc.load_model('models:/ModelName@alias')`. In production, always reference by alias (e.g., @champion), never hardcode versions. This lets you update the model by changing the alias without changing deployment code."

6. **How do you roll back a model?**
   > "Set the @champion alias back to the previous version. If you tagged the old champion as @previous before promoting, it's instant: `set_alias('MyModel', previous_version, 'champion')`. The registry keeps all versions, so rollback is always possible."

### Hands-On Practice

Try these exercises:

1. **Train 5 models** with different hyperparameters
   - Register all to the same name
   - Observe automatic versioning

2. **Set up dev/staging/prod workflow**
   - Assign different aliases to different versions
   - Load each in separate scripts

3. **Simulate production failure**
   - Promote a new champion
   - "Discover" it's worse
   - Rollback to previous

4. **Add custom tags**
   - Tag models with metadata
   - Filter models by tags

## Common Issues

### Issue 1: "Model name already exists"
**This is expected!** Re-registering creates a new version, it doesn't error. If you're seeing an error, check if you're trying to delete and recreate.

### Issue 2: Can't find model by alias
**Cause:** Alias not set
**Solution:**
```python
client.set_registered_model_alias("MyModel", "champion", "1")
```

### Issue 3: "Version not found"
**Cause:** Version numbers start at 1, not 0
**Solution:** Use `"1"`, `"2"`, etc. (as strings)

### Issue 4: Load fails with signature mismatch
**Cause:** Input data doesn't match model signature
**Solution:** Ensure you logged model with signature:
```python
signature = infer_signature(X_train, predictions)
mlflow.sklearn.log_model(model, "model", signature=signature)
```

## Integration with Azure ML

This same workflow works with Azure ML!

```python
# Connect to Azure ML
from azure.ai.ml import MLClient
ml_client = MLClient(...)

# Get MLflow tracking URI
tracking_uri = ml_client.workspaces.get("workspace-name").mlflow_tracking_uri
mlflow.set_tracking_uri(tracking_uri)

# Everything else is identical!
# Models appear in both MLflow Registry and Azure ML Models
```

## Next Steps

After mastering this example:

1. **Production Deployment:** See `../production-deployment/` for deploying registered models
2. **Full Project:** See `../../housing-price-azure-deployment/` for end-to-end example
3. **Try with Azure ML:** Replace tracking URI with Azure ML workspace

## Interview Cheat Sheet

**Quick reference:**

```python
from mlflow.tracking import MlflowClient
client = MlflowClient()

# Register model
mlflow.register_model("runs:/RUN_ID/model", "MyModel")

# Set alias
client.set_registered_model_alias("MyModel", "champion", "3")

# Load by alias (production pattern)
model = mlflow.pyfunc.load_model("models:/MyModel@champion")

# Get version info
mv = client.get_model_version("MyModel", "3")
print(mv.run_id, mv.creation_timestamp)

# List all versions
versions = client.search_model_versions("name='MyModel'")

# Compare versions
run1 = mlflow.get_run(version1.run_id)
run2 = mlflow.get_run(version2.run_id)
rmse1 = run1.data.metrics["rmse"]
rmse2 = run2.data.metrics["rmse"]
```

**Key concepts:**
- Models are versioned automatically (immutable)
- Use aliases (@champion, @challenger, @staging) for lifecycle
- Load by alias in production (never hardcode versions)
- Registry links to original runs (full lineage)
- Champion/challenger pattern for safe deployments

Good luck with your interview! 🚀
