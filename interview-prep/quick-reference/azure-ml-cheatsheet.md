# Azure ML Quick Reference Cheatsheet

**For last-minute interview review!**

---

## Azure Hierarchy

```
Subscription (billing)
  └── Resource Group (logical container)
       └── Azure ML Workspace (ML hub)
            ├── Auto-created: Storage, Key Vault, Container Registry, App Insights
            ├── Compute (instances & clusters)
            ├── Data Assets (versioned datasets)
            ├── Environments (Docker images)
            ├── Experiments (MLflow tracking)
            ├── Models (registry)
            └── Endpoints (deployment)
```

---

## Python SDK Setup

```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id="YOUR_SUBSCRIPTION_ID",
    resource_group_name="rg-mlops",
    workspace_name="mlw-prod"
)

# Get workspace
ws = ml_client.workspaces.get(name="mlw-prod")

# Get MLflow tracking URI
mlflow.set_tracking_uri(ws.mlflow_tracking_uri)
```

---

## CLI Commands

```bash
# Login
az login

# Set subscription
az account set --subscription "subscription-name"

# Create resource group
az group create --name rg-mlops --location eastus

# Create workspace
az ml workspace create \
  --name mlw-prod \
  --resource-group rg-mlops \
  --location eastus

# Create compute cluster
az ml compute create \
  --name training-cluster \
  --type amlcompute \
  --size Standard_DS3_v2 \
  --min-instances 0 \
  --max-instances 4
```

---

## Compute

### Compute Instance (Dev)

```python
from azure.ai.ml.entities import ComputeInstance

compute = ComputeInstance(
    name="my-dev-vm",
    size="STANDARD_DS3_V2",
    idle_time_before_shutdown_minutes=30  # Auto-shutdown
)
ml_client.compute.begin_create_or_update(compute)
```

### Compute Cluster (Training)

```python
from azure.ai.ml.entities import AmlCompute

compute = AmlCompute(
    name="training-cluster",
    size="STANDARD_DS3_V2",
    min_instances=0,  # Scale to zero!
    max_instances=4,
    idle_time_before_scale_down=300
)
ml_client.compute.begin_create_or_update(compute)
```

---

## Data Assets

```python
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

# Register data
data_asset = Data(
    name="housing-training",
    version="1",
    description="Housing price training data",
    type=AssetTypes.URI_FILE,
    path="azureml://datastores/workspaceblobstore/paths/data/housing.csv"
)
ml_client.data.create_or_update(data_asset)

# Use in job
job = command(
    inputs={"data": Input(type="uri_file", path="azureml:housing-training:1")}
)
```

---

## Environments

```python
from azure.ai.ml.entities import Environment

# Custom environment
env = Environment(
    name="sklearn-env",
    description="scikit-learn environment",
    conda_file="conda.yaml",
    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04"
)
ml_client.environments.create_or_update(env)

# Use curated environment
environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest"
```

---

## Training Jobs

```python
from azure.ai.ml import command, Input

job = command(
    code="./src",  # Local directory
    command="python train.py --alpha ${{inputs.alpha}} --data ${{inputs.data}}",
    inputs={
        "alpha": 0.5,
        "data": Input(type="uri_file", path="azureml:housing-data:1")
    },
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="training-cluster",
    display_name="elasticnet-training",
    experiment_name="housing-price"
)

# Submit job
returned_job = ml_client.jobs.create_or_update(job)

# Stream logs
ml_client.jobs.stream(returned_job.name)
```

---

## Hyperparameter Sweep

```python
from azure.ai.ml.sweep import Choice

sweep_job = command(
    code="./src",
    command="python train.py --alpha ${{inputs.alpha}}",
    inputs={"alpha": Choice([0.1, 0.5, 1.0])},  # Sweep this
    environment="sklearn-env:1",
    compute="training-cluster"
)

from azure.ai.ml.sweep import SweepJob

sweep = SweepJob(
    sampling_algorithm="grid",
    trial=sweep_job,
    objective={"goal": "minimize", "primary_metric": "rmse"},
    limits={"max_total_trials": 3}
)

ml_client.jobs.create_or_update(sweep)
```

---

## Model Deployment

### Online Endpoint (Real-Time)

```python
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, Model

# Create endpoint
endpoint = ManagedOnlineEndpoint(
    name="housing-endpoint",
    description="Housing price prediction",
    auth_mode="key"
)
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Deploy model
deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name="housing-endpoint",
    model=Model(name="HousingModel", version="1"),
    instance_type="Standard_DS2_v2",
    instance_count=2
)
ml_client.online_deployments.begin_create_or_update(deployment).result()

# Route traffic
endpoint.traffic = {"blue": 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()
```

### Test Endpoint

```python
import requests, json

scoring_uri = ml_client.online_endpoints.get(name="housing-endpoint").scoring_uri
api_key = ml_client.online_endpoints.get_keys(name="housing-endpoint").primary_key

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {"data": [[1.5, 2.0, 3.5]]}
response = requests.post(scoring_uri, json=data, headers=headers)
print(response.json())
```

---

## Blue-Green Deployment

```python
# Green deployment (new version)
green = ManagedOnlineDeployment(
    name="green",
    endpoint_name="housing-endpoint",
    model=Model(name="HousingModel", version="2"),  # New version
    instance_type="Standard_DS2_v2",
    instance_count=2
)
ml_client.online_deployments.begin_create_or_update(green).result()

# Test green
# ... invoke with deployment_name="green" ...

# Shift traffic gradually
endpoint.traffic = {"blue": 80, "green": 20}  # 20% canary
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Monitor, then full cutover
endpoint.traffic = {"blue": 0, "green": 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Delete old
ml_client.online_deployments.begin_delete(name="blue", endpoint_name="housing-endpoint")
```

---

## Batch Endpoint

```python
from azure.ai.ml.entities import BatchEndpoint, BatchDeployment

# Create batch endpoint
batch_endpoint = BatchEndpoint(
    name="churn-batch",
    description="Nightly churn scoring"
)
ml_client.batch_endpoints.begin_create_or_update(batch_endpoint).result()

# Deploy
batch_deployment = BatchDeployment(
    name="production",
    endpoint_name="churn-batch",
    model=Model(name="ChurnModel", version="1"),
    compute="batch-cluster",
    instance_count=10,
    mini_batch_size=100
)
ml_client.batch_deployments.begin_create_or_update(batch_deployment).result()

# Invoke
job = ml_client.batch_endpoints.invoke(
    endpoint_name="churn-batch",
    input=Input(type="uri_folder", path="azureml://datastores/blob/paths/customers/")
)
```

---

## Monitoring

### Application Insights Queries (KQL)

```kusto
// Endpoint latency
requests
| where name == "POST /predict"
| summarize p95=percentile(duration, 95) by bin(timestamp, 5m)

// Error rate
requests
| where name == "POST /predict"
| summarize ErrorRate = (countif(success == false) * 100.0) / count() by bin(timestamp, 5m)

// Prediction distribution
customEvents
| where name == "Prediction"
| extend value = todouble(customDimensions["prediction"])
| summarize avg(value), stdev(value) by bin(timestamp, 1h)
```

---

## Authentication

```python
# Interactive (local dev)
from azure.identity import InteractiveBrowserCredential
credential = InteractiveBrowserCredential()

# Service Principal (CI/CD)
from azure.identity import ClientSecretCredential
credential = ClientSecretCredential(
    tenant_id="TENANT_ID",
    client_id="CLIENT_ID",
    client_secret="SECRET"
)

# Default (tries multiple methods)
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
```

---

## MLflow Integration

```python
# Azure ML has built-in MLflow!
import mlflow

# Get tracking URI from workspace
tracking_uri = ml_client.workspaces.get(name="mlw-prod").mlflow_tracking_uri
mlflow.set_tracking_uri(tracking_uri)

# Now use MLflow normally
mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    mlflow.log_param("alpha", 0.5)
    mlflow.log_metric("rmse", 0.75)
    mlflow.sklearn.log_model(model, "model", registered_model_name="MyModel")
```

---

## Cost Optimization

✅ Set compute clusters to `min_instances=0`
✅ Enable auto-shutdown on compute instances (30 min idle)
✅ Right-size instances (don't over-provision)
✅ Use spot instances for training (up to 90% savings)
✅ Clean up old models and datasets
✅ Delete test resource groups when done
✅ Set budget alerts in Azure Cost Management

---

## Quick Interview Answers

**Q: What is Azure ML?**
> "A managed cloud service for the ML lifecycle. Provides scalable compute, built-in MLflow tracking, model registry, dataset versioning, pipeline orchestration, and managed endpoints."

**Q: Workspace hierarchy?**
> "Subscription → Resource Group → Workspace. Workspace auto-creates Storage, Key Vault, Container Registry, and App Insights."

**Q: Compute Instance vs Cluster?**
> "Instance = single-user dev VM with Jupyter. Cluster = multi-node auto-scaling for training jobs. Clusters can scale to zero to save costs."

**Q: How does Azure ML integrate with MLflow?**
> "Workspaces expose an MLflow-compatible API. Get the tracking URI from the workspace, set it in MLflow, and standard MLflow code works unchanged."

**Q: How to deploy a model?**
> "Create an online endpoint, deploy the model from the registry specifying instance type and count, route traffic, test via the scoring URI."

**Q: Authentication?**
> "Use `DefaultAzureCredential` locally (tries CLI, env vars, managed identity). Use Service Principal for CI/CD. Compute has managed identity automatically."

**Q: Data versioning?**
> "Register data as Data Assets with name and version. Reference by `azureml:dataset-name:version` instead of hardcoded paths. Provides lineage and reproducibility."

---

## Common Gotchas

❌ Forgetting to set `min_instances=0` → compute runs 24/7, high costs
❌ Hardcoding file paths instead of using Data Assets → breaks when paths change
❌ Not pinning environment versions → non-reproducible runs
❌ Deploying without auto-scaling → endpoint can't handle traffic spikes
❌ Skipping validation gates → bad models reach production

---

## Essential Commands

```bash
# List compute
az ml compute list -o table

# List jobs
az ml job list -o table

# List models
az ml model list -o table

# Get endpoint URL
az ml online-endpoint show -n housing-endpoint --query scoring_uri

# Stream job logs
az ml job stream -n JOB_NAME
```

---

**Last-Minute Review:**
- Azure ML = Workspace with auto-created Storage, Key Vault, ACR, App Insights
- Compute: Instance (dev), Cluster (training, auto-scale to 0)
- Built-in MLflow—just get tracking URI from workspace
- Deployment: Online (real-time) vs Batch (high-volume)
- Blue-green = zero-downtime with traffic splitting
- Always version data as Data Assets, not hardcoded paths

Good luck! 🚀
