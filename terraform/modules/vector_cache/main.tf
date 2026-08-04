resource "aws_elasticache_subnet_group" "this" {
  name       = "context-cache-subnet-group-${var.environment}"
  subnet_ids = var.subnet_ids
  tags       = var.tags
}

resource "aws_security_group" "this" {
  name        = "context-cache-sg-${var.environment}"
  description = "Security group for Context Cache Redis"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id       = "context-cache-${var.environment}"
  description                = "Context Cache for Enterprise Context Engineering"
  node_type                  = var.redis_node_type
  num_cache_clusters         = var.redis_num_cache_nodes
  engine                     = "redis"
  engine_version             = "7.0"
  port                       = 6379
  subnet_group_name          = aws_elasticache_subnet_group.this.name
  security_group_ids         = [aws_security_group.this.id]
  automatic_failover_enabled = var.redis_num_cache_nodes > 1 ? true : false
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true

  tags = var.tags
}
