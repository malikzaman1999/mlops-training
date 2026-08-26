# Production Model Deployment Example

This example demonstrates deploying ML models to production using Azure ML Online Endpoints.

## What You'll Learn

✅ **Deployment Strategies:**
- Blue-green deployment (instant cutover, easy rollback)
- Canary deployment (gradual rollout with monitoring)
- Traffic splitting across deployments

✅ **Azure ML Endpoints:**
- Creating online endpoints
- Deploying models to endpoints
- Managing traffic distribution
- Testing and monitoring

✅ **Production Best Practices:**
- Health probes (liveness, readiness)
- Resource limits and scaling
- Authentication (API key vs AAD token)
- Monitoring and alerting

## Prerequisites

1. **Azure ML workspace** with registered model
2. **Compute quota** for deployment instances
3. **Azure CLI** and **Python SDK** installed

## Deployment Concepts

### Online Endpoint

An **endpoint** is a stable HTTPS URL for making predictions.

```
https://<endpoint-name>.<region>.inference.ml.azure.com/score
```

**Key features:**
- Stable URL (never changes)
- Authentication (API key or AAD token)
- Can have multiple deployments behind it
- Handles traffic routing

### Deployment

A **deployment** is a specific model version with compute resources.

```
Endpoint: housing-price-endpoint
├── Deployment: blue (v1, 2 instances of Standard_DS2_v2)
└── Deployment: green (v2, 2 instances of Standard_DS2_v2)
```

**Interview tip:** One endpoint, multiple deployments = safe model updates!

## Deployment Strategies

### 1. Blue-Green Deployment

**Best for:** Zero-downtime deployments with instant rollback capability

**Workflow:**
```
1. Blue (v1) serving 100% traffic
2. Deploy Green (v2) with 0% traffic
3. Test Green deployment
4. Switch traffic: 100% → Green (instant!)
5. Monitor Green
6. If good: delete Blue
   If bad: switch back to Blue (instant rollback!)
```

**Pros:**
- Instant cutover
- Instant rollback
- Simple to understand

**Cons:**
- 2x compute cost during transition
- No gradual testing with real traffic

**Code:**
```python
# Deploy blue
deploy_model(..., deployment_name="blue", model_version="1")
set_traffic(endpoint, {"blue": 100})

# Deploy green
deploy_model(..., deployment_name="green", model_version="2")

# Test green directly
test_endpoint(endpoint, deployment_name="green")

# Cutover
set_traffic(endpoint, {"green": 100, "blue": 0})

# Rollback if needed
set_traffic(endpoint, {"blue": 100, "green": 0})
```

### 2. Canary Deployment

**Best for:** Risk-averse deployments, gradual validation with real traffic

**Workflow:**
```
1. Blue (v1) at 100%
2. Deploy Green (v2) at 0%
3. Shift 10% → Green, monitor 2-4 hours
4. Shift 25% → Green, monitor 2-4 hours
5. Shift 50% → Green, monitor 2-4 hours
6. Shift 100% → Green
7. Delete Blue
```

**Pros:**
- Gradual exposure to real traffic
- Early detection of issues (only 10% affected)
- Can monitor comparison metrics

**Cons:**
- Slower rollout
- More complex monitoring
- Still 2x cost during transition

**Code:**
```python
canary_steps = [10, 25, 50, 75, 100]

for percentage in canary_steps:
    set_traffic(endpoint, {
        "green": percentage,
        "blue": 100 - percentage
    })

    # Monitor for 2-4 hours
    monitor_metrics(endpoint)

    if metrics_look_bad():
        # Rollback
        set_traffic(endpoint, {"blue": 100, "green": 0})
        break
```

### 3. Shadow Deployment (Advanced)

**Best for:** Testing new models without affecting users

**Workflow:**
1. Blue serves all traffic (users see Blue predictions)
2. Green receives copy of traffic (predictions logged but not returned)
3. Compare Blue vs Green predictions offline
4. If Green is better, promote to Blue-Green or Canary

**Pros:**
- Zero user impact
- Real traffic testing
- Can compare predictions

**Cons:**
- Requires custom implementation
- 2x inference cost
- Complex logging

## Setup

### Step 1: Install Dependencies

```bash
cd interview-prep/code-examples/production-deployment
pip install -r requirements.txt
```

### Step 2: Set Environment Variables

```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="rg-mlops-demo"
export AZURE_WORKSPACE_NAME="mlw-demo"
export ENDPOINT_NAME="my-model-endpoint"
export MODEL_NAME="MyModel"
```

### Step 3: Ensure Model is Registered

You need a registered model (see `../model-registry-workflow/`):

```bash
# Check registered models
az ml model list -o table
```

## Running the Example

### Deploy a Model

```python
from deploy_model import create_endpoint, deploy_model, set_traffic

# Create endpoint
endpoint = create_endpoint(ml_client, "my-endpoint")

# Deploy model
deployment = deploy_model(
    ml_client=ml_client,
    endpoint_name="my-endpoint",
    deployment_name="blue",
    model_name="MyModel",
    model_version="1",
    instance_type="Standard_DS2_v2",
    instance_count=2
)

# Route traffic
set_traffic(ml_client, "my-endpoint", {"blue": 100})
```

### Test the Endpoint

```bash
# Get endpoint details
az ml online-endpoint show -n my-endpoint

# Get API key
az ml online-endpoint get-credentials -n my-endpoint

# Test with curl
curl -X POST <scoring-uri> \
  -H "Authorization: Bearer <api-key>" \
  -H "Content-Type: application/json" \
  -d '{"data": [[1.5, 2.0, 3.5]]}'
```

### Monitor Logs

```bash
# Get deployment logs
az ml online-deployment get-logs \
  -n blue \
  -e my-endpoint \
  --lines 100
```

## Instance Types

Choose based on model requirements:

| Instance Type | vCPU | RAM | GPU | Use Case |
|--------------|------|-----|-----|----------|
| Standard_DS2_v2 | 2 | 7 GB | - | Small models, low traffic |
| Standard_DS3_v2 | 4 | 14 GB | - | Medium models |
| Standard_F4s_v2 | 4 | 8 GB | - | CPU-optimized |
| Standard_NC6s_v3 | 6 | 112 GB | 1 | Deep learning (GPU) |

**Interview tip:** Start small, scale up based on metrics!

## Monitoring Best Practices

### 1. Application Insights

Query latency:
```kusto
requests
| where name == "POST /score"
| summarize p95=percentile(duration, 95) by bin(timestamp, 5m)
| render timechart
```

Query error rate:
```kusto
requests
| where name == "POST /score"
| summarize ErrorRate = (countif(success == false) * 100.0) / count()
  by bin(timestamp, 5m)
```

### 2. Key Metrics to Track

**Latency:**
- p50, p95, p99 percentiles
- Target: < 100ms for real-time, < 1s for batch

**Availability:**
- Uptime percentage
- Target: > 99.9% (3 nines)

**Error Rate:**
- 4xx (client errors), 5xx (server errors)
- Target: < 0.1%

**Throughput:**
- Requests per second
- Ensure within instance capacity

**Resource Utilization:**
- CPU, memory usage
- Scale if consistently > 70%

### 3. Alerts

Set up alerts for:
- Error rate > 1%
- p95 latency > 500ms
- Availability < 99%
- CPU usage > 80%

## Interview Practice

### Questions to Answer Out Loud

1. **What's the difference between an endpoint and a deployment?**
   > "An endpoint is a stable URL for predictions that never changes. A deployment is a specific model version with compute resources. You can have multiple deployments behind one endpoint, allowing safe model updates through traffic splitting."

2. **Explain blue-green deployment.**
   > "Blue is the current production model. You deploy green (new model) with 0% traffic, test it, then instantly switch 100% traffic to green. If issues arise, you can instantly roll back to blue. It's the safest deployment strategy with zero downtime."

3. **Explain canary deployment.**
   > "You gradually shift traffic from the old model to the new model: 10%, 25%, 50%, 100%. At each step, you monitor metrics for 2-4 hours. If anything looks wrong, you roll back. It's slower than blue-green but safer because you catch issues when only a small percentage of traffic is affected."

4. **What metrics should you monitor for a deployed model?**
   > "Four layers: (1) Infrastructure—CPU, memory, uptime. (2) Input data—check for drift, missing values, schema changes. (3) Predictions—distribution, outliers, confidence scores. (4) Business metrics—conversion rates, revenue impact. Also track latency (p95, p99) and error rates."

5. **How do you decide which instance type to use?**
   > "Start with the model's requirements: CPU-only models use Standard_DS or F-series, GPU models use NC-series. Choose size based on model memory footprint and expected latency. Start small (DS2_v2), load test, then scale up if needed. Monitor CPU/memory usage to right-size."

6. **How do you handle a bad deployment?**
   > "Immediate rollback by switching traffic back to the previous deployment. Investigate logs, check for data drift or code bugs. Fix the issue, re-register model, test thoroughly, then retry deployment. Always keep the previous version deployed for quick rollback."

### Hands-On Practice

1. **Deploy a model end-to-end:**
   - Register model from MLflow run
   - Create endpoint
   - Deploy as "blue"
   - Test with sample data

2. **Practice blue-green:**
   - Deploy v2 as "green"
   - Test green directly
   - Switch traffic
   - Practice rollback

3. **Simulate canary rollout:**
   - Write a script to gradually shift traffic
   - Add monitoring between steps
   - Practice rollback at 25%

4. **Monitor metrics:**
   - Query Application Insights
   - Create latency chart
   - Set up alert rules

## Common Issues

### Issue 1: Deployment fails with quota exceeded
**Solution:** Request quota increase or use smaller instance type
```bash
az vm list-usage --location eastus -o table
```

### Issue 2: Model returns errors (5xx)
**Check:**
- Deployment logs for stack traces
- Model signature matches input data
- Model dependencies are in environment

### Issue 3: High latency
**Solutions:**
- Scale up instance type (more CPU/RAM)
- Scale out instance count (more replicas)
- Optimize model (quantization, pruning)
- Add caching for common requests

### Issue 4: Can't delete deployment
**Cause:** Deployment is receiving traffic
**Solution:** Set traffic to 0% first
```python
set_traffic(ml_client, endpoint_name, {"blue": 0, "green": 100})
# Now you can delete blue
```

## Cost Optimization

**Strategies:**
- Use smallest instance that meets performance needs
- Scale down instance count during low-traffic hours
- Delete old deployments after validation period
- Use spot instances for non-critical workloads (up to 90% savings)
- Set up auto-scaling based on request load

**Example costs (approximate):**
- Standard_DS2_v2: ~$0.11/hour per instance
- 2 instances, 24/7: ~$160/month
- Blue-green during 1-hour cutover: ~$0.22 extra

## Next Steps

After mastering this example:

1. **Set up CI/CD:** Automate deployments with GitHub Actions or Azure Pipelines
2. **Add monitoring:** Integrate Application Insights alerts
3. **Implement A/B testing:** Split traffic for business metric comparison
4. **Full project:** See `../../housing-price-azure-deployment/` for complete example

## Interview Cheat Sheet

**Quick reference:**

```python
from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, Model

# Create endpoint
endpoint = ManagedOnlineEndpoint(name="my-endpoint", auth_mode="key")
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Deploy model
deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name="my-endpoint",
    model=Model(name="MyModel", version="1"),
    instance_type="Standard_DS2_v2",
    instance_count=2
)
ml_client.online_deployments.begin_create_or_update(deployment).result()

# Set traffic
endpoint.traffic = {"blue": 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Test
ml_client.online_endpoints.invoke(endpoint_name="my-endpoint", request_file="sample.json")
```

**Key facts:**
- Endpoint = stable URL, Deployment = model version + compute
- Blue-green = instant cutover, Canary = gradual rollout
- Monitor: latency, errors, throughput, resource usage
- Always keep previous deployment for rollback
- Traffic dict must sum to 100%

Good luck with your interview! 🚀
