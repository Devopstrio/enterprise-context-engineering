resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/context-engineering/audit/${var.environment}"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_cloudwatch_log_metric_filter" "context_assembly" {
  name           = "ContextAssemblyEvent"
  pattern        = "{ $.event = \"context_assembly\" }"
  log_group_name = aws_cloudwatch_log_group.this.name

  metric_transformation {
    name      = "ContextAssemblyCount"
    namespace = "ContextEngineering"
    value     = "1"
  }
}
