# Azure ML + MLflow Integration Example

This example demonstrates how Azure ML integrates seamlessly with MLflow.

## What You'll Learn

✅ **Azure ML + MLflow Integration:**
- How to connect to Azure ML workspace
- How Azure ML provides built-in MLflow tracking
- Using standard MLflow code with Azure backend

✅ **Submitting Training Jobs:**
- Running training on Azure ML compute clusters
- Automatic MLflow logging in cloud jobs
- Monitoring job status and logs

✅ **Key Differences:**
- Local MLflow server vs Azure-managed MLflow
- When to use each approach
- Zero code changes when switching!

## Prerequisites

### 1. Azure Account
You need an Azure subscription. Options:
- **Free trial:** https://azure.microsoft.com/free/ ($200 credit)
- **Student:** https://azure.microsoft.com/free/students/ (no credit card)
- **Work account:** Use your organization's subscription

### 2. Azure CLI
Install Azure CLI:
```bash
# macOS
brew install azure-cli

# Windows
# Download from: https://aka.ms/installazurecliwindows

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

Verify installation:
```bash
az --version
```

### 3. Python Dependencies
```bash
cd interview-prep/code-examples/azure-ml-integration
pip install -r requirements.txt
```

## Setup

### Step 1: Authenticate with Azure

```bash
# Login to Azure
az login

# Set your subscription (if you have multiple)
az account list -o table
az account set --subscription "YOUR_SUBSCRIPTION_NAME"
```

### Step 2: Create Azure ML Workspace (if you don't have one)

```bash
# Create resource group
az group create --name rg-mlops-demo --location eastus

# Create Azure ML workspace
az ml workspace create \
  --name mlw-demo \
  --resource-group rg-mlops-demo \
  --location eastus
```

This creates:
- Azure ML Workspace
- Storage Account (for MLflow artifacts)
- Key Vault (for secrets)
- Container Registry (for Docker images)
- Application Insights (for monitoring)

**Interview tip:** Know what auto-creates with a workspace!

### Step 3: Set Environment Variables

```bash
# Linux/macOS
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="rg-mlops-demo"
export AZURE_WORKSPACE_NAME="mlw-demo"

# Windows PowerShell
$env:AZURE_SUBSCRIPTION_ID="your-subscription-id"
$env:AZURE_RESOURCE_GROUP="rg-mlops-demo"
$env:AZURE_WORKSPACE_NAME="mlw-demo"
```

To find your subscription ID:
```bash
az account show --query id -o tsv
```

## Running the Examples

### Example 1: Azure ML + MLflow Integration

Demonstrates how to use MLflow with Azure ML backend:

```bash
python azure_mlflow_demo.py
```

**What this does:**
1. Connects to Azure ML workspace
2. Gets MLflow tracking URI from workspace
3. Logs a run using standard MLflow code
4. Lists experiments and searches runs
5. Shows comparison: Local vs Azure MLflow

**Key Learning:**
```python
# Standard MLflow code
mlflow.set_tracking_uri(workspace.mlflow_tracking_uri)
mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    mlflow.log_param("alpha", 0.5)
    mlflow.log_metric("rmse", 0.75)
    # Data stored in Azure ML automatically!
```

**Interview Question:** "What's the difference between local MLflow and Azure ML MLflow?"
- **Storage:** Local uses SQLite/filesystem, Azure uses managed backend/blob storage
- **UI:** Local is http://localhost:5000, Azure is Azure ML Studio (cloud)
- **Collaboration:** Local requires sharing server, Azure has built-in RBAC
- **Code:** SAME! Just change the tracking URI

### Example 2: Submit Training Job (Optional)

**Note:** Requires compute cluster. Skip if not set up.

Create compute cluster first:
```bash
az ml compute create \
  --name training-cluster \
  --type amlcompute \
  --size Standard_DS3_v2 \
  --min-instances 0 \
  --max-instances 4 \
  --resource-group rg-mlops-demo \
  --workspace-name mlw-demo
```

Then submit job:
```bash
export AZURE_COMPUTE_NAME="training-cluster"
python submit_training_job.py
```

**What this does:**
1. Submits training code to Azure ML compute
2. Code runs on cloud VMs (not your laptop!)
3. MLflow tracking happens automatically
4. Results appear in Azure ML Studio

**Monitor the job:**
```bash
python submit_training_job.py --monitor JOB_NAME
```

**Stream logs:**
```bash
python submit_training_job.py --stream JOB_NAME
```

## Viewing Results

### Option 1: Azure ML Studio (Recommended)

1. Go to https://ml.azure.com
2. Select your workspace: `mlw-demo`
3. Navigate to **Experiments**
4. Click on `azure-mlflow-demo`
5. View runs, metrics, models

### Option 2: Local MLflow UI (Optional)

You can run MLflow UI locally pointing to Azure:

```bash
# This doesn't work directly—Azure ML doesn't expose MLflow UI port
# Instead, use Azure ML Studio
```

**Interview tip:** Azure ML Studio IS the MLflow UI for Azure!

## Understanding the Integration

### How Azure ML Provides MLflow

```
┌────────────────────────────────────────────────────────────┐
│ Your Code (Local or Cloud)                                 │
│                                                             │
│  import mlflow                                              │
│  mlflow.set_tracking_uri(workspace.mlflow_tracking_uri)    │
│  mlflow.log_param(...)                                      │
│  mlflow.log_metric(...)                                     │
│                                                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ MLflow API calls
                   │
                   ▼
┌────────────────────────────────────────────────────────────┐
│ Azure ML Workspace (Managed MLflow Server)                 │
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │ Backend Store    │      │ Artifact Store   │           │
│  │ (metadata)       │      │ (models, plots)  │           │
│  │                  │      │                  │           │
│  │ Azure ML Backend │      │ Azure Blob       │           │
│  │ Database         │      │ Storage          │           │
│  └──────────────────┘      └──────────────────┘           │
│                                                             │
└────────────────────────────────────────────────────────────┘
                   │
                   │
                   ▼
┌────────────────────────────────────────────────────────────┐
│ Azure ML Studio UI                                          │
│                                                             │
│  View experiments, runs, metrics, models                    │
│  Same data as MLflow UI, but cloud-based                    │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Key Integration Points

1. **Tracking URI:**
   - Local: `http://localhost:5000`
   - Azure: `azureml://...` (from workspace)

2. **Backend Store:**
   - Local: SQLite file or PostgreSQL
   - Azure: Azure ML managed database

3. **Artifact Store:**
   - Local: `./mlruns/` or S3
   - Azure: Azure Blob Storage (auto-configured)

4. **Authentication:**
   - Local: No auth (or basic auth)
   - Azure: Azure RBAC with DefaultAzureCredential

## Interview Practice

### Questions to Answer Out Loud

1. **How does Azure ML integrate with MLflow?**
   > "Azure ML provides a fully managed MLflow tracking server. You get the MLflow tracking URI from the workspace, set it in your code, and standard MLflow API calls work unchanged. Azure stores metadata in its backend and artifacts in Azure Blob Storage."

2. **Do I need to change my MLflow code to use Azure ML?**
   > "No! Just change the tracking URI from `http://localhost:5000` to the Azure workspace URI. All other code stays the same. This is the beauty of the integration."

3. **Where are MLflow artifacts stored in Azure ML?**
   > "In the Azure Storage Account that's auto-created with the workspace. You don't manage this directly—Azure ML handles it."

4. **How do I view MLflow runs in Azure?**
   > "Azure ML Studio serves as the MLflow UI. Navigate to Experiments in the Studio to see all your runs, metrics, and models."

5. **What's DefaultAzureCredential?**
   > "A class that tries multiple authentication methods in order: environment variables, managed identity, Azure CLI, then interactive browser. Perfect for code that runs both locally and in Azure."

### Hands-On Practice

1. **Modify the demo:**
   - Change experiment name
   - Log additional parameters
   - Add custom tags

2. **Search runs:**
   - Filter runs by metric value
   - Order by best performance
   - Export results to DataFrame

3. **Compare local vs Azure:**
   - Run the same code locally (change tracking URI)
   - Then run with Azure backend
   - Compare where data is stored

## Common Issues

### Issue 1: "DefaultAzureCredential failed"
**Cause:** Not logged into Azure CLI
**Solution:**
```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION"
```

### Issue 2: "Workspace not found"
**Cause:** Wrong subscription or workspace name
**Solution:**
```bash
# List all workspaces
az ml workspace list -o table

# Verify your subscription
az account show
```

### Issue 3: "Permission denied"
**Cause:** Insufficient permissions
**Solution:** You need at least "Contributor" role on the workspace
```bash
# Check your role
az role assignment list --assignee YOUR_EMAIL --resource-group rg-mlops-demo
```

### Issue 4: "ModuleNotFoundError: azure.ai.ml"
**Cause:** SDK not installed
**Solution:**
```bash
pip install -r requirements.txt
```

## No Azure Access? No Problem!

If you don't have Azure set up:

1. **Read the code:** Understand the concepts even without running
2. **Focus on `azure_mlflow_demo.py`:** It has detailed comments
3. **Study the comparison table:** Local vs Azure MLflow
4. **Practice explaining:** How the integration works

**For interviews, knowing HOW it works is more important than having run it!**

## Next Steps

After mastering this example:

1. **Model Registry:** See `../model-registry-workflow/` for registering and versioning models
2. **Production Deployment:** See `../production-deployment/` for deploying to Azure ML endpoints
3. **Full Project:** See `../../housing-price-azure-deployment/` for end-to-end example

## Interview Cheat Sheet

**Quick answers:**

```python
# Connect to workspace
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="...",
    resource_group_name="...",
    workspace_name="..."
)

# Get MLflow tracking URI
tracking_uri = ml_client.workspaces.get("workspace-name").mlflow_tracking_uri

# Use MLflow with Azure backend
import mlflow
mlflow.set_tracking_uri(tracking_uri)
mlflow.set_experiment("my-experiment")

# Everything else is standard MLflow!
with mlflow.start_run():
    mlflow.log_param("alpha", 0.5)
    mlflow.log_metric("rmse", 0.75)
    mlflow.sklearn.log_model(model, "model")
```

**Key facts:**
- Azure ML auto-creates: Storage, Key Vault, Container Registry, App Insights
- Tracking URI format: `azureml://...`
- Same MLflow API, different backend
- View results in Azure ML Studio
- Authentication via DefaultAzureCredential

Good luck with your interview! 🚀
