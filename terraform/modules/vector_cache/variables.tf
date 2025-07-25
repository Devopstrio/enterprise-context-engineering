variable "environment" { type = string }
variable "redis_node_type" { type = string }
variable "redis_num_cache_nodes" { type = number }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "vpc_cidr" { type = string }
variable "tags" { type = map(string) }
