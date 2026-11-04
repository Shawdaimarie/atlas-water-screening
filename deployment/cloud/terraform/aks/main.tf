resource "terraform_data" "resource_guard" {
  input = var.resource_creation_authorized
  lifecycle {
    precondition {
      condition     = var.resource_creation_authorized
      error_message = "Cloud resource creation is disabled until the owner explicitly approves all onboarding and remote-state gates."
    }
  }
}

resource "azurerm_kubernetes_cluster" "atlas" {
  depends_on                          = [terraform_data.resource_guard]
  name                                = var.cluster_name
  location                            = var.location
  resource_group_name                 = var.resource_group_name
  dns_prefix                          = var.dns_prefix
  kubernetes_version                  = var.kubernetes_version
  sku_tier                            = "Standard"
  private_cluster_enabled             = true
  private_dns_zone_id                 = var.private_dns_zone_id
  private_cluster_public_fqdn_enabled = false
  local_account_disabled              = true
  oidc_issuer_enabled                 = true
  workload_identity_enabled           = true
  azure_policy_enabled                = true
  image_cleaner_enabled               = true
  image_cleaner_interval_hours        = 48
  role_based_access_control_enabled   = true
  tags                                = var.tags

  identity {
    type         = "UserAssigned"
    identity_ids = [var.cluster_identity_id]
  }
  kubelet_identity {
    client_id                 = var.kubelet_identity_client_id
    object_id                 = var.kubelet_identity_object_id
    user_assigned_identity_id = var.kubelet_identity_resource_id
  }
  azure_active_directory_role_based_access_control {
    tenant_id          = var.tenant_id
    azure_rbac_enabled = true
  }
  default_node_pool {
    name                         = "atlas"
    vm_size                      = var.vm_size
    node_count                   = var.node_count
    vnet_subnet_id               = var.private_subnet_id
    type                         = "VirtualMachineScaleSets"
    auto_scaling_enabled         = true
    min_count                    = 2
    max_count                    = 10
    only_critical_addons_enabled = true
    os_disk_type                 = "Ephemeral"
    upgrade_settings {
      max_surge = "33%"
    }
    temporary_name_for_rotation = "atlasrot"
  }
  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
    network_policy      = "azure"
    outbound_type       = "userDefinedRouting"
    load_balancer_sku   = "standard"
    service_cidr        = var.service_cidr
    dns_service_ip      = var.dns_service_ip
  }
  lifecycle {
    precondition {
      condition     = var.dns_service_ip == cidrhost(var.service_cidr, 10)
      error_message = "dns_service_ip must be the tenth address in the non-overlapping service_cidr."
    }
  }
}
