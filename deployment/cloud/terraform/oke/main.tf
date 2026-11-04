resource "terraform_data" "resource_guard" {
  input = var.resource_creation_authorized
  lifecycle {
    precondition {
      condition     = var.resource_creation_authorized
      error_message = "Cloud resource creation is disabled until the owner explicitly approves all onboarding and remote-state gates."
    }
  }
}

resource "oci_containerengine_cluster" "atlas" {
  depends_on         = [terraform_data.resource_guard]
  compartment_id     = var.compartment_id
  kubernetes_version = var.kubernetes_version
  name               = var.cluster_name
  vcn_id             = var.vcn_id
  type               = "ENHANCED"
  freeform_tags      = var.tags

  endpoint_config {
    subnet_id            = var.private_endpoint_subnet_id
    is_public_ip_enabled = false
    nsg_ids              = var.private_endpoint_nsg_ids
  }
  cluster_pod_network_options {
    cni_type = "FLANNEL_OVERLAY"
  }
}

resource "oci_containerengine_node_pool" "atlas" {
  compartment_id     = var.compartment_id
  cluster_id         = oci_containerengine_cluster.atlas.id
  name               = "atlas-private"
  kubernetes_version = var.kubernetes_version
  node_shape         = var.node_shape
  freeform_tags      = var.tags

  node_config_details {
    size = var.node_count
    dynamic "placement_configs" {
      for_each = var.private_node_subnet_ids_by_ad
      content {
        availability_domain = placement_configs.key
        subnet_id           = placement_configs.value
      }
    }
    node_pool_pod_network_option_details {
      cni_type = "FLANNEL_OVERLAY"
    }
    is_pv_encryption_in_transit_enabled = true
  }
  node_source_details {
    image_id    = var.node_image_id
    source_type = "IMAGE"
  }
  initial_node_labels {
    key   = "app.kubernetes.io/part-of"
    value = "atlas"
  }
}
