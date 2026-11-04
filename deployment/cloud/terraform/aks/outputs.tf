output "cluster_name" {
  value = azurerm_kubernetes_cluster.atlas.name
}
output "private_fqdn" {
  value     = azurerm_kubernetes_cluster.atlas.private_fqdn
  sensitive = true
}
output "oidc_issuer_url" {
  value = azurerm_kubernetes_cluster.atlas.oidc_issuer_url
}
