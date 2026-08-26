# Azure ML Fundamentals - Complete Beginner's Guide

## Table of Contents
1. [Azure Basics (Complete Beginner)](#azure-basics-complete-beginner)
2. [Azure ML Architecture](#azure-ml-architecture)
3. [Core Azure ML Components](#core-azure-ml-components)
4. [Azure ML Compute Options](#azure-ml-compute-options)
5. [Data Management in Azure ML](#data-management-in-azure-ml)
6. [Setting Up Your First Azure ML Workspace](#setting-up-your-first-azure-ml-workspace)
7. [Interview Questions & Answers](#interview-questions--answers)

---

## Azure Basics (Complete Beginner)

### What is Azure?

**Microsoft Azure** is a cloud computing platform—think of it as **"renting computers, storage, and services from Microsoft"** instead of buying your own servers.

### Why Cloud? Why Azure?

| Without Cloud | With Azure |
|---------------|------------|
| Buy expensive servers | Rent only what you need |
| Maintain hardware | Microsoft handles hardware |
| Limited to office location | Access from anywhere |
| Pay upfront | Pay as you go |
| Scale manually | Auto-scale instantly |

**Azure for ML:** Powerful GPUs for training, unlimited storage for data, managed services so you focus on models, not infrastructure.

---

### Azure Hierarchy (Top to Bottom)

```
[Your Organization]
    ↓
[Azure Account] ← Your login (email)
    ↓
[Subscription] ← Billing boundary (like a credit card)
    ↓
[Resource Group] ← Logical container (like a project folder)
    ↓
[Resources] ← Actual services (VMs, storage, databases)
```

**Simple Analogy:**
- **Account**: Your Microsoft identity
- **Subscription**: Your payment method/budget
- **Resource Group**: A project folder
- **Resources**: Individual tools/services in that project

---

### Key Azure Concepts

#### 1. Subscription

**What:** A billing and access boundary.

**Why:** Separates costs by department, project, or environment (dev vs prod).

**Example:**
```
Company XYZ has 3 subscriptions:
├── Dev/Test Subscription ($500/month budget)
├── Production Subscription ($5000/month budget)
└── Research Subscription ($1000/month budget)
```

#### 2. Resource Group

**What:** A container for related Azure resources.

**Why:** Group everything for one project so you can manage, monitor, or delete them together.

**Example:**
```
Resource Group: "ml-housing-price-prod"
├── Azure ML Workspace
├── Storage Account (for data)
├── Key Vault (for secrets)
├── Container Registry (for Docker images)
└── Application Insights (for monitoring)
```

**Interview Tip:** When you delete a resource group, ALL resources inside are deleted—be careful!

#### 3. Region

**What:** Physical location of Azure data centers (e.g., "East US", "West Europe").

**Why:** Affects latency, compliance (data residency laws), and pricing.

**Best Practice:** Keep related resources in the same region (faster, cheaper).

**Common Regions:**
- **US:** East US, West US, Central US
- **Europe:** North Europe, West Europe
- **Asia:** Southeast Asia, East Asia

---

## Azure ML Architecture

### The Full Picture

```
Azure Subscription
 └── Resource Group (rg-mlops-prod)
      ├── Azure ML Workspace (mlw-prod) ← YOUR CONTROL CENTER
      │    ├── Experiments (MLflow tracking)
      │    ├── Models (registry)
      │    ├── Compute (training clusters)
      │    ├── Data Assets (versioned datasets)
      │    ├── Environments (Docker images)
      │    ├── Pipelines (orchestration)
      │    └── Endpoints (deployed models)
      │
      ├── Storage Account (blob, file storage)
      │    ├── Blobs (unstructured data: CSVs, images)
      │    ├── File Shares (shared filesystem)
      │    └── Tables/Queues (less common for ML)
      │
      ├── Key Vault (secrets management)
      │    ├── Connection strings
      │    ├── API keys
      │    └── Certificates
      │
      ├── Container Registry (ACR)
      │    └── Docker images for training/serving
      │
      └── Application Insights (monitoring)
           ├── Logs
           ├── Metrics
           └── Traces
```

---

### Azure ML Workspace: Your ML Hub

Think of the **workspace** as your **ML command center**. Everything ML-related lives here.

**What it Provides:**
- ✅ MLflow tracking built-in
- ✅ Model registry
- ✅ Compute management (spin up/down GPUs)
- ✅ Dataset versioning
- ✅ Pipeline orchestration
- ✅ Model deployment (endpoints)
- ✅ Team collaboration

**Interview Answer:**
> "An Azure ML Workspace is a centralized environment for the entire ML lifecycle. It provides experiment tracking via built-in MLflow, compute for training, a model registry, dataset versioning, pipeline orchestration, and deployment endpoints. It's the hub where data scientists collaborate, and it automatically creates associated resources like storage, key vault, and container registry."

---

### Auto-Created Resources

When you create an Azure ML Workspace, **4 resources are automatically created**:

| Resource | Purpose | ML Use Case |
|----------|---------|-------------|
| **Storage Account** | Blobs, file shares | Store training data, model artifacts, logs |
| **Key Vault** | Secrets, keys, certs | Store database passwords, API keys |
| **Container Registry** | Docker images | Custom training environments, serving images |
| **Application Insights** | Telemetry, logs | Monitor endpoint latency, model performance |

**Important:** These are created in the **same resource group** as the workspace.

---

## Core Azure ML Components

### 1. Compute

**Purpose:** Where your code actually runs.

**Types:**

#### Compute Instance (Development)
- **What:** Single-user VM with Jupyter, VS Code, terminal
- **Use Case:** Interactive development, experimentation
- **Cost:** Pay per hour while running
- **Sizes:** `Standard_DS3_v2` (4 cores, 14 GB), `Standard_DS11_v2` (2 cores, 14 GB)

```python
# Create via Python SDK
from azure.ai.ml.entities import ComputeInstance

compute = ComputeInstance(
    name="my-dev-instance",
    size="STANDARD_DS3_V2",
    idle_time_before_shutdown_minutes=30  # Auto-shutdown to save $$$
)
ml_client.compute.begin_create_or_update(compute)
```

#### Compute Cluster (Training)
- **What:** Multi-node, auto-scaling cluster
- **Use Case:** Production training jobs, parallel experiments
- **Cost:** Pay per node-hour (can scale to zero!)
- **Key Benefit:** Runs 10 experiments in parallel on 10 nodes, then scales to 0

```python
from azure.ai.ml.entities import AmlCompute

compute = AmlCompute(
    name="training-cluster",
    type="amlcompute",
    size="STANDARD_DS11_V2",
    min_instances=0,  # Scale to zero when idle
    max_instances=4,  # Max parallelism
    idle_time_before_scale_down=300  # 5 min idle → scale down
)
ml_client.compute.begin_create_or_update(compute)
```

---

### 2. Data Assets

**Purpose:** Versioned, named references to data.

**Why:** Instead of hardcoding paths like `/data/train.csv`, reference `diabetes-training:v2`.

**Types:**
- **URI File**: Single file (e.g., `housing.csv`)
- **URI Folder**: Directory of files
- **MLTable**: Tabular data with schema (like a database table)

```python
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

data_asset = Data(
    name="housing-training-data",
    version="1",
    description="Housing price training dataset",
    type=AssetTypes.URI_FILE,
    path="azureml://datastores/workspaceblobstore/paths/data/housing.csv"
)
ml_client.data.create_or_update(data_asset)
```

**Benefits:**
- ✅ Versioning (v1, v2, v3...)
- ✅ Lineage (which models used which data)
- ✅ Discoverability (browse in UI)

---

### 3. Environments

**Purpose:** Docker images + Python packages for reproducible training.

**Why:** "Works on my machine" → "Works everywhere"

**Types:**
- **Curated Environments**: Pre-built by Microsoft (e.g., `AzureML-sklearn-1.0-ubuntu20.04-py38-cpu`)
- **Custom Environments**: Your own Dockerfile or conda spec

```python
from azure.ai.ml.entities import Environment

env = Environment(
    name="mlflow-sklearn-env",
    description="MLflow + sklearn environment",
    conda_file="conda.yaml",  # Your conda environment
    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04"  # Base image
)
ml_client.environments.create_or_update(env)
```

---

### 4. Experiments & Runs

**Azure ML has built-in MLflow!**

```python
import mlflow

# Azure ML auto-configures MLflow tracking URI
# No need to manually set_tracking_uri!

mlflow.set_experiment("housing-price-prediction")

with mlflow.start_run():
    mlflow.log_param("alpha", 0.5)
    mlflow.log_metric("rmse", 0.75)
    mlflow.sklearn.log_model(model, "model")
```

**Behind the Scenes:**
- Metadata → Workspace's backend database
- Artifacts → Workspace's storage account

---

### 5. Model Registry

**Azure ML Model Registry = MLflow Registry**

```python
# Register via MLflow (same as before!)
mlflow.sklearn.log_model(
    model,
    "model",
    registered_model_name="HousingPriceModel"
)

# Or via Azure ML SDK
from azure.ai.ml.entities import Model

model = Model(
    name="HousingPriceModel",
    version="1",
    path="azureml://jobs/abc123/outputs/artifacts/paths/model/",
    type="mlflow_model"
)
ml_client.models.create_or_update(model)
```

---

### 6. Endpoints (Deployment)

**Two Types:**

#### Online Endpoints (Real-Time)
- **Use Case:** Low-latency predictions (< 1 second)
- **Example:** Fraud detection API, recommendation API
- **Managed:** Auto-scaling, load balancing, monitoring

#### Batch Endpoints (High-Volume)
- **Use Case:** Process millions of records (minutes/hours OK)
- **Example:** Nightly scoring of all customers
- **Managed:** Parallel processing, automatic retries

```python
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment

# Create endpoint
endpoint = ManagedOnlineEndpoint(
    name="housing-price-endpoint",
    description="Housing price prediction API",
    auth_mode="key"  # or "aml_token" for Azure AD
)
ml_client.online_endpoints.begin_create_or_update(endpoint)

# Deploy model to endpoint
deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name="housing-price-endpoint",
    model="azureml:HousingPriceModel:1",
    environment="mlflow-sklearn-env:1",
    instance_type="Standard_DS3_v2",
    instance_count=1
)
ml_client.online_deployments.begin_create_or_update(deployment)

# Send traffic to deployment
endpoint.traffic = {"blue": 100}  # 100% to "blue" deployment
ml_client.online_endpoints.begin_create_or_update(endpoint)
```

---

## Azure ML Compute Options

### Choosing the Right Compute

| Scenario | Recommended Compute | Why |
|----------|---------------------|-----|
| Experimenting in Jupyter | Compute Instance | Interactive, Jupyter built-in |
| Training single model | Compute Cluster (min=0, max=1) | Auto-shutdown saves money |
| Hyperparameter tuning (100 runs) | Compute Cluster (min=0, max=10) | Parallel execution |
| Production pipelines | Compute Cluster | Reliable, scales on demand |
| Deep learning (GPUs) | GPU Compute Cluster | `Standard_NC6` or higher |

---

### Common Instance Sizes

| Size | vCPUs | RAM | Cost/Hour | Use Case |
|------|-------|-----|-----------|----------|
| `Standard_DS2_v2` | 2 | 7 GB | ~$0.14 | Light dev work |
| `Standard_DS3_v2` | 4 | 14 GB | ~$0.28 | Standard dev |
| `Standard_DS11_v2` | 2 | 14 GB | ~$0.19 | Memory-heavy |
| `Standard_NC6` | 6 | 56 GB + GPU | ~$0.90 | Deep learning |

**Cost Tip:** Always set `idle_time_before_shutdown` and `min_instances=0` to avoid paying for idle compute!

---

## Data Management in Azure ML

### Storage Account Deep Dive

Every Azure ML workspace gets a **default storage account** with:

1. **Blob Storage**: Object storage for any file type
   - CSVs, images, videos, models
   - Path: `https://<account>.blob.core.windows.net/<container>/<path>`

2. **File Shares**: Shared filesystem (like NFS)
   - Good for code that expects a traditional file path
   - Path: `\\<account>.file.core.windows.net\<share>\<path>`

3. **Datastores**: Azure ML abstraction over storage accounts

```python
# Get default datastore
datastore = ml_client.datastores.get_default()

# Upload file
datastore.upload(
    src_dir="./data",
    target_path="housing-data",
    overwrite=True
)
```

---

### Best Practices for Data

1. **Version your data** using Data Assets, not manual file copies
2. **Use datastores** instead of hardcoding storage paths
3. **Keep data close to compute** (same region) for speed
4. **Use appropriate storage tier**:
   - Hot: Frequently accessed
   - Cool: Accessed monthly (cheaper)
   - Archive: Rarely accessed (cheapest, retrieval fee)

---

## Setting Up Your First Azure ML Workspace

### Prerequisites

1. **Azure Account**: Sign up at https://azure.microsoft.com/free (includes $200 credit)
2. **Azure CLI**: Install from https://aka.ms/InstallAzureCLI
3. **Azure ML CLI Extension**: `az extension add -n ml`
4. **Python**: 3.8+

---

### Step-by-Step Setup

#### 1. Login to Azure

```bash
az login
# Opens browser for authentication
```

#### 2. Set Active Subscription

```bash
# List subscriptions
az account list --output table

# Set active subscription
az account set --subscription "Your Subscription Name"
```

#### 3. Create Resource Group

```bash
az group create \
  --name rg-mlops-demo \
  --location eastus
```

#### 4. Create Azure ML Workspace

```bash
az ml workspace create \
  --name mlw-demo \
  --resource-group rg-mlops-demo \
  --location eastus
```

**What Happened:**
- ✅ Workspace created
- ✅ Storage account auto-created
- ✅ Key Vault auto-created
- ✅ Container Registry auto-created
- ✅ Application Insights auto-created

#### 5. Create Compute Cluster

```bash
az ml compute create \
  --name training-cluster \
  --type amlcompute \
  --resource-group rg-mlops-demo \
  --workspace-name mlw-demo \
  --size Standard_DS3_v2 \
  --min-instances 0 \
  --max-instances 4 \
  --idle-time-before-scale-down 300
```

#### 6. Create Compute Instance (Optional)

```bash
az ml compute create \
  --name my-dev-vm \
  --type computeinstance \
  --resource-group rg-mlops-demo \
  --workspace-name mlw-demo \
  --size Standard_DS3_v2
```

#### 7. Verify Setup

```bash
# List compute
az ml compute list \
  --resource-group rg-mlops-demo \
  --workspace-name mlw-demo \
  --output table
```

---

### Python SDK Setup

```bash
pip install azure-ai-ml azure-identity mlflow
```

```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

# Connect to workspace
ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id="YOUR_SUBSCRIPTION_ID",
    resource_group_name="rg-mlops-demo",
    workspace_name="mlw-demo"
)

# Verify connection
workspace = ml_client.workspaces.get(name="mlw-demo")
print(f"Connected to workspace: {workspace.name}")
```

---

## Interview Questions & Answers

### Q1: "What is Azure ML and why would you use it?"

**Answer:**
> "Azure ML is a managed cloud service for the full ML lifecycle. It provides experiment tracking via built-in MLflow, scalable compute that can spin up for training and scale to zero to save costs, a model registry for versioning, and managed endpoints for deployment. I'd use it instead of self-managing infrastructure because it handles the heavy lifting—auto-scaling, monitoring, security—letting me focus on models instead of DevOps. It's especially valuable for teams because it provides centralized collaboration and governance."

---

### Q2: "Explain the Azure ML workspace hierarchy."

**Answer:**
> "At the top is your Azure subscription, which is your billing boundary. Within a subscription, you create resource groups, which are logical containers for related resources. Inside a resource group, you create an Azure ML workspace, which is the hub for all ML work. The workspace contains experiments, models, compute, data assets, environments, and endpoints. When you create a workspace, Azure automatically provisions four supporting resources in the same resource group: a storage account for data and artifacts, Key Vault for secrets, Container Registry for Docker images, and Application Insights for monitoring."

---

### Q3: "What's the difference between a Compute Instance and a Compute Cluster?"

**Answer:**
> "A Compute Instance is a single-user VM designed for interactive development—it has Jupyter, VS Code, and a terminal built-in. You start and stop it manually and pay while it's running. A Compute Cluster is multi-node and designed for scalable training jobs. It can auto-scale from 0 to N nodes based on workload—so if you submit 10 jobs, it spins up 10 nodes in parallel, then scales back to zero when idle. For cost efficiency, I always set min_instances to 0 on clusters and enable auto-shutdown on instances."

---

### Q4: "How does data versioning work in Azure ML?"

**Answer:**
> "Azure ML has Data Assets, which are named, versioned references to data. Instead of hardcoding a path like `/storage/train.csv`, you register the data as an asset with a name like `housing-training` and version `1`. When you update the data, you create version `2`. This provides lineage—you can trace which model was trained on which exact data version. It also enables discoverability via the UI and makes pipelines more robust because they reference stable asset names instead of fragile file paths that might move or change."

---

### Q5: "Walk through deploying a model to an Azure ML endpoint."

**Answer:**
> "First, I train and register the model in the model registry via MLflow. Then I create a managed online endpoint, which is a stable URL that can host multiple deployments. I create a deployment specifying the model version, environment (Docker image), instance type, and instance count. Azure ML handles provisioning the infrastructure, loading the model, and exposing a REST API. I test the deployment with sample requests, then route traffic to it. For zero-downtime updates, I use blue-green deployment: create a new green deployment, test it, gradually shift traffic from blue to green, then delete blue."

---

### Q6: "How would you handle secrets like database passwords in Azure ML?"

**Answer:**
> "Azure ML workspaces come with an auto-created Key Vault. I'd store secrets there and reference them in code via the Azure SDK. For example, in a training script, I'd use `DefaultAzureCredential` to authenticate, retrieve the secret from Key Vault, and use it. I'd never hardcode secrets in code or config files, and I'd never commit them to git. For connections to external systems like databases, Azure ML has a Connections feature that securely stores credentials. The key principle is: secrets live in Key Vault, code references them at runtime."

---

### Q7: "What happens when you delete a resource group?"

**Answer:**
> "When you delete a resource group, ALL resources inside it are permanently deleted—the workspace, storage accounts, compute, models, everything. There's no undo. This is why resource groups should be organized by lifecycle: group resources that should be deleted together. Before deletion, I'd always verify I'm targeting the right resource group, especially in production. For critical resources, I'd enable locks in Azure to prevent accidental deletion."

---

### Q8: "How does Azure ML integrate with MLflow?"

**Answer:**
> "Azure ML has built-in MLflow support. When you run code in an Azure ML job or compute instance, it automatically sets the MLflow tracking URI to point to the workspace. This means any `mlflow.log_param` or `mlflow.log_model` calls are captured in the workspace's experiments. The Azure ML model registry is actually backed by MLflow, so you can use standard MLflow APIs like `mlflow.pyfunc.load_model` to load registered models. The integration is seamless—code written for local MLflow runs unchanged in Azure ML."

---

### Q9: "What cost optimization strategies would you use in Azure ML?"

**Answer:**
> "First, always set compute clusters to min_instances=0 so they scale to zero when idle. Second, enable auto-shutdown on compute instances with a short idle timeout like 30 minutes. Third, choose the right instance size—don't use a GPU when a CPU suffices. Fourth, use spot instances for non-critical training to save up to 90%. Fifth, clean up old models and datasets to reduce storage costs. Sixth, use the cost management dashboard to monitor spending and set budget alerts. Finally, for development, I'd use a dev subscription with spending limits to prevent runaway costs."

---

### Q10: "How would you set up Azure ML for a team?"

**Answer:**
> "I'd create a shared Azure ML workspace with role-based access control. Data scientists get Contributor role to run experiments and register models, while only ML engineers get Owner role to create compute. I'd establish naming conventions for experiments, models, and environments. I'd create shared curated environments for common frameworks to avoid duplication. I'd set up a centralized compute cluster with auto-scaling, and each data scientist gets their own compute instance for development. For data, I'd use datastores with shared access. I'd also enable workspace monitoring to track usage and costs."

---

## Summary: Key Takeaways

✅ **Azure Hierarchy**: Account → Subscription → Resource Group → Resources

✅ **Workspace = ML Hub**: Experiments, models, compute, data, endpoints all in one place

✅ **Auto-Created Resources**: Storage, Key Vault, Container Registry, App Insights

✅ **Compute Types**:
- Instance = dev (interactive)
- Cluster = training (auto-scale)

✅ **Data Assets** = versioned, named data references

✅ **Built-in MLflow**: No extra setup, just works

✅ **Endpoints**: Online (real-time) vs Batch (high-volume)

✅ **Cost Optimization**: Scale to zero, auto-shutdown, right-size instances

---

**Time to Complete:** 3-4 hours
**Next:** Study Guide 03 - MLflow + Azure Integration
**Hands-On:** Code Example - Azure ML Integration
