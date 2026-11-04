variable "subscription_id" { type = string }
variable "tenant_id" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "cluster_name" { type = string }
variable "dns_prefix" { type = string }
variable "private_subnet_id" {
  type        = string
  description = "Existing private node subnet with controlled outbound routing."
}
variable "private_dns_zone_id" {
  type        = string
  description = "Owner-approved AKS private DNS zone, linked to the runner VNet."
}
variable "cluster_identity_id" {
  type        = string
  description = "Pre-created user-assigned control-plane identity with minimum required network permissions."
}
variable "kubelet_identity_client_id" { type = string }
variable "kubelet_identity_object_id" { type = string }
variable "kubelet_identity_resource_id" { type = string }
variable "kubernetes_version" {
  type        = string
  description = "Approved supported AKS version."
}
variable "vm_size" {
  type    = string
  default = "Standard_D2s_v5"
}
variable "node_count" {
  type    = number
  default = 2
  validation {
    condition     = var.node_count >= 2 && var.node_count <= 10
    error_message = "Use 2-10 nodes after checking approved budget and quotas."
  }
}
variable "service_cidr" {
  type    = string
  default = "10.96.0.0/16"
}
variable "dns_service_ip" {
  type    = string
  default = "10.96.0.10"
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
