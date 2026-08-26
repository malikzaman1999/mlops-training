"""
Shared utilities for housing price prediction project.
"""

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv


def load_environment():
    """
    Load environment variables from .env file.
    """
    load_dotenv()


def get_ml_client():
    """
    Create and return Azure ML client.

    Returns:
        MLClient instance connected to workspace
    """
    load_environment()

    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    workspace_name = os.getenv("AZURE_WORKSPACE_NAME")

    if not all([subscription_id, resource_group, workspace_name]):
        raise ValueError(
            "Missing Azure configuration. Set AZURE_SUBSCRIPTION_ID, "
            "AZURE_RESOURCE_GROUP, and AZURE_WORKSPACE_NAME in .env file"
        )

    credential = DefaultAzureCredential()

    ml_client = MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name
    )

    return ml_client


def get_mlflow_tracking_uri():
    """
    Get MLflow tracking URI from Azure ML workspace.

    Returns:
        MLflow tracking URI string
    """
    ml_client = get_ml_client()
    workspace = ml_client.workspaces.get(name=ml_client.workspace_name)
    return workspace.mlflow_tracking_uri
