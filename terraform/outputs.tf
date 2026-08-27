# ==============================================================================
# outputs.tf
#
# OUTPUT VALUES are things Terraform prints to the terminal after a
# successful `apply` (and that other Terraform configs/modules could read
# programmatically later, e.g. when we add AKS in a future phase and need
# to know which subnet to place the cluster's nodes into).
#
# Without these, after `apply` finishes you'd have to go dig through the
# Azure Portal or run `az` CLI queries to find the real IDs Azure assigned
# to what you just created. Outputs surface that information immediately.
#
# Every value below is only known AFTER `apply` actually creates the real
# resource -- that's why `terraform plan` shows these as
# "(known after apply)" rather than a real value.
# ==============================================================================

output "resource_group_name" {
  value = azurerm_resource_group.main.name # just "rg-mlops" -- this one IS knowable
  # before apply, since we hardcoded it via
  # the project_name variable rather than
  # letting Azure generate it
}

output "vnet_id" {
  # Azure resource IDs are long, globally-structured strings, e.g.:
  #   /subscriptions/<sub-id>/resourceGroups/rg-mlops/providers/
  #   Microsoft.Network/virtualNetworks/vnet-mlops
  # Terraform can't know this string until Azure actually creates the
  # resource and assigns it -- hence "(known after apply)" in the plan.
  value = azurerm_virtual_network.main.id
}

output "subnet_1_id" {
  value = azurerm_subnet.app_1.id
}

output "subnet_2_id" {
  value = azurerm_subnet.app_2.id
}
