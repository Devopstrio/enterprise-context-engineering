output "dynamodb_table_name" { value = module.context_store.table_name }
output "dynamodb_table_arn" { value = module.context_store.table_arn }
output "redis_endpoint" { value = module.vector_cache.endpoint }
output "redis_port" { value = module.vector_cache.port }
output "cloudwatch_log_group_name" { value = module.audit_logs.log_group_name }
output "vpc_id" { value = module.network.vpc_id }
output "private_subnet_ids" { value = module.network.private_subnet_ids }
