variable "environment" { type = string }
variable "dynamodb_billing_mode" { type = string }
variable "dynamodb_read_capacity" { type = number }
variable "dynamodb_write_capacity" { type = number }
variable "tags" { type = map(string) }
