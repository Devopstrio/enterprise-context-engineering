variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "project_name" {
  type    = string
  default = "context-engineering"
}

variable "vpc_cidr" {
  type = string
}

variable "private_subnet_cidrs" {
  type = list(string)
}

variable "dynamodb_billing_mode" {
  type = string
}

variable "dynamodb_read_capacity" {
  type = number
}

variable "dynamodb_write_capacity" {
  type = number
}

variable "redis_node_type" {
  type = string
}

variable "redis_num_cache_nodes" {
  type = number
}

variable "log_retention_days" {
  type = number
}

variable "tags" {
  type = map(string)
}
