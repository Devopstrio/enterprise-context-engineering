# Security Hardening Guide

## 1. Network Security and Encryption
*   **TLS for Redis Connections**: All communication with ElastiCache Redis must enforce TLS encryption in transit. Ensure the `REDIS_TLS_ENABLED` environment variable is set to `true` and the appropriate certificates are loaded into the pod trust store.
*   **DynamoDB Encryption**: The `context-memory-store` table must have encryption at rest enabled using an AWS KMS Customer Managed Key (CMK), not the default AWS-owned key.
*   **API Gateway TLS**: Termination of external client traffic must occur at the Ingress controller using TLS 1.2 or higher.

## 2. Identity and Access Management (IAM)
*   **Principle of Least Privilege**: The Kubernetes pods run under a dedicated IAM Service Account (IRSA).
*   **DynamoDB Permissions**: The role must only have `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:Query`, and `dynamodb:DeleteItem` permissions specifically bounded to the `context-memory-store` table ARN.
*   **CloudWatch Permissions**: The role must only have `logs:CreateLogStream` and `logs:PutLogEvents` bounded to the specific audit log group ARN.

## 3. Network Policies (Kubernetes)
Isolate the platform within the cluster using Calico Network Policies:
*   **Ingress**: Allow traffic only from the designated API Gateway namespace on port 80/443. Deny all other internal cluster traffic.
*   **Egress**: Deny all outbound traffic by default. Explicitly allow egress to AWS API endpoints (DynamoDB, CloudWatch) and the specific internal IP address of the Redis cluster.

## 4. Secret Management
*   **No Hardcoded Secrets**: Credentials, API keys (if applicable for downstream integrations), and TLS certificates must never be stored in the repository or hardcoded in configuration files.
*   **External Secrets Operator**: Use the Kubernetes External Secrets Operator to synchronize credentials from AWS Secrets Manager directly into Kubernetes Secrets mounted as tmpfs volumes.

## 5. Container Security
*   **Non-Root Execution**: The Docker container must run as a non-root user. Enforce this via the Kubernetes `securityContext` by setting `runAsNonRoot: true` and specifying a `runAsUser` ID (e.g., 1000).
*   **Read-Only Root Filesystem**: The container must operate with a read-only root filesystem to prevent runtime tampering. Set `readOnlyRootFilesystem: true` in the deployment definition. Any required temporary storage must use explicitly mounted `emptyDir` volumes.

## 6. Role-Based Access Control (RBAC)
*   **Cluster Roles**: Limit access to the `context-platform` namespace. Developers should have `view` access; CI/CD service accounts should have `edit` access.
*   **API Authentication**: All requests to the `/api/v1/context/*` endpoints must require a valid JWT token validated by the upstream API Gateway before reaching the context platform pods.
