# Housing Price Prediction - Azure ML Deployment

A complete end-to-end MLOps project demonstrating:
- Training with MLflow tracking
- Model registration in Azure ML
- Deployment to Azure ML Online Endpoint
- Production monitoring and maintenance

This project shows everything you've learned in one cohesive example—perfect for discussing in interviews!

## Project Overview

**Business Problem:** Predict housing prices based on property features (size, location, amenities, etc.)

**ML Solution:**
- Model: ElasticNet regression
- Features: Square footage, bedrooms, bathrooms, location, year built, etc.
- Target: Sale price
- Metric: RMSE (Root Mean Squared Error)

**MLOps Implementation:**
- Tracking: MLflow with Azure ML backend
- Registry: Azure ML Model Registry with versioning
- Deployment: Azure ML Online Endpoint with blue-green pattern
- Monitoring: Application Insights for latency, errors, drift

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Development (Your Laptop)                                        │
│                                                                  │
│  1. Train model (train.py)                                       │
│     ├── Log experiments to MLflow                                │
│     ├── Track parameters, metrics, artifacts                     │
│     └── Save model with signature                                │
│                                                                  │
│  2. Register model (register.py)                                 │
│     ├── Register best model in Registry                          │
│     ├── Set alias: @champion, @challenger                        │
│     └── Add metadata and tags                                    │
│                                                                  │
│  3. Deploy model (deploy.py)                                     │
│     ├── Create Azure ML Online Endpoint                          │
│     ├── Deploy as "blue" deployment                              │
│     └── Route 100% traffic                                       │
│                                                                  │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   │ MLflow API calls
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│ Azure ML Workspace (Cloud)                                       │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ MLflow         │  │ Model Registry │  │ Online Endpoint  │  │
│  │ Tracking       │  │                │  │                  │  │
│  │                │  │ HousingModel:  │  │ housing-endpoint │  │
│  │ Experiments →  │  │  v1, v2, v3    │  │  ├── blue (v2)   │  │
│  │  - Run 1       │  │                │  │  └── green (v3)  │  │
│  │  - Run 2       │  │ @champion → v2 │  │                  │  │
│  │  - Run 3       │  │ @challenger→v3 │  │ Traffic:         │  │
│  │                │  │                │  │  blue: 80%       │  │
│  │                │  │                │  │  green: 20%      │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Storage        │  │ App Insights   │  │ Key Vault        │  │
│  │ (artifacts)    │  │ (monitoring)   │  │ (secrets)        │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                   │
                   │ HTTPS API calls
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│ Production Application                                           │
│                                                                  │
│  import requests                                                 │
│  response = requests.post(                                       │
│      scoring_uri,                                                │
│      headers={"Authorization": f"Bearer {api_key}"},             │
│      json={"data": [[2500, 3, 2, ...]]}                          │
│  )                                                               │
│  prediction = response.json()                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
housing-price-azure-deployment/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── data/
│   └── housing_data.csv       # Sample dataset
├── src/
│   ├── train.py              # Training script with MLflow
│   ├── register.py           # Model registration script
│   ├── deploy.py             # Deployment script
│   ├── predict.py            # Inference script
│   └── utils.py              # Shared utilities
├── notebooks/
│   └── exploratory_analysis.ipynb  # Data exploration (optional)
└── tests/
    └── test_model.py         # Model tests (optional)
```

## Setup

### Prerequisites

1. **Azure Subscription** (free tier works!)
2. **Azure CLI** installed
3. **Python 3.8+**

### Step 1: Azure ML Workspace

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-housing-mlops --location eastus

# Create Azure ML workspace
az ml workspace create \
  --name mlw-housing-prod \
  --resource-group rg-housing-mlops \
  --location eastus

# Create compute cluster (for training)
az ml compute create \
  --name training-cluster \
  --type amlcompute \
  --size Standard_DS3_v2 \
  --min-instances 0 \
  --max-instances 4 \
  --resource-group rg-housing-mlops \
  --workspace-name mlw-housing-prod
```

### Step 2: Environment Setup

```bash
# Clone or navigate to project
cd housing-price-azure-deployment

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your Azure details
nano .env
```

**.env file:**
```bash
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=rg-housing-mlops
AZURE_WORKSPACE_NAME=mlw-housing-prod
AZURE_COMPUTE_NAME=training-cluster
```

### Step 3: Verify Setup

```bash
# Test Azure connection
python -c "from src.utils import get_ml_client; client = get_ml_client(); print('✓ Connected to', client.workspace_name)"
```

## Workflow

### 1. Train Model

```bash
python src/train.py --alpha 0.5 --l1_ratio 0.5
```

**What this does:**
- Loads housing data
- Trains ElasticNet model
- Logs to MLflow (Azure ML backend)
- Saves model with signature
- Logs metrics: RMSE, MAE, R2

**Output:**
```
✓ Connected to Azure ML workspace: mlw-housing-prod
✓ Experiment: housing-price-prediction
✓ Training model...
  RMSE: 45231.23
  MAE: 32145.67
  R2: 0.8432
✓ Model logged to MLflow
  Run ID: abc123def456
```

**View in Azure ML Studio:**
1. Go to https://ml.azure.com
2. Navigate to "Experiments"
3. Click "housing-price-prediction"
4. See your run with metrics and model

### 2. Register Model

```bash
# Register the best model from latest run
python src/register.py --run-id abc123def456 --alias champion
```

**What this does:**
- Registers model in Azure ML Model Registry
- Versions automatically (v1, v2, v3, ...)
- Sets alias (@champion, @challenger)
- Adds metadata tags

**Output:**
```
✓ Model registered: HousingPriceModel
  Version: 3
  Alias: champion
  Run ID: abc123def456
```

**View in Azure ML Studio:**
1. Navigate to "Models"
2. Click "HousingPriceModel"
3. See versions with aliases

### 3. Deploy Model

```bash
# Deploy the champion model to production
python src/deploy.py --model-name HousingPriceModel --alias champion
```

**What this does:**
- Creates Azure ML Online Endpoint
- Deploys model as "blue" deployment
- Configures 2 instances of Standard_DS2_v2
- Routes 100% traffic to blue

**Output:**
```
✓ Endpoint created: housing-endpoint
  Scoring URI: https://housing-endpoint.eastus.inference.ml.azure.com/score
✓ Model deployed: blue (v3)
✓ Traffic: blue 100%
```

**This takes 5-10 minutes** (Azure is provisioning VMs)

### 4. Make Predictions

```bash
# Test the deployed model
python src/predict.py \
  --endpoint housing-endpoint \
  --data '[[2500, 3, 2, 1995, 1, 0, 1]]'
```

**What this does:**
- Gets endpoint credentials
- Sends prediction request
- Returns predicted price

**Output:**
```
✓ Prediction: $425,350
  Latency: 87ms
```

### 5. Update Model (Blue-Green)

When you train a better model:

```bash
# Train new model
python src/train.py --alpha 0.3 --l1_ratio 0.7

# Register as challenger
python src/register.py --run-id xyz789 --alias challenger

# Deploy as green (0% traffic initially)
python src/deploy.py \
  --model-name HousingPriceModel \
  --alias challenger \
  --deployment-name green \
  --traffic '{"blue": 100, "green": 0}'

# Test green deployment
python src/predict.py \
  --endpoint housing-endpoint \
  --deployment green

# If good, switch traffic
python src/deploy.py --set-traffic '{"blue": 0, "green": 100}'

# Update alias
python src/register.py --update-alias --version 4 --alias champion
```

## Interview Discussion Points

When discussing this project in interviews, highlight:

### 1. End-to-End MLOps
> "This project demonstrates the complete ML lifecycle. I train models with MLflow tracking, register versions in a model registry, deploy to production endpoints with blue-green deployment, and monitor in production with Application Insights."

### 2. Azure ML Integration
> "I used Azure ML because it provides managed MLflow infrastructure, so my team doesn't need to run servers. The MLflow API is standard, so code works locally or in Azure without changes—just swap the tracking URI."

### 3. Production Deployment Strategy
> "I implemented blue-green deployment for zero-downtime updates. The champion model serves production traffic. When I train a better model, I deploy it as green with 0% traffic, test it, then instantly cut over. If anything goes wrong, I can roll back immediately."

### 4. Reproducibility
> "Every model has full lineage—I can trace from production deployment back to the exact training run, hyperparameters, data version, and code commit. The model registry maintains immutable versions, so I can always roll back or reproduce results."

### 5. Monitoring
> "I monitor four layers: infrastructure (CPU, memory), input data (schema validation, drift detection), predictions (distribution, outliers), and business metrics (conversion rates). Application Insights tracks latency and errors with alerts for anomalies."

### 6. Challenges Solved
> "One challenge was training-serving skew—my model worked in notebooks but failed in production. I solved it by logging models with MLflow signatures, which validate inputs at serving time. This catches schema mismatches before they cause errors."

## Key Files Explained

### train.py
- Loads and preprocesses data
- Trains ElasticNet with configurable hyperparameters
- Logs everything to MLflow (params, metrics, model)
- Infers and logs model signature
- Can run locally or on Azure ML compute

### register.py
- Registers models from MLflow runs
- Manages version lifecycle with aliases
- Compares model versions
- Updates champion/challenger aliases

### deploy.py
- Creates Azure ML Online Endpoints
- Deploys models with specified compute
- Manages traffic distribution (blue-green, canary)
- Configures health probes and scaling

### predict.py
- Makes predictions against deployed endpoints
- Handles authentication
- Measures latency
- Can test specific deployments

### utils.py
- Shared functions: Azure ML client, data loading
- Environment variable management
- Logging configuration

## Extending the Project

### For interviews, you can mention:

1. **CI/CD Integration:**
   > "I'd add GitHub Actions to automate training, registration, and deployment. On main branch push, run training, and if RMSE < baseline, auto-deploy to staging."

2. **A/B Testing:**
   > "Instead of blue-green, I could route 50% traffic to each version and compare business metrics—conversion rates, revenue per prediction—not just ML metrics."

3. **Data Drift Detection:**
   > "I'd implement Population Stability Index (PSI) monitoring. If PSI > 0.2, trigger retraining pipeline automatically."

4. **Model Explainability:**
   > "Add SHAP values to explain predictions. Log feature importance to MLflow. Provide explanations in API responses for regulatory compliance."

5. **Cost Optimization:**
   > "Right-size instances based on load testing. Implement auto-scaling. Use spot instances for training. Set compute clusters to min_instances=0 to scale to zero."

## Troubleshooting

### Training fails
- Check data path is correct
- Verify Azure ML workspace connection
- Check compute cluster quota

### Registration fails
- Ensure run_id exists in MLflow
- Check model was logged during training
- Verify permissions (need Contributor role)

### Deployment fails
- Check quota for deployment instances
- Ensure model is registered
- Verify model has valid signature

### Predictions return errors
- Check input data format matches signature
- View deployment logs: `az ml online-deployment get-logs`
- Test deployment directly (not through traffic split)

## Next Steps

1. **Practice explaining this project** in 2-3 minutes
2. **Be ready to deep-dive** into any component
3. **Prepare for follow-up questions:**
   - "How would you handle data drift?"
   - "What if the deployment fails?"
   - "How do you ensure reproducibility?"
4. **Add this to your resume** as a production ML project

## Interview Cheat Sheet

**Quick facts to remember:**

- **Business problem:** Housing price prediction
- **Model:** ElasticNet regression
- **Tracking:** MLflow with Azure ML backend
- **Deployment:** Blue-green pattern, Azure ML Online Endpoint
- **Monitoring:** Application Insights (latency, errors, drift)
- **Best RMSE:** ~45K (example metric)
- **Production uptime:** 99.9% target
- **Deployment strategy:** Zero-downtime with instant rollback
- **Key learning:** Training-serving skew prevention with model signatures

**30-second pitch:**
> "I built an end-to-end housing price prediction system. I use MLflow for experiment tracking with Azure ML as the backend, so my team can collaborate without managing servers. Models go through a registry with versioning before deployment. I deploy to Azure ML endpoints using blue-green deployment for zero downtime and instant rollback. In production, I monitor latency, errors, and data drift with Application Insights. The system maintains full lineage from production predictions back to training runs for reproducibility."

Good luck with your interview! 🚀
