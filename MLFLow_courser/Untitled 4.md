---
title: "Course: MLflow in Action - Master the art of MLOps using MLflow tool | Udemy Business"
description: A master guide to unleash the full potential of MLflow to optimize MLOps. Streamline MLOps workflows using MLflow tool
author: Udemy Business
source: https://10pearls.udemy.com/course/mlflow-course/learn/lecture/41273446#learning-tools
created: "2026-08-23"
tags:
  - hover-notes
  - udemy
hovernotes-id: doc_1502d536-83ca-4fe4-a2f3-f429091fd2e6
---

### MLflow SageMaker Container Deployment

- Use MLflow to build and push a Docker container image that encapsulates the ML model, its dependencies, and configurations
- **[Two-step process]**
    - **Task 1: Build**
        - MLflow prepares a Docker image with all necessary dependencies and configurations specified for deployment
    - **Task 2: Push**
        - The built image is pushed to Amazon ECR (Amazon Elastic Container Registry)
        - This makes the container image accessible and ready for deployment on Amazon SageMaker
- **Command Execution**
    - The command used follows this structure:

```bash
mlflow sagemaker build-and-push-container --container-name xgb --env-manager conda
```

    - **Parameters used:**
        - `--container-name xgb`: Sets the name of the container (must be all lowercase)
        - `--env-manager conda`: Sets the environment manager (defaults to `virtualenv`, but `conda` is used here)
- **Deployment Requirement**
    - Before deploying to production, the IAM role must have the necessary permissions to register the container to ECR

### Amazon ECR (Elastic Container Registry)

- A fully managed AWS container registry service
    - Designed to store, manage, and deploy Docker container images
- **[Verifying the Image]** After the `mlflow sagemaker build-and-push-container` command completes, the image can be found in the ECR console
    - The console provides critical metadata for deployment:
        - Image tag
        - Push timestamp
        - Image size
        - **Image URI** (Required for creating the endpoint)

### Deploying the Model Endpoint

- Once the Docker image is in ECR, it can be deployed as an endpoint to serve the model
- **Deployment Methods**
    - CLI command
    - Python code (using the SageMaker SDK)
- **Implementation via Python**
    - The deployment logic is encapsulated in a script named `deploy.py`

```python
import mlflow.sagemaker
from mlflow.deployments import get_deploy_client

endpoint_name = "prod_endpoint"
model_uri = "..."

# Define configuration parameters as a dictionary
config = {
    "execution_role_arn": "...",
    "bucket_name": "mlflow-project-artifacts",
    "image_uri": "...",
    "region": "us-east-1",
    "instance_type": "ml.m5.xlarge",
    "instance_count": 1,
    "synchronous": True
}

# Initialize a deployment client for SageMaker
client = get_deploy_client("sagemaker")

# Create the deployment
client.create_deployment(
    name=endpoint_name,
    model_uri=model_uri,
    flavor="python_function",
    config=config
)
```

### MLflow Deployment Logic

- The `mlflow.deployments` module provides functionality to deploy models to custom serving tools
- For AWS-specific workflows, deployment to SageMaker is performed using the `mlflow.sagemaker` module
- **Core Deployment Functions**
    - `get_deploy_client("sagemaker")`: Initializes the deployment client specifically for the SageMaker service
    - `client.create_deployment(...)`: Executes the actual deployment to a specified target using several key parameters:
        - `name`: A unique identifier for the deployment (e.g., `prod_endpoint`).
            - **Note:** This must be in lowercase; using a duplicate name will raise an exception.
        - `model_uri`: The specific URI of the model version to be deployed (retrieved from an MLflow run, such as an XGBoost model version)
        - `flavor`: The model flavor being used (e.g., `"python_function"`)
        - `config`: A dictionary containing infrastructure and environmental settings (e.g., `execution_role_arn`, `instance_type`, `image_uri`)

### SageMaker Deployment Configuration Details

- The `config` dictionary passed to `client.create_deployment` contains target-specific settings for AWS
- **Key Configuration Parameters**
    - `execution_role_arn`: The Amazon Resource Name (ARN) of the IAM role assigned to SageMaker
        - **How to find it**: Navigate to the IAM service $\rightarrow$ Roles $\rightarrow$ Select your role $\rightarrow$ Copy the ARN value
    - `bucket_name`: The name of the S3 bucket used for project artifacts (e.g., `"mlflow-project-artifacts"`)
    - `image_uri`: The URI of the Docker image stored in Amazon ECR
    - `region`: The AWS region where the endpoint will be hosted (e.g., `"us-east-1"`)
    - `archive`: Set to `False`
    - `instance_count`: The number of instances to run (e.g., `1`)
    - `instance_type`: The hardware specification for the endpoint (e.g., `"ml.m5.xlarge"`)
- **[Critical Warning] Instance Selection**
    - Avoid using small instances like `t2.medium` for endpoints
    - **Why?** They may take hours to create or fail entirely due to insufficient resources
    - It is recommended to use at least an `ml.m5.xlarge` or similar specification

### Executing SageMaker Deployment

- Running the deployment script (`deploy.py`) triggers the creation of the endpoint
- **[Handling Errors]** If the deployment fails with a validation error, it may be due to the endpoint name
    - **Error Example**: `ValueError: 'prod_endpoint' at 'namecontains' failed to satisfy constraint...`
    - **Resolution**: Change the `name` parameter in the configuration to a valid string that satisfies the required regular expression pattern
- **Deployment Lifecycle**
    - Once the script is run successfully, the terminal will indicate that the endpoint is being created
    - The creation phase typically takes several minutes

### Verifying the Endpoint Status

- After the creation process completes, the status must be verified in the AWS Management Console
- **Steps to Verify**

    1. Navigate to the **SageMaker** service
    2. Select **Inference** from the left-hand menu
    3. Click on **Endpoints**

- **Successful Deployment Indicator**
    - The endpoint status should display as `InService`
    - An `InService` status confirms that the model is ready to receive inference requests

### Performing Inference with SageMaker

- **[Required Libraries]**
    - `boto3`: Used to interact with AWS services via Python
    - `json`: Used to serialize data into the format required for inference requests
    - `test_dataset`: The local data used for testing the model
- **[Client Initialization]**
    - Two distinct Boto3 clients are required to handle different aspects of SageMaker:
        - `sm_client`: Manages SageMaker resources and configurations (e.g., creating/deleting models, endpoints, and jobs)
        - `smrt_client`: Specifically for runtime operations, such as sending data to an endpoint and receiving predictions
- **[Data Preparation]**
    - Data must be converted into a JSON format to be compatible with the endpoint
    - Example logic: Taking the first 10 rows of a dataset, converting them to a list, and serializing via `json.dumps()`
- **[Inference Execution]**
    - The `invoke_endpoint` function on the `smrt_client` is used to send the prepared data to the deployed model and retrieve the prediction

```python
from data import test_dataset, boto3, json

endpoint_name = "prod_endpoint"
region = "us-east-1"

sm = boto3.client("sagemaker", region_name=region)
smrt = boto3.client("runtime.sagemaker", region_name=region)

test_data = json.dumps(test_dataset[:10].toarray().tolist(), default=str)

prediction = smrt.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="application/json",
    Body=test_data
)

prediction = prediction["Body"].read().decode("ascii")
print(prediction)
```

### Completing the Inference Request

- **[Arguments for&#32;`invoke_endpoint`]**
    - `EndpointName`: The name of the deployed SageMaker endpoint
    - `ContentType`: Set to `"application/json"` to match the serialized data format
    - `Body`: The actual input data (the test dataset)
- **[Processing the Response]**
    - The `invoke_endpoint` method triggers the endpoint and returns a response object in the `prediction` variable
    - To access the actual result, the response body must be read and decoded:

```python
prediction = prediction["Body"].read().decode("ascii")
print(prediction)
```

- **[Real-World Application of Predictions]**
    - In a production pipeline, these predictions are not just printed; they are passed to downstream applications
    - **Examples of use cases:**
        - Powering user-facing dashboards
        - Triggering new automated machine learning pipelines

### Project Conclusion

- **[Project Scope]** The project demonstrated the integration of MLflow with AWS SageMaker
- **[Summary]** Successfully covered the workflow from model management to deploying endpoints and performing inference