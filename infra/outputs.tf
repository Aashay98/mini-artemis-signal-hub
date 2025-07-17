output "alb_dns_name" {
  value = aws_lb.app.dns_name
  description = "Application Load Balancer DNS"
}
output "db_endpoint" {
  value = module.db.db_instance_endpoint
}
output "redis_endpoint" {
  value = module.redis.primary_endpoint_address
}
