variable "compartment_id" { type = string }
variable "region" { type = string }
variable "cluster_name" { type = string }
variable "vcn_id" { type = string }
variable "private_endpoint_subnet_id" {
  type        = string
  description = "Existing private control-plane endpoint subnet with runner route and DNS."
}
variable "private_endpoint_nsg_ids" {
  type        = list(string)
  description = "NSGs allowing only the approved private runner and required control-plane paths."
}
variable "private_node_subnet_ids_by_ad" {
  type        = map(string)
  description = "Availability-domain to private worker subnet map; each subnet must prohibit public IPs."
  validation {
    condition     = length(var.private_node_subnet_ids_by_ad) >= 2
    error_message = "Use private subnets in at least two availability domains."
  }
}
variable "kubernetes_version" {
  type        = string
  description = "Approved supported OKE version."
}
variable "node_shape" { type = string }
variable "node_image_id" {
  type        = string
  description = "Approved supported OKE worker image OCID."
}
variable "node_count" {
  type    = number
  default = 2
  validation {
    condition     = var.node_count >= 2 && var.node_count <= 10
    error_message = "Use 2-10 nodes after checking approved budget and quotas."
  }
}
variable "tags" {
  type    = map(string)
  default = { application = "ATLAS", environment = "staging", managed_by = "terraform" }
}

variable "resource_creation_authorized" {
  type        = bool
  default     = false
  description = "Set true only after account, billing, budget, region, network, identity, and remote-state gates are approved."
}
