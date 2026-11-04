output "cluster_name" {
  value = google_container_cluster.atlas.name
}
output "private_endpoint" {
  value     = google_container_cluster.atlas.private_cluster_config[0].private_endpoint
  sensitive = true
}
output "workload_identity_pool" {
  value = google_container_cluster.atlas.workload_identity_config[0].workload_pool
}
