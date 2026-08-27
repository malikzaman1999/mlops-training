# ==============================================================================
# storage.tf
#
# The MLflow tracking server's ARTIFACT STORE -- where actual model files,
# plots, and logged datasets live (as opposed to database.tf's metadata).
# In the course notes this was a local `./mlruns` or `./mlflow-artifacts`
# folder; here it becomes Azure Blob Storage, the direct equivalent of the
# S3 buckets used in the course's AWS SageMaker deployment section.
# ==============================================================================

# Azure Storage Account names have unusual constraints: 3-24 characters,
# LOWERCASE letters and digits only (no hyphens, no underscores), and must
# be GLOBALLY unique across every Azure customer worldwide -- not just your
# subscription. `random_string` generates a short random suffix so our
# chosen name doesn't collide with someone else's storage account.
resource "random_string" "storage_suffix" {
  length  = 6
  special = false # no punctuation -- storage account names can't contain it
  upper   = false # lowercase only, per the naming rule above
}

resource "azurerm_storage_account" "mlflow" {
  # "st" + project name + random suffix, e.g. "stmlops8f3k2a" -- kept short
  # and lowercase/alphanumeric-only to satisfy the naming rule above.
  name                = "st${var.project_name}${random_string.storage_suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  # "Standard" performance tier (as opposed to "Premium", which is SSD-backed
  # and priced for high-throughput workloads we don't need here).
  account_tier = "Standard"

  # "LRS" = Locally Redundant Storage: Azure keeps 3 synchronous copies of
  # your data within a single datacenter. The cheapest replication option,
  # and enough durability for a learning project's model artifacts (a real
  # production system might choose "ZRS" or "GRS" for datacenter- or
  # region-level redundancy instead).
  account_replication_type = "LRS"

  # Same idea as the Postgres firewall rule in database.tf: public network
  # access stays enabled, but access is restricted to specific IPs via the
  # network_rules block below, rather than being wide open.
  public_network_access_enabled = true

  network_rules {
    default_action = "Deny"                  # deny everyone EXCEPT what's explicitly listed below
    ip_rules       = [var.allowed_client_ip] # allow only your current public IP
    bypass         = ["AzureServices"]       # lets Azure's own internal services (e.g. other
    # Azure resources acting on your behalf) through --
    # this does NOT open access to the public internet
  }
}

# A "container" in Blob Storage is roughly like a top-level folder / bucket
# -- MLflow will write its artifacts (models, plots, input examples) into
# this one, addressed via the same artifact-URI scheme covered in the
# MLflow course notes ("wasbs://..." or "https://<account>.blob.core.windows.net/...").
resource "azurerm_storage_container" "mlflow_artifacts" {
  name                  = "mlflow-artifacts"
  storage_account_id    = azurerm_storage_account.mlflow.id
  container_access_type = "private" # no anonymous/public read access -- only credentialed
  # requests (e.g. from the MLflow server, using the
  # storage account's access key) can read/write here
}
