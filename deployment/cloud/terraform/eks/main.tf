resource "terraform_data" "resource_guard" {
  input = var.resource_creation_authorized
  lifecycle {
    precondition {
      condition     = var.resource_creation_authorized
      error_message = "Cloud resource creation is disabled until the owner explicitly approves all onboarding and remote-state gates."
    }
  }
}

data "aws_vpc" "atlas" {
  id = var.vpc_id
}
data "aws_subnet" "private" {
  for_each = toset(var.private_subnet_ids)
  id       = each.value
}

resource "aws_eks_cluster" "atlas" {
  depends_on                = [terraform_data.resource_guard]
  name                      = var.cluster_name
  role_arn                  = var.cluster_role_arn
  version                   = var.kubernetes_version
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  tags                      = var.tags
  vpc_config {
    subnet_ids              = var.private_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = false
  }
  encryption_config {
    provider {
      key_arn = var.kms_key_arn
    }
    resources = ["secrets"]
  }
  access_config {
    authentication_mode                         = "API"
    bootstrap_cluster_creator_admin_permissions = false
  }
  lifecycle {
    precondition {
      condition = alltrue([
        for subnet in data.aws_subnet.private :
        subnet.vpc_id == data.aws_vpc.atlas.id && !subnet.map_public_ip_on_launch
      ])
      error_message = "All EKS subnets must belong to the supplied VPC and not auto-assign public IPv4 addresses."
    }
  }
}

resource "aws_launch_template" "atlas_nodes" {
  name_prefix            = "${var.cluster_name}-nodes-"
  update_default_version = true
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "disabled"
  }
  network_interfaces {
    associate_public_ip_address = false
  }
  tag_specifications {
    resource_type = "instance"
    tags          = var.tags
  }
}

resource "aws_eks_node_group" "atlas" {
  cluster_name    = aws_eks_cluster.atlas.name
  node_group_name = "atlas-private"
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.private_subnet_ids
  instance_types  = var.instance_types
  ami_type        = "AL2023_x86_64_STANDARD"
  capacity_type   = "ON_DEMAND"
  launch_template {
    id      = aws_launch_template.atlas_nodes.id
    version = aws_launch_template.atlas_nodes.latest_version
  }
  scaling_config {
    desired_size = var.desired_size
    min_size     = 2
    max_size     = 10
  }
  update_config {
    max_unavailable = 1
  }
  tags = var.tags
}

resource "aws_eks_access_entry" "release_operator" {
  cluster_name      = aws_eks_cluster.atlas.name
  principal_arn     = var.release_operator_role_arn
  type              = "STANDARD"
  kubernetes_groups = ["atlas-deployers"]
}
