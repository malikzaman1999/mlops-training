# ==============================================================================
# main.tf
#
# This is the actual infrastructure definition -- every `resource` block here
# describes ONE real Azure object Terraform should create/manage.
#
# This file mirrors AWS.md's VPC build 1:1 (see the "AWS -> Azure translation"
# table appended to the end of that file):
#   VPC                        -> azurerm_virtual_network
#   2 subnets                  -> 2x azurerm_subnet
#   Security Group (22, 80)    -> azurerm_network_security_group
#
# General syntax reminder for every block below:
#   resource "<TYPE>" "<LOCAL NAME>" { argument = value ... }
# - <TYPE> (e.g. "azurerm_virtual_network") is fixed by the provider -- it's
#   the specific kind of Azure object being created. You can't invent your
#   own; it has to match a resource type the azurerm provider documents.
# - <LOCAL NAME> (e.g. "main") is something YOU choose -- it's how other
#   blocks in this same Terraform project refer back to this resource
#   (e.g. `azurerm_resource_group.main.name` below reads: "the `name`
#   attribute of the azurerm_resource_group resource I locally called
#   `main`"). It's never sent to Azure; it only exists inside Terraform.
# ==============================================================================

# ------------------------------------------------------------------------
# RESOURCE GROUP
# Azure-specific concept with no AWS equivalent: a logical folder that every
# other resource below must live inside. Deleting this resource group later
# deletes everything inside it in one shot -- convenient for tearing down
# this whole learning project cleanly.
# ------------------------------------------------------------------------
resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}" # "rg-mlops" -- string interpolation of the variable declared in variables.tf
  location = var.location             # "eastus" by default, from variables.tf
}

# ------------------------------------------------------------------------
# VIRTUAL NETWORK (the VPC equivalent)
# Corresponds to AWS.md's:
#   aws ec2 create-vpc --cidr-block 10.0.0.0/16
# ------------------------------------------------------------------------
resource "azurerm_virtual_network" "main" {
  name          = "vnet-${var.project_name}" # "vnet-mlops"
  address_space = [var.vnet_cidr]            # a LIST containing one CIDR block: ["10.0.0.0/16"]
  # (a list, because Azure VNets can technically have more
  # than one address space -- we only need one here)

  # These two lines are a common Terraform pattern: instead of hardcoding
  # "eastus" and "rg-mlops" again, we REFERENCE the resource group resource
  # defined above. This creates an explicit DEPENDENCY: Terraform now knows
  # it must create azurerm_resource_group.main successfully BEFORE it
  # attempts to create this VNet, because this VNet needs the resource
  # group's real name/location to exist first. You never have to declare
  # dependency order manually like the AWS.md CLI script did with its
  # `export X_ID=...` chaining -- Terraform infers it automatically from
  # these references.
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

# ------------------------------------------------------------------------
# SUBNET 1
# Corresponds to AWS.md's:
#   aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.10.1.24/24 ...
# Note our subnet_1_cidr (10.0.1.0/24) is correctly INSIDE the VNet's
# 10.0.0.0/16 range -- Azure enforces this the same way AWS does; a subnet
# CIDR that falls outside its parent VNet's range is rejected at apply time.
# ------------------------------------------------------------------------
resource "azurerm_subnet" "app_1" {
  name                 = "snet-app-1"
  resource_group_name  = azurerm_resource_group.main.name  # which resource group this subnet's parent VNet lives in
  virtual_network_name = azurerm_virtual_network.main.name # which VNet this subnet belongs to
  address_prefixes     = [var.subnet_1_cidr]               # ["10.0.1.0/24"]
}

# ------------------------------------------------------------------------
# SUBNET 2
# The second subnet, mirroring AWS.md's two-subnets pattern.
#
# IMPORTANT DIFFERENCE FROM AWS: in AWS.md, the two subnets were explicitly
# placed in two different Availability Zones (us-east-1a / us-east-1b) as
# part of the create-subnet call itself, because ALBs require that for high
# availability. In Azure, a subnet is just an address range within a
# region -- it is NOT pinned to a specific Availability Zone. Zone
# redundancy in Azure is instead a property of the COMPUTE you place inside
# the subnet (e.g. telling an AKS node pool or a VM Scale Set to spread its
# instances across zones 1/2/3). So this subnet, by itself, doesn't yet give
# us the AZ-spread AWS.md got for free from its two-AZ subnet layout -- we'll
# configure that when we get to AKS.
# ------------------------------------------------------------------------
resource "azurerm_subnet" "app_2" {
  name                 = "snet-app-2"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_2_cidr] # ["10.0.2.0/24"]
}

# ------------------------------------------------------------------------
# NETWORK SECURITY GROUP (the Security Group equivalent)
# Corresponds to AWS.md's:
#   aws ec2 create-security-group --description "allow app and ssh" ...
#   aws ec2 authorize-security-group-ingress --port 80 --cidr 0.0.0.0/0 ...
#   aws ec2 authorize-security-group-ingress --port 22 --cidr 0.0.0.0/0 ...
# One NSG resource can hold multiple rules -- each `security_rule` block
# below is the Azure equivalent of one `authorize-security-group-ingress`
# call in AWS.md.
# ------------------------------------------------------------------------
resource "azurerm_network_security_group" "app" {
  name                = "nsg-app"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # Rule: allow inbound HTTP (port 80) from anywhere.
  security_rule {
    name     = "allow-http" # a human-readable rule name, shown in the Azure portal
    priority = 100          # LOWER number = evaluated FIRST. Rules are checked in priority
    # order and the first matching rule wins -- this is why the two
    # rules here have different priorities (100 and 110); if they
    # ever conflicted, the lower number's rule would apply.
    direction = "Inbound" # this rule governs traffic COMING IN to the subnet, not going out
    access    = "Allow"   # the alternative would be "Deny" -- explicitly blocking traffic
    # even if a lower-priority rule would otherwise allow it
    protocol = "Tcp" # HTTP rides on top of TCP

    source_port_range = "*" # the CLIENT's port can be anything (this is normal --
    # clients use a random high-numbered port, only the
    # SERVER's port, i.e. destination, is fixed at 80)
    destination_port_range = "80" # the port ON THE VM this rule opens

    source_address_prefix = "*" # "*" here means "any source IP" -- the Azure NSG
    # equivalent of AWS's "0.0.0.0/0" in
    # authorize-security-group-ingress
    destination_address_prefix = "*" # applies regardless of which internal IP is the target
  }

  # Rule: allow inbound SSH (port 22) from anywhere -- for admin/troubleshooting
  # access to VMs, exactly like AWS.md's second authorize-security-group-ingress
  # call. (Once we move to AKS, we generally won't SSH into individual nodes
  # this way -- this rule exists here purely to mirror AWS.md's exercise
  # 1:1; we'll tighten/remove it in a later phase.)
  security_rule {
    name     = "allow-ssh"
    priority = 110 # must be a DIFFERENT number from the rule above --
    # Azure requires unique priorities per NSG
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# ------------------------------------------------------------------------
# NSG <-> SUBNET ASSOCIATIONS
# In AWS, a Security Group is attached directly to an EC2 instance (or its
# network interface) at launch time -- there's no separate "attach this SG
# to this subnet" step in AWS.md. Azure instead lets you attach an NSG at
# EITHER the subnet level (applies to everything inside it) OR the
# individual network-interface level. We're attaching at the subnet level
# here -- simpler for a learning project, and it means every VM/pod that
# ever lands in these subnets automatically inherits these rules without
# needing per-resource configuration.
#
# This has to be a SEPARATE resource block (not just an argument inside
# azurerm_subnet) because, structurally, Azure models the association
# itself as its own linkable object.
# ------------------------------------------------------------------------
resource "azurerm_subnet_network_security_group_association" "app_1" {
  subnet_id                 = azurerm_subnet.app_1.id               # link to subnet 1 (by its real Azure ID, not our local name)
  network_security_group_id = azurerm_network_security_group.app.id # link to the NSG defined above
}

resource "azurerm_subnet_network_security_group_association" "app_2" {
  subnet_id                 = azurerm_subnet.app_2.id
  network_security_group_id = azurerm_network_security_group.app.id
}
