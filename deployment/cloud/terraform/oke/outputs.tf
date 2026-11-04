output "cluster_id" {
  value = oci_containerengine_cluster.atlas.id
}
output "private_endpoint_ip" {
  value     = oci_containerengine_cluster.atlas.endpoints[0].private_endpoint
  sensitive = true
}
