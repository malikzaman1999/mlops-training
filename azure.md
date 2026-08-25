# Azure ML lab architecture

Hierarchy created by [`mslearn-mlops/infra/setup.sh`](mslearn-mlops/infra/setup.sh), from subscription down to data assets.

## Hierarchy

```
[ Azure Subscription ]
   │
   └──► [ Resource Provider ] (Microsoft.MachineLearningServices)
         │
         └──► [ Resource Group ] (rg-ai300-l...)
               │
               ├──► [ Hidden infrastructure ] (created with the workspace)
               │     ├── Azure Storage Account (blobs / file share)
               │     ├── Azure Key Vault (secrets)
               │     ├── Azure Container Registry (Docker images)
               │     └── Azure Application Insights (logs and monitoring)
               │
               └──► [ Azure ML Workspace ] (mlw-ai300-l...)
                     │
                     ├──► [ Compute instance ] (ci...)
                     ├──► [ Compute cluster ] (aml-cluster)
                     │
                     ├──► [ Data asset: MLTable ] (diabetes-training)
                     └──► [ Data asset: URI file ] (diabetes-data)
```

## What each layer is

### Resource group

A logical container in Azure Resource Manager. Group assets that share a lifecycle (workspace, storage, VMs) so you can deploy, lock, and delete them together. The group itself is free; you pay for what is inside it.

### Resource provider

A REST API that creates and manages one family of resources. `Microsoft.MachineLearningServices` handles Azure ML. It must be registered on the **subscription** before you can create workspaces.

### Workspace

A specialized environment for a workload (Azure ML, Databricks, Synapse, Log Analytics). For Azure ML it is the collaborative hub: jobs, models, data, compute. It lives in a resource group and provisions the hidden storage, Key Vault, ACR, and App Insights resources.

## Why each component exists

| Component | Why you need it |
| --- | --- |
| **Subscription** | Billing and access boundary. Azure needs to know who to invoice and who has admin rights. |
| **Resource provider** (`Microsoft.MachineLearningServices`) | API that understands ML resources. Without registration, `az ml workspace create` fails. |
| **Resource group** (`rg-ai300-l...`) | One bucket to create, lock, and delete. Delete the group and everything in the lab goes with it. |
| **Storage account** | Holds notebooks, job code, logs, and training data. |
| **Key Vault** | Stores connection strings and keys so they are not hardcoded in scripts. |
| **Container Registry (ACR)** | Builds and stores Docker images so Python environments run the same on any compute. |
| **Application Insights** | Health, job logs, and later endpoint monitoring. |
| **Workspace** (`mlw-ai300-l...`) | Command center: experiments, models, pipelines, data, compute in one portal. |
| **Compute instance** (`ci...`) | One cloud VM with Jupyter / VS Code. Interactive work instead of your laptop. |
| **Compute cluster** (`aml-cluster`) | Scalable job compute. Can sit at 0 nodes, then spin up (max 2 in this lab) for training and scale back down. |
| **Data assets** (`diabetes-training`, `diabetes-data`) | Named, versioned pointers to data. Jobs reference the asset name instead of a local path. |

### Data assets in this lab

- **MLTable** (`diabetes-training`): folder-style table for training jobs.
- **URI file** (`diabetes-data`): single CSV (`diabetes.csv`) for scripts that need one file.

## Notes from the setup script

- Provider registration is **subscription-scoped**. After it succeeds, any resource group in that subscription can host ML workspaces.
- Compute and data assets cannot exist on their own; they belong to the workspace.
- Creating the workspace automatically creates the four hidden dependencies in the **same** resource group, even though the script never names them.

## Setup script (reference)

```bash
#! /usr/bin/sh

guid=$(cat /proc/sys/kernel/random/uuid)
suffix=${guid//[-]/}
suffix=${suffix:0:18}

RESOURCE_GROUP="rg-ai300-l${suffix}"
RESOURCE_PROVIDER="Microsoft.MachineLearningServices"
REGIONS=("eastus" "westus" "centralus" "northeurope" "westeurope")
RANDOM_REGION=${REGIONS[$RANDOM % ${#REGIONS[@]}]}
WORKSPACE_NAME="mlw-ai300-l${suffix}"
COMPUTE_INSTANCE="ci${suffix}"
COMPUTE_CLUSTER="aml-cluster"

az provider register --namespace $RESOURCE_PROVIDER

az group create --name $RESOURCE_GROUP --location $RANDOM_REGION
az configure --defaults group=$RESOURCE_GROUP

az ml workspace create --name $WORKSPACE_NAME
az configure --defaults workspace=$WORKSPACE_NAME

az ml compute create --name ${COMPUTE_INSTANCE} --size STANDARD_DS11_V2 --type ComputeInstance
az ml compute create --name ${COMPUTE_CLUSTER} --size STANDARD_DS11_V2 --max-instances 2 --type AmlCompute

az ml data create --type mltable --name "diabetes-training" --path ../data/diabetes-data
az ml data create --type uri_file --name "diabetes-data" --path ../data/diabetes-data/diabetes.csv
```
