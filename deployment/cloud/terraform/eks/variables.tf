variable "region" { type = string }
variable "cluster_name" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" {
  type        = list(string)
  description = "At least two private subnets in distinct AZs."
  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "EKS requires at least two private subnet IDs."
  }
}
variable "cluster_role_arn" {
  type        = string
  description = "Pre-created EKS control-plane IAM role, scoped to this cluster."
}
variable "node_role_arn" {
  type        = string
  description = "Pre-created node role with only required worker and image-pull permissions."
}
variable "kms_key_arn" {
  type        = string
  description = "Customer-managed KMS key for Kubernetes secret encryption."
}
variable "kubernetes_version" {
  type        = string
  description = "Approved supported EKS version."
}
variable "instance_types" {
  type    = list(string)
  default = ["t3.large"]
}
variable "desired_size" {
  type    = number
  default = 2
  validation {
    condition     = var.desired_size >= 2 && var.desired_size <= 10
    error_message = "Use 2-10 nodes after checking approved budget and quotas."
  }
}
variable "tags" {
  type    = map(string)
  default = { Application = "ATLAS", Environment = "staging", ManagedBy = "Terraform" }
}

variable "resource_creation_authorized" {
  type        = bool
  default     = false
  description = "Set true only after account, billing, budget, region, network, identity, and remote-state gates are approved."
}

variable "release_operator_role_arn" {
  type        = string
  description = "GitHub OIDC-backed deploy role; mapped only to the atlas-deployers Kubernetes group."
}
