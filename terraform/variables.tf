# ==============================================================================
# variables.tf
#
# This file declares INPUT VARIABLES -- named, typed, optionally-defaulted
# "slots" that other .tf files (mainly main.tf) can reference instead of
# hardcoding values directly. This is the Terraform equivalent of the shell
# variables AWS.md exported with `export VPC_ID=$(...)` -- except here the
# "variables" are declared up front with a type and a default, rather than
# captured as the output of a command that already ran.
#
# Why bother, instead of just typing "10.0.0.0/16" directly into main.tf?
#   - One place to change a value that might be reused in multiple resources.
#   - Can be overridden per-environment (e.g. a "dev" and a "prod" version of
#     this same config) without editing the resource definitions themselves.
#   - Self-documents what's actually configurable about this project.
# ==============================================================================

# Which Azure region to create every resource in.
# "eastus" is one of Azure's original, generally cheapest/most-available
# regions -- a safe default for a learning project.
variable "location" {
  type    = string
  default = "eastus"
}

# A short name used as a prefix/suffix when naming every resource
# (e.g. "rg-mlops", "vnet-mlops") so resource names stay consistent and
# recognizable as belonging to this project.
variable "project_name" {
  type    = string
  default = "mlops"
}

# The CIDR block (address range) for the VNet itself.
# "10.0.0.0/16" = addresses 10.0.0.0 through 10.0.255.255 (65,536 addresses).
# This is the Azure equivalent of AWS.md's `aws ec2 create-vpc --cidr-block
# 10.0.0.0/16`. See the CIDR explanation we covered earlier in this project's
# tutoring notes for why "/16" means that specific range.
variable "vnet_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

# The CIDR block for the first subnet, carved out of the VNet's range above.
# "10.0.1.0/24" = 10.0.1.0 through 10.0.1.255 (256 addresses) -- correctly a
# SUBSET of 10.0.0.0/16 (unlike the AWS.md notes, which used 10.10.x.x
# subnets under a 10.0.0.0/16 VPC -- an inconsistency we caught earlier;
# Azure would reject this the same way AWS would).
variable "subnet_1_cidr" {
  type    = string
  default = "10.0.1.0/24"
}

# The second subnet's CIDR block -- a different, non-overlapping slice of
# the same VNet range, mirroring AWS.md's two-subnets-for-availability
# pattern (though see the note in main.tf about how Azure's AZ story differs
# from AWS's here).
variable "subnet_2_cidr" {
  type    = string
  default = "10.0.2.0/24"
}
