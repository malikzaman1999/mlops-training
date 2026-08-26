"""
Production Model Deployment Example

This script demonstrates deploying a model to Azure ML Online Endpoint.

For interview prep: Understand the complete deployment workflow including:
- Creating endpoints
- Deploying models
- Blue-green deployment
- Traffic splitting
- Monitoring

Note: Requires Azure ML workspace and registered model.
"""

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model,
    Environment,
    CodeConfiguration
)
from azure.identity import DefaultAzureCredential
import os
import time


def create_endpoint(ml_client, endpoint_name, description="Production model endpoint"):
    """
    Create an Azure ML Online Endpoint.

    Interview tip: An endpoint is a stable URL for making predictions.
    You can have multiple deployments (versions) behind one endpoint.

    Args:
        ml_client: Azure ML client
        endpoint_name: Name for the endpoint (must be unique in region)
        description: Description of the endpoint

    Returns:
        Created endpoint
    """
    print("="*60)
    print(f"Creating Online Endpoint: {endpoint_name}")
    print("="*60)

    # Define endpoint
    # Interview tip: auth_mode can be "key" or "aad_token"
    # - key: Simple API key authentication
    # - aad_token: Azure Active Directory (more secure for enterprise)
    endpoint = ManagedOnlineEndpoint(
        name=endpoint_name,
        description=description,
        auth_mode="key",  # or "aad_token" for AAD auth
        tags={"environment": "production", "team": "ml-engineering"}
    )

    print(f"Endpoint configuration:")
    print(f"  Name: {endpoint_name}")
    print(f"  Auth mode: key")
    print(f"  Description: {description}")

    # Create endpoint (this takes a few minutes)
    print(f"\nCreating endpoint...")
    endpoint_result = ml_client.online_endpoints.begin_create_or_update(endpoint).result()

    print(f"\n✓ Endpoint created!")
    print(f"  Scoring URI: {endpoint_result.scoring_uri}")
    print(f"  Swagger URI: {endpoint_result.swagger_uri}")

    return endpoint_result


def deploy_model(
    ml_client,
    endpoint_name,
    deployment_name,
    model_name,
    model_version,
    instance_type="Standard_DS2_v2",
    instance_count=2
):
    """
    Deploy a model to an endpoint.

    Interview tip: A deployment is a specific model version with compute resources.
    You can have multiple deployments (blue/green) behind one endpoint.

    Args:
        ml_client: Azure ML client
        endpoint_name: Name of the endpoint
        deployment_name: Name for this deployment (e.g., "blue", "green")
        model_name: Name of registered model
        model_version: Version to deploy
        instance_type: VM size for serving
        instance_count: Number of instances (for scaling)

    Returns:
        Deployment object
    """
    print("\n" + "="*60)
    print(f"Deploying Model to Endpoint")
    print("="*60)

    # Interview tip: Common instance types
    # - Standard_DS2_v2: 2 vCPU, 7 GB RAM (good for most models)
    # - Standard_F4s_v2: 4 vCPU, 8 GB RAM (CPU-optimized)
    # - Standard_NC6s_v3: 6 vCPU, 112 GB RAM, 1 GPU (for deep learning)

    deployment = ManagedOnlineDeployment(
        name=deployment_name,
        endpoint_name=endpoint_name,
        model=Model(name=model_name, version=model_version),
        instance_type=instance_type,
        instance_count=instance_count,

        # Resource limits per instance
        request_settings={
            "request_timeout_ms": 60000,  # 60 seconds
            "max_concurrent_requests_per_instance": 1
        },

        # Liveness and readiness probes
        liveness_probe={
            "initial_delay": 10,
            "period": 10,
            "timeout": 2,
            "success_threshold": 1,
            "failure_threshold": 3
        },

        readiness_probe={
            "initial_delay": 10,
            "period": 10,
            "timeout": 2,
            "success_threshold": 1,
            "failure_threshold": 3
        }
    )

    print(f"Deployment configuration:")
    print(f"  Deployment name: {deployment_name}")
    print(f"  Model: {model_name} v{model_version}")
    print(f"  Instance type: {instance_type}")
    print(f"  Instance count: {instance_count}")

    # Deploy (this takes several minutes)
    print(f"\nDeploying model... (this may take 5-10 minutes)")
    deployment_result = ml_client.online_deployments.begin_create_or_update(deployment).result()

    print(f"\n✓ Deployment complete!")
    print(f"  Deployment: {deployment_name}")

    return deployment_result


def set_traffic(ml_client, endpoint_name, traffic_allocation):
    """
    Set traffic distribution across deployments.

    Interview tip: This enables blue-green and canary deployments!
    - Blue-green: Switch from {"blue": 100} to {"green": 100}
    - Canary: Gradually shift {"blue": 90, "green": 10} → {"blue": 0, "green": 100}

    Args:
        ml_client: Azure ML client
        endpoint_name: Name of endpoint
        traffic_allocation: Dict mapping deployment name to traffic % (must sum to 100)
    """
    print("\n" + "="*60)
    print(f"Setting Traffic Distribution")
    print("="*60)

    print(f"Traffic allocation:")
    for deployment, percentage in traffic_allocation.items():
        print(f"  {deployment}: {percentage}%")

    # Get endpoint and update traffic
    endpoint = ml_client.online_endpoints.get(name=endpoint_name)
    endpoint.traffic = traffic_allocation

    ml_client.online_endpoints.begin_create_or_update(endpoint).result()

    print(f"\n✓ Traffic updated!")


def test_endpoint(ml_client, endpoint_name, sample_data, deployment_name=None):
    """
    Test an endpoint with sample data.

    Interview tip: Always test before routing production traffic!

    Args:
        ml_client: Azure ML client
        endpoint_name: Name of endpoint
        sample_data: Input data for prediction
        deployment_name: Optional specific deployment to test

    Returns:
        Prediction result
    """
    print("\n" + "="*60)
    print(f"Testing Endpoint")
    print("="*60)

    # Get endpoint details
    endpoint = ml_client.online_endpoints.get(name=endpoint_name)

    print(f"Endpoint: {endpoint_name}")
    if deployment_name:
        print(f"Testing specific deployment: {deployment_name}")
    else:
        print(f"Testing default deployment (traffic split applied)")

    # Invoke endpoint
    # Interview tip: You can test a specific deployment or let traffic split decide
    result = ml_client.online_endpoints.invoke(
        endpoint_name=endpoint_name,
        deployment_name=deployment_name,  # None = use traffic split
        request_file=sample_data
    )

    print(f"\n✓ Prediction successful!")
    print(f"Result: {result}")

    return result


def blue_green_deployment_workflow(ml_client, endpoint_name, model_name):
    """
    Demonstrate complete blue-green deployment workflow.

    Interview tip: This is the safest way to deploy new models!

    Workflow:
    1. Deploy initial model as "blue" (100% traffic)
    2. Deploy new model as "green" (0% traffic)
    3. Test green deployment
    4. Switch traffic to green (instant cutover)
    5. Monitor, then delete blue

    Args:
        ml_client: Azure ML client
        endpoint_name: Name of endpoint
        model_name: Name of model to deploy
    """
    print("\n" + "="*70)
    print("BLUE-GREEN DEPLOYMENT WORKFLOW")
    print("="*70)

    # === Step 1: Deploy Blue (initial) ===
    print("\n--- Step 1: Deploy Blue (v1) ---")
    deploy_model(
        ml_client=ml_client,
        endpoint_name=endpoint_name,
        deployment_name="blue",
        model_name=model_name,
        model_version="1",
        instance_count=2
    )

    set_traffic(ml_client, endpoint_name, {"blue": 100})
    print("✓ Blue is live with 100% traffic")

    # === Step 2: Deploy Green (new version) ===
    print("\n--- Step 2: Deploy Green (v2) ---")
    deploy_model(
        ml_client=ml_client,
        endpoint_name=endpoint_name,
        deployment_name="green",
        model_name=model_name,
        model_version="2",
        instance_count=2
    )

    # No traffic yet!
    print("✓ Green deployed but receiving 0% traffic")

    # === Step 3: Test Green ===
    print("\n--- Step 3: Test Green Deployment ---")
    print("Testing green deployment directly (not through endpoint traffic)")
    # test_endpoint(ml_client, endpoint_name, "sample.json", deployment_name="green")
    print("✓ Green tested successfully (simulated)")

    # === Step 4: Cutover ===
    print("\n--- Step 4: Instant Cutover ---")
    set_traffic(ml_client, endpoint_name, {"blue": 0, "green": 100})
    print("✓ Traffic switched to green!")
    print("  If issues detected, instant rollback: set traffic back to blue")

    # === Step 5: Monitor and Cleanup ===
    print("\n--- Step 5: Monitor and Cleanup ---")
    print("Monitor green for 24-48 hours...")
    print("If stable, delete blue deployment:")
    print(f"  ml_client.online_deployments.begin_delete(name='blue', endpoint_name='{endpoint_name}')")

    print("\n" + "="*70)
    print("Blue-green deployment complete!")
    print("="*70)


def canary_deployment_workflow(ml_client, endpoint_name, model_name):
    """
    Demonstrate canary deployment workflow.

    Interview tip: Gradual rollout with monitoring between steps.

    Workflow:
    1. Deploy blue with 100% traffic
    2. Deploy green with 0% traffic
    3. Shift 10% → green, monitor
    4. Shift 50% → green, monitor
    5. Shift 100% → green
    6. Delete blue

    Args:
        ml_client: Azure ML client
        endpoint_name: Name of endpoint
        model_name: Name of model
    """
    print("\n" + "="*70)
    print("CANARY DEPLOYMENT WORKFLOW")
    print("="*70)

    # Deploy both versions
    print("\n--- Initial State ---")
    print("Blue (v1): 100% traffic")
    print("Green (v2): deployed, 0% traffic")

    # Canary rollout
    canary_steps = [
        {"blue": 90, "green": 10},
        {"blue": 50, "green": 50},
        {"blue": 10, "green": 90},
        {"blue": 0, "green": 100}
    ]

    for i, traffic in enumerate(canary_steps, 1):
        print(f"\n--- Canary Step {i} ---")
        print(f"Traffic: Blue {traffic['blue']}%, Green {traffic['green']}%")
        # set_traffic(ml_client, endpoint_name, traffic)
        print("Monitor for 2-4 hours...")
        print("  - Check error rates")
        print("  - Check latency (p95, p99)")
        print("  - Compare predictions between blue/green")
        print("  - If issues: ROLLBACK (set blue to 100%)")
        print("✓ Metrics look good, proceeding...")

    print("\n✓ Canary rollout complete! Green at 100%")


def get_deployment_logs(ml_client, endpoint_name, deployment_name, lines=100):
    """
    Get logs from a deployment.

    Interview tip: Essential for debugging deployment issues!

    Args:
        ml_client: Azure ML client
        endpoint_name: Name of endpoint
        deployment_name: Name of deployment
        lines: Number of log lines to retrieve
    """
    print(f"\nGetting logs for {deployment_name}...")

    logs = ml_client.online_deployments.get_logs(
        name=deployment_name,
        endpoint_name=endpoint_name,
        lines=lines
    )

    print(logs)
    return logs


def monitor_endpoint_metrics(ml_client, endpoint_name):
    """
    Get metrics for an endpoint.

    Interview tip: In production, you'd integrate with Azure Monitor/App Insights.
    Key metrics to track:
    - Request latency (p50, p95, p99)
    - Error rate (4xx, 5xx)
    - Throughput (requests/sec)
    - Resource utilization (CPU, memory)

    This is a simplified example showing the concept.
    """
    print("\n" + "="*60)
    print("Monitoring Endpoint")
    print("="*60)

    print(f"\nKey metrics to monitor for {endpoint_name}:")
    print("\n1. Latency (Application Insights):")
    print("   - p50, p95, p99 latency")
    print("   - Target: < 100ms for real-time, < 1s for batch")
    print("\n2. Error Rate:")
    print("   - 4xx errors (client errors)")
    print("   - 5xx errors (server errors)")
    print("   - Target: < 0.1% error rate")
    print("\n3. Throughput:")
    print("   - Requests per second")
    print("   - Ensure within capacity")
    print("\n4. Resource Utilization:")
    print("   - CPU usage")
    print("   - Memory usage")
    print("   - Consider auto-scaling if > 70%")

    print("\nQuery Application Insights (KQL):")
    print("""
    // Request latency
    requests
    | where name == "POST /predict"
    | summarize p95=percentile(duration, 95) by bin(timestamp, 5m)

    // Error rate
    requests
    | where name == "POST /predict"
    | summarize ErrorRate = (countif(success == false) * 100.0) / count()
      by bin(timestamp, 5m)
    """)


def main():
    """
    Main demonstration.
    """
    print("\n" + "="*70)
    print("Production Model Deployment Demo")
    print("="*70)

    # Configuration
    SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "YOUR_SUBSCRIPTION_ID")
    RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "rg-mlops-demo")
    WORKSPACE_NAME = os.getenv("AZURE_WORKSPACE_NAME", "mlw-demo")
    ENDPOINT_NAME = os.getenv("ENDPOINT_NAME", "housing-price-endpoint")
    MODEL_NAME = os.getenv("MODEL_NAME", "HousingPriceModel")

    if SUBSCRIPTION_ID == "YOUR_SUBSCRIPTION_ID":
        print("\n⚠️  This demo requires an Azure ML workspace and registered model.")
        print("\nTo run:")
        print("  1. Set up Azure ML workspace")
        print("  2. Register a model (see model-registry-workflow example)")
        print("  3. Set environment variables")
        print("\nFor interview prep: Read the code to understand deployment patterns!\n")

        # Show conceptual demos
        print("\n" + "="*70)
        print("CONCEPTUAL DEMOS (No Azure Required)")
        print("="*70)

        print("\nBlue-Green Deployment Pattern:")
        print("  1. Deploy new version (green) with 0% traffic")
        print("  2. Test green deployment")
        print("  3. Instant cutover: 100% → green")
        print("  4. Monitor, rollback if needed")
        print("  5. Delete old version (blue)")

        print("\nCanary Deployment Pattern:")
        print("  1. Deploy new version with 0% traffic")
        print("  2. Gradually increase: 10% → 25% → 50% → 100%")
        print("  3. Monitor metrics at each step")
        print("  4. Rollback immediately if issues")

        return

    try:
        # Connect to workspace
        credential = DefaultAzureCredential()
        ml_client = MLClient(
            credential=credential,
            subscription_id=SUBSCRIPTION_ID,
            resource_group_name=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME
        )

        print(f"✓ Connected to workspace: {WORKSPACE_NAME}")

        # Create endpoint
        endpoint = create_endpoint(ml_client, ENDPOINT_NAME)

        # Deploy model
        deployment = deploy_model(
            ml_client=ml_client,
            endpoint_name=ENDPOINT_NAME,
            deployment_name="blue",
            model_name=MODEL_NAME,
            model_version="1"
        )

        # Set traffic
        set_traffic(ml_client, ENDPOINT_NAME, {"blue": 100})

        # Show monitoring
        monitor_endpoint_metrics(ml_client, ENDPOINT_NAME)

        print("\n" + "="*70)
        print("✓ Deployment Complete!")
        print("="*70)
        print(f"\nEndpoint URL: {endpoint.scoring_uri}")
        print("\nNext steps:")
        print("  1. Test endpoint with sample data")
        print("  2. Monitor metrics in Azure ML Studio")
        print("  3. Set up alerts for errors/latency")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure model is registered")
        print("  2. Check permissions (need Contributor role)")
        print("  3. Verify quota for compute instances")


if __name__ == "__main__":
    main()
