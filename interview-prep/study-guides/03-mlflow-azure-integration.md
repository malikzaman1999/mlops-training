# MLflow + Azure ML Integration - Study Guide

## Table of Contents
1. [Integration Overview](#integration-overview)
2. [Azure ML's Built-in MLflow](#azure-mls-built-in-mlflow)
3. [Custom MLflow Server on Azure](#custom-mlflow-server-on-azure)
4. [Storage Architecture](#storage-architecture)
5. [Training Jobs on Azure ML with MLflow](#training-jobs-on-azure-ml-with-mlflow)
6. [Model Deployment Workflows](#model-deployment-workflows)
7. [Interview Questions & Answers](#interview-questions--answers)

---

## Integration Overview

### Two Approaches to MLflow on Azure

| Approach | When to Use | Pros | Cons |
|----------|-------------|------|------|
| **Azure ML Built-in** | Most teams | Fully managed, zero setup, integrated auth | Less customization |
| **Custom MLflow Server** | Advanced teams | Full control, custom backends | You manage infrastructure |

**Recommendation for Interviews:** Know both, emphasize built-in approach.

---

## Azure ML's Built-in MLflow

### The Seamless Integration

**Key Insight:** Azure ML Workspaces **are** MLflow tracking servers.

```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import mlflow

# Connect to Azure ML Workspace
ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="YOUR_SUBSCRIPTION_ID",
    resource_group_name="rg-mlops",
    workspace_name="mlw-prod"
)

# Get MLflow tracking URI (auto-configured!)
tracking_uri = ml_client.workspaces.get(name="mlw-prod").mlflow_tracking_uri
mlflow.set_tracking_uri(tracking_uri)

# Now use MLflow normally—it's integrated!
mlflow.set_experiment("housing-price")

with mlflow.start_run():
    mlflow.log_param("alpha", 0.5)
    mlflow.log_metric("rmse", 0.75)
    mlflow.sklearn.log_model(model, "model", registered_model_name="HousingModel")
```

---

### What Happens Behind the Scenes

```
Your MLflow Code
    ↓
Azure ML MLflow Endpoint
    ↓
├─→ Metadata (params, metrics, tags)
│   └─→ Workspace's SQL Database
│
└─→ Artifacts (models, plots, data)
    └─→ Workspace's Storage Account (Blob)
```

**Interview Answer:**
> "Azure ML workspaces expose an MLflow-compatible API. When I call `mlflow.log_param`, it's sent via HTTPS to the workspace's MLflow endpoint. Metadata is stored in the workspace's backend database, and artifacts go to the default storage account. I don't need to deploy or manage any MLflow infrastructure—it's provided as part of the workspace."

---

### Authentication

```python
# Option 1: Interactive (local development)
from azure.identity import InteractiveBrowserCredential

credential = InteractiveBrowserCredential()
ml_client = MLClient(credential, subscription_id, resource_group, workspace_name)

# Option 2: Service Principal (CI/CD pipelines)
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id="YOUR_TENANT_ID",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
ml_client = MLClient(credential, subscription_id, resource_group, workspace_name)

# Option 3: Default (tries multiple methods)
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()  # CLI → managed identity → env vars
ml_client = MLClient(credential, subscription_id, resource_group, workspace_name)
```

**Best Practice:** Use `DefaultAzureCredential` for flexibility.

---

### MLflow UI in Azure ML

**Access the UI:**
1. Navigate to Azure ML Studio: https://ml.azure.com
2. Select your workspace
3. Click "Experiments" in left nav
4. Click any experiment → See all runs with full MLflow UI

**What You Get:**
- ✅ Compare runs side-by-side
- ✅ Visualize metrics over time
- ✅ Download artifacts
- ✅ Register models
- ✅ Track lineage

**Interview Tip:** Azure ML Studio **is** the MLflow UI, just with extra Azure features.

---

## Custom MLflow Server on Azure

### When to Use

- Need a non-Azure MLflow setup (e.g., multi-cloud)
- Want full control over backend/artifact stores
- Existing MLflow server to migrate

---

### Architecture: MLflow Server on Azure VM

```
Azure VM (Ubuntu)
├── MLflow Server Process
│   └── Listening on port 5000
│
├── Backend Store
│   └── Azure SQL Database (metadata)
│
└── Artifact Store
    └── Azure Blob Storage (artifacts)
```

---

### Setup Steps

#### 1. Create Azure Resources

```bash
# Resource group
az group create --name rg-mlflow --location eastus

# Azure SQL Database
az sql server create \
  --name mlflowsqlserver \
  --resource-group rg-mlflow \
  --location eastus \
  --admin-user mlfladmin \
  --admin-password "StrongPass123!"

az sql db create \
  --resource-group rg-mlflow \
  --server mlflowsqlserver \
  --name mlflowdb \
  --service-objective S0  # Standard tier

# Storage Account
az storage account create \
  --name mlflowstorage \
  --resource-group rg-mlflow \
  --location eastus \
  --sku Standard_LRS

# Container for artifacts
az storage container create \
  --name mlflow-artifacts \
  --account-name mlflowstorage

# VM for MLflow server
az vm create \
  --resource-group rg-mlflow \
  --name mlflow-server-vm \
  --image UbuntuLTS \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys

# Open port 5000
az vm open-port \
  --resource-group rg-mlflow \
  --name mlflow-server-vm \
  --port 5000
```

#### 2. Install MLflow on VM

```bash
# SSH into VM
ssh azureuser@<VM_PUBLIC_IP>

# Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv

# Create virtual environment
python3 -m venv mlflow-env
source mlflow-env/bin/activate

# Install MLflow + Azure SDK
pip install mlflow azure-storage-blob azure-identity psycopg2-binary
```

#### 3. Start MLflow Server

```bash
export AZURE_STORAGE_CONNECTION_STRING="<YOUR_STORAGE_CONNECTION_STRING>"

mlflow server \
  --backend-store-uri "postgresql://mlfladmin:StrongPass123!@mlflowsqlserver.database.windows.net:5432/mlflowdb?sslmode=require" \
  --default-artifact-root "wasbs://mlflow-artifacts@mlflowstorage.blob.core.windows.net/" \
  --host 0.0.0.0 \
  --port 5000
```

#### 4. Connect from Client

```python
import mlflow

mlflow.set_tracking_uri("http://<VM_PUBLIC_IP>:5000")

mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    mlflow.log_param("test", "value")
```

---

### Cost Comparison

| Component | Built-in Azure ML | Custom Server |
|-----------|-------------------|---------------|
| **MLflow Server** | Free (part of workspace) | ~$40/month (VM) |
| **Database** | Included | ~$15/month (Azure SQL S0) |
| **Storage** | Workspace storage | ~$0.02/GB/month |
| **Total** | **Workspace cost only** | **~$55/month + storage** |

**Interview Insight:** Custom server adds complexity and cost. Only use if you need features Azure ML doesn't provide.

---

## Storage Architecture

### Azure Blob Storage as Artifact Store

**URI Formats:**

```python
# Blob storage URI
"wasbs://container@account.blob.core.windows.net/path/to/artifact"

# HTTPS URI (alternative)
"https://account.blob.core.windows.net/container/path/to/artifact"

# Azure ML datastore URI
"azureml://datastores/workspaceblobstore/paths/artifacts/model"
```

---

### Accessing Artifacts

```python
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

# Connect to blob storage
blob_service = BlobServiceClient(
    account_url="https://mlflowstorage.blob.core.windows.net",
    credential=DefaultAzureCredential()
)

# List artifacts
container_client = blob_service.get_container_client("mlflow-artifacts")
blobs = container_client.list_blobs()

for blob in blobs:
    print(blob.name)

# Download artifact
blob_client = container_client.get_blob_client("experiment_1/run_abc/model.pkl")
with open("model.pkl", "wb") as f:
    f.write(blob_client.download_blob().readall())
```

---

### Azure SQL Database as Backend Store

**Connection String:**

```
postgresql://username:password@server.database.windows.net:5432/database?sslmode=require
```

**What's Stored:**

- Experiment names and IDs
- Run IDs, names, statuses
- Parameters (key-value pairs)
- Metrics (key-value-timestamp-step)
- Tags
- Model registry metadata

**What's NOT Stored:** Large files (models, plots, datasets) → those go to blob storage.

---

## Training Jobs on Azure ML with MLflow

### Local Development → Azure ML Pattern

#### Local Script (train.py)

```python
import argparse
import mlflow
import mlflow.sklearn
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--alpha", type=float, default=0.5)
parser.add_argument("--l1_ratio", type=float, default=0.5)
parser.add_argument("--data", type=str, required=True)
args = parser.parse_args()

# Load data
data = pd.read_csv(args.data)
X = data.drop("target", axis=1)
y = data["target"]

# Start MLflow run (auto-connects to Azure ML workspace)
with mlflow.start_run():
    # Log parameters
    mlflow.log_param("alpha", args.alpha)
    mlflow.log_param("l1_ratio", args.l1_ratio)

    # Train model
    model = ElasticNet(alpha=args.alpha, l1_ratio=args.l1_ratio)
    model.fit(X, y)

    # Evaluate
    predictions = model.predict(X)
    rmse = mean_squared_error(y, predictions, squared=False)
    r2 = r2_score(y, predictions)

    # Log metrics
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)

    # Log model
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="ElasticNetModel"
    )

    print(f"Model trained: RMSE={rmse:.4f}, R2={r2:.4f}")
```

---

### Submit to Azure ML Compute

```python
from azure.ai.ml import command, Input
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

# Connect to workspace
ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="YOUR_SUBSCRIPTION_ID",
    resource_group_name="rg-mlops",
    workspace_name="mlw-prod"
)

# Define training job
job = command(
    code="./src",  # Local directory with train.py
    command="python train.py --alpha ${{inputs.alpha}} --l1_ratio ${{inputs.l1_ratio}} --data ${{inputs.data}}",
    inputs={
        "alpha": 0.5,
        "l1_ratio": 0.5,
        "data": Input(
            type="uri_file",
            path="azureml:housing-data:1"  # Data asset
        )
    },
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="training-cluster",
    display_name="elasticnet-training",
    experiment_name="housing-price"
)

# Submit job
returned_job = ml_client.jobs.create_or_update(job)
print(f"Job submitted: {returned_job.name}")

# Stream logs (optional)
ml_client.jobs.stream(returned_job.name)
```

---

### Hyperparameter Sweep on Azure ML

```python
from azure.ai.ml.sweep import Choice

# Define sweep job
sweep_job = command(
    code="./src",
    command="python train.py --alpha ${{inputs.alpha}} --l1_ratio ${{inputs.l1_ratio}} --data ${{inputs.data}}",
    inputs={
        "alpha": Choice([0.1, 0.5, 1.0]),  # Sweep over alphas
        "l1_ratio": Choice([0.2, 0.5, 0.8]),  # Sweep over l1_ratios
        "data": Input(type="uri_file", path="azureml:housing-data:1")
    },
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="training-cluster",
    experiment_name="housing-price-sweep"
)

from azure.ai.ml.sweep import SweepJob

sweep = SweepJob(
    sampling_algorithm="grid",  # or "random", "bayesian"
    trial=sweep_job,
    objective={
        "goal": "minimize",
        "primary_metric": "rmse"
    },
    limits={"max_total_trials": 9}  # 3 alphas × 3 l1_ratios
)

returned_sweep = ml_client.jobs.create_or_update(sweep)
print(f"Sweep submitted: {returned_sweep.name}")
```

**Result:** 9 child runs created, all logged to MLflow, easily comparable in UI.

---

## Model Deployment Workflows

### Workflow 1: MLflow Model → Azure ML Endpoint

```python
# 1. Train and register model (already done via log_model)

# 2. Create online endpoint
from azure.ai.ml.entities import ManagedOnlineEndpoint

endpoint = ManagedOnlineEndpoint(
    name="housing-price-endpoint",
    description="Housing price prediction API",
    auth_mode="key"
)
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# 3. Deploy model
from azure.ai.ml.entities import ManagedOnlineDeployment, Model

deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name="housing-price-endpoint",
    model=Model(name="ElasticNetModel", version="1"),
    instance_type="Standard_DS2_v2",
    instance_count=1
)
ml_client.online_deployments.begin_create_or_update(deployment).result()

# 4. Assign traffic
endpoint.traffic = {"blue": 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# 5. Test endpoint
import requests
import json

scoring_uri = ml_client.online_endpoints.get(name="housing-price-endpoint").scoring_uri
api_key = ml_client.online_endpoints.get_keys(name="housing-price-endpoint").primary_key

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {"data": [[1.5, 2.0, 3.5]]}  # Sample input

response = requests.post(scoring_uri, json=data, headers=headers)
print(response.json())
```

---

### Workflow 2: Blue-Green Deployment

```python
# Green deployment (new model version)
green_deployment = ManagedOnlineDeployment(
    name="green",
    endpoint_name="housing-price-endpoint",
    model=Model(name="ElasticNetModel", version="2"),  # New version
    instance_type="Standard_DS2_v2",
    instance_count=1
)
ml_client.online_deployments.begin_create_or_update(green_deployment).result()

# Test green deployment (0% traffic)
# ... test with sample requests ...

# Gradually shift traffic
endpoint.traffic = {"blue": 80, "green": 20}  # 20% to new version
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Monitor green deployment
# ... check metrics in Application Insights ...

# Full cutover
endpoint.traffic = {"blue": 0, "green": 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Delete old deployment
ml_client.online_deployments.begin_delete(
    name="blue",
    endpoint_name="housing-price-endpoint"
).result()
```

---

## Interview Questions & Answers

### Q1: "How does Azure ML integrate with MLflow?"

**Answer:**
> "Azure ML workspaces expose an MLflow-compatible API endpoint. When I create a workspace, it comes with built-in MLflow tracking—no server deployment needed. I connect by getting the workspace's MLflow tracking URI and calling `mlflow.set_tracking_uri`. From there, standard MLflow code works unchanged: `mlflow.log_param`, `mlflow.log_model`, etc. Metadata is stored in the workspace's backend database, artifacts go to the workspace's default storage account, and the Azure ML model registry is actually backed by MLflow, so I can use `mlflow.pyfunc.load_model` with registry URIs."

---

### Q2: "When would you run a custom MLflow server on Azure instead of using Azure ML?"

**Answer:**
> "I'd use a custom MLflow server in three scenarios: first, if I need a multi-cloud setup where experiments from AWS and Azure are tracked centrally; second, if I have specific backend requirements like a custom database schema or a non-Azure artifact store; third, if I'm migrating an existing on-prem MLflow server to the cloud but can't immediately adopt Azure ML. However, for most teams, Azure ML's built-in MLflow is better—it's managed, secure, integrated with other Azure ML features, and costs less than running a VM plus database."

---

### Q3: "Walk through submitting a training job to Azure ML that logs to MLflow."

**Answer:**
> "First, I write a standard Python training script that uses MLflow—`mlflow.log_param`, `mlflow.log_metric`, `mlflow.log_model`. I don't set the tracking URI in the script; Azure ML auto-configures that. Then I use the Azure ML Python SDK to define a `command` job, specifying the code directory, the command to run, input data as a registered data asset, the environment, and the compute cluster. I submit the job with `ml_client.jobs.create_or_update`. Azure ML provisions a node, downloads the code and data, sets the MLflow tracking URI, runs the script, and logs everything to the workspace. I can monitor progress in Azure ML Studio, which shows the MLflow run details."

---

### Q4: "How do you handle authentication for MLflow in Azure ML?"

**Answer:**
> "For local development, I use `DefaultAzureCredential` from the Azure Identity SDK, which tries multiple auth methods—Azure CLI, environment variables, managed identity—and picks the first one that works. This lets me run `az login` locally, and the code authenticates automatically. For CI/CD pipelines, I use a Service Principal with client ID and secret stored in pipeline secrets. For training jobs running on Azure ML compute, I don't need to authenticate at all—the compute has a managed identity with automatic access to the workspace."

---

### Q5: "How would you implement blue-green deployment for a model?"

**Answer:**
> "In Azure ML, an endpoint can have multiple deployments, each with different models and traffic allocations. I'd deploy the new model version as a 'green' deployment alongside the existing 'blue' deployment, initially with 0% traffic. I'd test the green deployment directly using its URL. Once validated, I'd gradually shift traffic from blue to green—first 10%, then 25%, 50%, and so on—monitoring error rates and latency after each step. If any issues appear, I immediately shift traffic back to blue. Once green receives 100% traffic and proves stable, I delete the blue deployment. The key benefit is zero downtime and instant rollback capability."

---

### Q6: "What storage backends does Azure ML use for MLflow?"

**Answer:**
> "Azure ML uses a SQL database for the MLflow backend store, which holds experiment metadata, run parameters, metrics, tags, and model registry entries. For the artifact store, it uses the workspace's default Azure Blob Storage account. Artifacts are stored in blobs with URIs like `azureml://datastores/workspaceblobstore/paths/...`. This separation makes sense: metadata is small and query-heavy, so it goes to a database for fast searches; artifacts are large and write-heavy, so they go to cheap, scalable object storage."

---

### Q7: "How do you compare multiple training runs in Azure ML?"

**Answer:**
> "Azure ML Studio has a built-in comparison view. I navigate to the experiment, select multiple runs using checkboxes, and click 'Compare'. This shows side-by-side tables of parameters and metrics, plus visualizations like parallel coordinates plots and scatter plots. I can sort by any metric to find the best run. Programmatically, I use the MLflow search API: `mlflow.search_runs(experiment_ids=['...'], filter_string='metrics.rmse < 0.5', order_by=['metrics.rmse ASC'])`. This returns a pandas DataFrame of matching runs that I can analyze in code."

---

### Q8: "What's the difference between an Azure ML job and an MLflow run?"

**Answer:**
> "An Azure ML job is the infrastructure execution—it defines where code runs, what compute is used, what inputs are provided. An MLflow run is the logical record of one training execution—it logs parameters, metrics, and artifacts. They're linked: when I submit an Azure ML job that calls `mlflow.start_run`, Azure ML creates the job and MLflow creates the run. The job provides the execution environment; the run provides the experiment tracking. In the UI, I see both: the job shows compute logs and resource usage, while the run shows model metrics and parameters."

---

### Q9: "How would you set up a hyperparameter sweep that logs each trial to MLflow?"

**Answer:**
> "I'd use Azure ML's sweep capability. I define a base `command` job with parameter inputs marked as `Choice([...])` or `Uniform(min, max)` for numeric sweeps. Then I wrap it in a `SweepJob`, specifying the sampling algorithm—grid, random, or Bayesian—the optimization goal like 'minimize rmse', and max trials. Each trial runs as a separate child job, and if my training script calls `mlflow.start_run`, each creates an MLflow run under the same experiment. After the sweep completes, I can compare all child runs in the MLflow UI to find the best hyperparameters."

---

### Q10: "Explain how model registry works in the Azure ML + MLflow integration."

**Answer:**
> "The Azure ML model registry is backed by MLflow, so there's a unified registry. When I call `mlflow.sklearn.log_model` with `registered_model_name`, it registers in both Azure ML and MLflow. I can access models using MLflow URIs like `models:/ModelName/1` or Azure ML URIs like `azureml:ModelName:1`. The registry supports versioning, aliasing (like @champion), and metadata like descriptions and tags. For deployment, I can reference a model by name and version, and Azure ML resolves it from the registry—this decouples deployment code from specific model artifacts."

---

## Summary: Key Takeaways

✅ **Azure ML = Built-in MLflow**: No server setup required

✅ **Storage**: Metadata → SQL Database, Artifacts → Blob Storage

✅ **Authentication**: `DefaultAzureCredential` for most cases

✅ **Training Jobs**: Submit with Azure ML SDK, auto-logs to MLflow

✅ **Deployments**: MLflow models → Azure ML endpoints

✅ **Blue-Green**: Multiple deployments per endpoint with traffic splitting

✅ **Unified Registry**: MLflow and Azure ML share the same model registry

---

**Time to Complete:** 3-4 hours
**Next:** Study Guide 04 - Production Deployment Patterns
**Hands-On:** Code Example - Azure ML Integration
