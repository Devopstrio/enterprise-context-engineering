# Production Readiness Checklist

This checklist must be fully verified and signed off before deploying the Context Engineering Platform to the `prod` environment.

## 1. Infrastructure Validation
- [ ] **DynamoDB Provisioned**: `context-memory-store` table exists in the target region.
- [ ] **DynamoDB Encryption**: KMS CMK encryption at rest is verified on the table.
- [ ] **Redis Provisioned**: ElastiCache Redis multi-AZ cluster is active and healthy.
- [ ] **Redis TLS**: In-transit encryption is enabled and enforced.
- [ ] **IAM Roles**: IRSA (IAM Roles for Service Accounts) is correctly mapped to the Kubernetes namespace and scoped to least privilege.

## 2. Application Configuration
- [ ] **Secrets Configured**: External Secrets Operator is successfully syncing from AWS Secrets Manager.
- [ ] **Environment Variables**: `LOG_LEVEL` is set to `INFO` or `WARN` (no `DEBUG` in prod).
- [ ] **Resource Limits**: CPU and Memory requests/limits are explicitly defined in the Kustomize overlay.
- [ ] **HPA Configured**: Horizontal Pod Autoscaler is enabled with appropriate min/max thresholds.

## 3. Observability & Monitoring
- [ ] **Health Endpoints**: `/health` endpoint is accessible and correctly reporting component status.
- [ ] **Metrics Exported**: Prometheus is scraping the platform's `/metrics` endpoint.
- [ ] **Logs Ingested**: Structlog JSON logs are successfully flowing into AWS CloudWatch `ContextAuditEvents`.
- [ ] **Dashboards Active**: Grafana dashboards for Context Assembly, Budgets, and Infrastructure are populated.

## 4. Alerting
- [ ] **High Latency Alert**: Configured for p95 Assembly Latency > 1500ms.
- [ ] **High Error Rate Alert**: Configured for 5xx errors > 1% over a 5-minute window.
- [ ] **Memory Throttling Alert**: Configured for DynamoDB Write/Read ProvisionedThroughputExceeded errors.
- [ ] **Cache Eviction Alert**: Configured for Redis aggressive LRU eviction spikes.

## 5. Resilience & DR
- [ ] **PITR Enabled**: DynamoDB Point-in-Time Recovery is verified as active.
- [ ] **Multi-AZ Verified**: Kubernetes deployment spans at least 3 availability zones.
- [ ] **DR Runbook Tested**: A simulated recovery exercise has been completed successfully within the last quarter.
- [ ] **Capacity Validated**: Load testing confirms the cluster can handle the expected peak of 500 TPS.

## 6. Security Review
- [ ] **Container Scanned**: Image vulnerability scan (e.g., Trivy or ECR Basic Scan) reports 0 Critical/High CVEs.
- [ ] **Rootless Container**: `securityContext` verifies `runAsNonRoot: true`.
- [ ] **Network Policies**: Calico policies strictly limit ingress/egress traffic.
- [ ] **Code Review**: All PRs merged to `main` have received two approving reviews from the core team.

**Sign-off:**
*   Platform Lead: _______________ (Date: ________)
*   Security Reviewer: _______________ (Date: ________)
