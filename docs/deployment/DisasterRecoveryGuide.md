# Disaster Recovery Guide

## 1. RTO and RPO Targets
*   **Recovery Time Objective (RTO)**: 1 Hour. This is the maximum acceptable time the Context Engineering platform can be offline before business impact becomes severe.
*   **Recovery Point Objective (RPO)**: 15 Minutes. This is the maximum acceptable data loss for conversation memory (DynamoDB).

## 2. DynamoDB Point-in-Time Recovery (PITR)
Conversation memory is the only persistent state in the platform.
*   **Configuration**: PITR is enabled by default via Terraform on the `context-memory-store` table.
*   **Capabilities**: Allows restoring the table to any second in the preceding 35 days.
*   **Recovery Procedure**:
    1.  Navigate to the DynamoDB AWS Console.
    2.  Select the `context-memory-store` table.
    3.  Choose the 'Backups' tab and select 'Restore to point-in-time'.
    4.  Specify the exact timestamp required.
    5.  Restore to a *new* table name (e.g., `context-memory-store-restored`).
    6.  Update the Kubernetes ConfigMap `DYNAMODB_TABLE_MEMORY` variable to point to the new table and trigger a rolling restart of the API pods.

## 3. Redis Replication and Failover
The ElastiCache Redis cluster operates primarily as an ephemeral cache, but rapid recovery is critical for performance.
*   **Configuration**: Deployed as a Multi-AZ cluster with 1 primary node and 2 read replicas.
*   **Failover**: If the primary node fails, ElastiCache automatically promotes a replica to primary. This process typically takes 1-3 minutes.
*   **Impact**: During failover, write operations (caching new contexts) may temporarily fail or experience high latency. The application will fall back to processing the context assembly pipeline fully, increasing CPU load on the Kubernetes pods. No manual intervention is required for this failover.

## 4. CloudWatch Log Retention
Audit logs are crucial for compliance and post-incident analysis.
*   **Retention Policy**: Logs are retained in CloudWatch for 90 days.
*   **Archival**: Logs older than 90 days are automatically exported to an S3 Glacier bucket for 7-year long-term retention.
*   **Recovery**: In the event of an audit query requirement for older data, initiate a Glacier restore process to access the necessary timeframes.

## 5. Recovery Runbooks (Cluster Loss)
If the entire primary Kubernetes cluster is lost:
1.  **Acknowledge Incident**: Declare a Sev-1 incident.
2.  **Deploy to Standby Cluster**: The platform relies on GitOps (Kustomize). Ensure the secondary cluster (e.g., in a different AWS region) is active.
3.  **Update DNS**: Modify the Route53 alias record for the API Gateway to point to the Ingress controller of the secondary cluster.
4.  **Verify State**: Ensure the secondary cluster can communicate with the cross-region replicated DynamoDB table (if configured for Global Tables) or the local standby table.
5.  **Post-Incident**: Perform a root cause analysis once the system is stable.
