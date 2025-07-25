module "network" {
  source               = "./modules/network"
  environment          = var.environment
  aws_region           = var.aws_region
  vpc_cidr             = var.vpc_cidr
  private_subnet_cidrs = var.private_subnet_cidrs
  tags                 = var.tags
}

module "context_store" {
  source                   = "./modules/context_store"
  environment              = var.environment
  dynamodb_billing_mode    = var.dynamodb_billing_mode
  dynamodb_read_capacity   = var.dynamodb_read_capacity
  dynamodb_write_capacity  = var.dynamodb_write_capacity
  tags                     = var.tags
}

module "vector_cache" {
  source                = "./modules/vector_cache"
  environment           = var.environment
  redis_node_type       = var.redis_node_type
  redis_num_cache_nodes = var.redis_num_cache_nodes
  vpc_id                = module.network.vpc_id
  subnet_ids            = module.network.private_subnet_ids
  vpc_cidr              = var.vpc_cidr
  tags                  = var.tags
}

module "audit_logs" {
  source             = "./modules/audit_logs"
  environment        = var.environment
  log_retention_days = var.log_retention_days
  tags               = var.tags
}
