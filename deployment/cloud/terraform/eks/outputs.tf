output "cluster_name" {
  value = aws_eks_cluster.atlas.name
}
output "cluster_endpoint" {
  value     = aws_eks_cluster.atlas.endpoint
  sensitive = true
}
output "cluster_certificate_authority_data" {
  value     = aws_eks_cluster.atlas.certificate_authority[0].data
  sensitive = true
}
