# ==============================================================================
# database.tf
#
# The MLflow tracking server's BACKEND STORE -- the piece that holds
# experiment/run/param/metric/tag metadata. In the MLflow course notes this
# was `sqlite:///mlflow.db`, a single local file. Here it becomes a real,
# always-on PostgreSQL server so it can survive independently of any one
# machine and be shared by every training job / CI pipeline / teammate.
#
# We're using PUBLIC access + a firewall rule (scoped to your IP) rather
# than a Private Endpoint for this phase -- the simpler option we chose,
# with Private Endpoints as a deliberate later upgrade once more of the
# project (especially AKS) exists to actually need VNet-internal access.
# ==============================================================================

# ------------------------------------------------------------------------
# THE POSTGRES SERVER ITSELF
# "Flexible Server" is Azure's current-generation managed PostgreSQL
# offering (as opposed to the older, now-deprecated "Single Server" SKU) --
# it's the one Microsoft recommends for all new deployments.
# ------------------------------------------------------------------------
resource "azurerm_postgresql_flexible_server" "mlflow" {
  name = "psql-${var.project_name}" # "psql-mlops" -- must be globally unique
  # across all of Azure (it becomes part of
  # the server's DNS name)
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  # Which major version of PostgreSQL to run. 16 is current as of writing.
  version = "16"

  # Login credentials for the server's admin account. The password comes
  # from the `postgres_admin_password` variable, which -- as explained in
  # variables.tf -- has no default and must be supplied via an environment
  # variable or a gitignored .tfvars file, never hardcoded here.
  administrator_login    = var.postgres_admin_username
  administrator_password = var.postgres_admin_password

  # `sku_name` picks the compute tier + size. "B_Standard_B1ms" is the
  # cheapest "Burstable" tier (1 vCore, 2 GiB RAM) -- Burstable tiers are
  # designed for workloads that are mostly idle with occasional bursts,
  # which is exactly what a small learning project's tracking server looks
  # like. This is NOT what you'd choose for a real production workload
  # under constant load.
  sku_name = "B_Standard_B1ms"

  # Minimum allowed storage for Flexible Server is 32 GiB (32768 MiB) --
  # far more than this project needs, but it's the platform's floor, not
  # a choice we're making.
  storage_mb = 32768

  # Explicitly true (this is also the default) -- means the server gets a
  # public IP/DNS name reachable from outside the VNet, gated by the
  # firewall rule below rather than by network isolation. This is the
  # deliberate "simpler for now" choice.
  public_network_access_enabled = true

  # A Flexible Server MUST be told not to expect zone-redundant HA for the
  # cheap Burstable tier -- leaving this unset defaults correctly, but
  # being explicit here avoids a surprise if you later resize the SKU.
  zone = null

  # Azure won't let you delete/recreate a Postgres Flexible Server without
  # first taking a final backup unless this is set -- fine for a learning
  # project where you don't need Azure's own long-term backup retention
  # once you tear it down.
  lifecycle {
    ignore_changes = [zone] # Azure sometimes assigns a zone automatically on
    # creation even when we pass null -- this tells
    # Terraform "don't treat that as configuration
    # drift on every subsequent plan"
  }
}

# ------------------------------------------------------------------------
# FIREWALL RULE -- the actual access control
# Without this, `public_network_access_enabled = true` above still means
# NOTHING can reach the server -- Azure Postgres Flexible Server denies all
# inbound connections by default until you explicitly allow specific IP
# ranges, exactly like how AWS.md's IGW alone didn't grant internet access
# without a matching route table entry. Same lesson, different resource.
# ------------------------------------------------------------------------
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_my_ip" {
  name             = "allow-my-ip"
  server_id        = azurerm_postgresql_flexible_server.mlflow.id
  start_ip_address = var.allowed_client_ip # a /32-style single-IP rule: start == end
  end_ip_address   = var.allowed_client_ip
}

# ------------------------------------------------------------------------
# THE ACTUAL DATABASE (a schema inside the Postgres server)
# One Postgres SERVER can host many separate DATABASEs. We only need one,
# named "mlflow", for the tracking server to use as its backend store.
# ------------------------------------------------------------------------
resource "azurerm_postgresql_flexible_server_database" "mlflow" {
  name      = "mlflow"
  server_id = azurerm_postgresql_flexible_server.mlflow.id
  collation = "en_US.utf8" # sorting/comparison rules for text columns -- en_US.utf8
  # is the standard default, no reason to deviate here
  charset = "utf8"
}
