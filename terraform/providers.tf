# ==============================================================================
# providers.tf
#
# This file tells Terraform two things:
#   1. Which version of Terraform itself, and which "provider" plugins, this
#      project needs (the `terraform {}` block).
#   2. How to configure the provider(s) it will actually use (the
#      `provider "azurerm" {}` block).
#
# A "provider" is a plugin that knows how to talk to one specific platform's
# API. Terraform's core engine knows nothing about Azure, AWS, or anything
# else by itself -- all of that platform-specific knowledge (what a
# "virtual network" is, what fields it needs, how to create/read/update/
# delete one via the API) lives inside the provider plugin. `azurerm` is the
# official HashiCorp provider for Azure Resource Manager (the modern Azure
# API surface -- as opposed to the old "classic" Azure API).
# ==============================================================================

terraform {
  # The minimum version of the Terraform CLI itself required to run this
  # config. Protects against someone using an ancient Terraform binary that
  # doesn't understand syntax/features this config relies on.
  required_version = ">= 1.9"

  required_providers {
    azurerm = {
      # `source` = where Terraform downloads this provider plugin from.
      # "hashicorp/azurerm" resolves to the Terraform Registry
      # (registry.terraform.io/providers/hashicorp/azurerm).
      source = "hashicorp/azurerm"

      # `version` = which version(s) of the provider are acceptable.
      # "~> 4.0" means "any 4.x version, but not 5.0 or higher" -- this is
      # the pessimistic version constraint operator. It protects you from a
      # provider major-version upgrade silently changing resource behavior
      # underneath you. `terraform init` writes the EXACT version it picked
      # into .terraform.lock.hcl, so re-running init later reuses that exact
      # version instead of drifting to a newer 4.x release.
      version = "~> 4.0"
    }

    # A second, small provider used only to generate a random suffix for
    # the Storage Account name in storage.tf (Azure Storage Account names
    # must be GLOBALLY unique across all of Azure, not just your
    # subscription -- "random" gives us an easy way to avoid a naming
    # collision with someone else's storage account elsewhere in the world).
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

# This block configures the azurerm provider itself (as opposed to the
# `required_providers` block above, which just declared that we need it).
provider "azurerm" {
  # `features {}` is REQUIRED by the azurerm provider even when empty -- it's
  # where you'd customize provider-wide behaviors (e.g. auto-deleting
  # resources inside a resource group when the group itself is destroyed).
  # We're not customizing anything yet, so it's left empty.
  features {}

  # Note: no `subscription_id`, `tenant_id`, or credentials are specified
  # here. When those are omitted, the azurerm provider automatically falls
  # back to whatever `az login` session is currently active in the Azure
  # CLI (the same one we used to run `az account show`). That's convenient
  # for local learning/dev; a real production setup would instead pin an
  # explicit `subscription_id` and authenticate via a service principal or
  # managed identity, not an interactively-logged-in human user.
}
