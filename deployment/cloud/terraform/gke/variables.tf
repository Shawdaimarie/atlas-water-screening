variable "project_id" { type = string }
variable "region" { type = string }
variable "cluster_name" { type = string }

variable "network" {
  type        = string
  description = "Existing VPC self-link; network and routes must be reviewed before apply."
}
variable "subnetwork" {
  type        = string
  description = "Existing private subnet self-link with approved secondary ranges."
}
variable "pods_range_name" { type = string }
variable "services_range_name" { type = string }

variable "master_ipv4_cidr_block" {
  type        = string
  description = "Dedicated non-overlapping /28 for the private control plane."
  validation {
    condition     = can(cidrnetmask(var.master_ipv4_cidr_block)) && tonumber(split("/", var.master_ipv4_cidr_block)[1]) == 28
    error_message = "GKE control-plane range must be a valid /28 CIDR."
  }
}
variable "node_service_account" {
  type        = string
  description = "Pre-created least-privilege node service account; do not use the default Compute Engine account."
}
variable "node_machine_type" {
  type    = string
  default = "e2-standard-2"
}
variable "node_count" {
  type    = number
  default = 2
  validation {
    condition     = var.node_count >= 2 && var.node_count <= 10
    error_message = "Use 2-10 nodes after checking approved budget and quotas."
  }
}
variable "labels" {
  type    = map(string)
  default = { application = "atlas", environment = "staging", managed_by = "terraform" }
}

variable "resource_creation_authorized" {
  type        = bool
  default     = false
  description = "Set true only after account, billing, budget, region, network, identity, and remote-state gates are approved."
}
