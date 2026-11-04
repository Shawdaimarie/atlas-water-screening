resource "terraform_data" "resource_guard" {
  input = var.resource_creation_authorized
  lifecycle {
    precondition {
      condition     = var.resource_creation_authorized
      error_message = "Cloud resource creation is disabled until the owner explicitly approves all onboarding and remote-state gates."
    }
  }
}

resource "google_container_cluster" "atlas" {
  depends_on               = [terraform_data.resource_guard]
  name                     = var.cluster_name
  location                 = var.region
  network                  = var.network
  subnetwork               = var.subnetwork
  deletion_protection      = true
  remove_default_node_pool = true
  initial_node_count       = 1
  networking_mode          = "VPC_NATIVE"
  datapath_provider        = "ADVANCED_DATAPATH"
  resource_labels          = var.labels

  release_channel {
    channel = "REGULAR"
  }
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_range_name
    services_secondary_range_name = var.services_range_name
  }
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = true
    master_ipv4_cidr_block  = var.master_ipv4_cidr_block
    master_global_access_config {
      enabled = false
    }
  }
  master_authorized_networks_config {
    gcp_public_cidrs_access_enabled = false
  }
  network_policy {
    enabled  = true
    provider = "CALICO"
  }
  addons_config {
    network_policy_config {
      disabled = false
    }
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }
  }
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS", "APISERVER", "CONTROLLER_MANAGER", "SCHEDULER"]
  }
  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
  }
  maintenance_policy {
    recurring_window {
      start_time = "2026-01-04T04:00:00Z"
      end_time   = "2026-01-04T08:00:00Z"
      recurrence = "FREQ=WEEKLY;BYDAY=SU"
    }
  }
}

resource "google_container_node_pool" "atlas" {
  name       = "atlas-private"
  location   = var.region
  cluster    = google_container_cluster.atlas.name
  node_count = var.node_count
  node_config {
    machine_type    = var.node_machine_type
    service_account = var.node_service_account
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    tags            = ["atlas-private-node"]
    labels          = var.labels
    metadata = {
      disable-legacy-endpoints = "true"
    }
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }
  management {
    auto_repair  = true
    auto_upgrade = true
  }
  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}
