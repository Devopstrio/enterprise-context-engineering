# Operational Runbook

## 1. Service Start/Stop Procedures
The Context Engineering Platform operates as a stateless deployment in Kubernetes.
*   **To gracefully restart the service:**
    `kubectl rollout restart deployment context-engineering-api -n context-platform`
*   **To halt the service (scale to zero):**
    `kubectl scale deployment context-engineering-api --replicas=0 -n context-platform`
*   **To resume the service:**
    `kubectl scale deployment context-engineering-api --replicas=3 -n context-platform`

## 2. Health Check Verification
To manually verify the health of the application and its dependencies:
1.  Port-forward to a specific pod:
    `kubectl port-forward svc/context-engineering-api 8080:80 -n context-platform`
2.  Execute the check:
    `curl -s http://localhost:8080/health | jq`
3.  Expected output must show `"status": "healthy"` for all components (redis, dynamodb, memory_manager).

## 3. Memory Store Maintenance (DynamoDB)
DynamoDB largely manages itself, but occasional intervention may be required.
*   **Clear a corrupted session:**
    If a specific `session_id` is causing crashes, manually delete it via AWS CLI:
    `aws dynamodb delete-item --table-name context-memory-store --key '{"session_id": {"S": "<UUID>"}}'`
*   **Verify TTL operations:**
    Ensure old data is expiring by querying the `expires_at` attribute and comparing it to the current epoch time.

## 4. Cache Flush Procedures
If prompt templates are updated globally or if the cache is poisoned, a manual flush may be necessary.
*   **Flush Entire Context Cache:**
    1.  Connect to the Redis primary node using `redis-cli`.
    2.  Execute: `FLUSHDB` (Note: Ensure you are connected to the correct database index used by the context platform).
*   **Invalidate a specific cache key:**
    Execute: `DEL <request_hash_key>`

## 5. Log Analysis Queries
We use structured JSON logging. Use CloudWatch Logs Insights to query the `ContextAuditEvents` log group.
*   **Find high compression events (potential quality loss):**
    ```sql
    fields @timestamp, session_id, allocation_metadata.compression_ratio
    | filter allocation_metadata.compression_ratio < 0.5
    | sort @timestamp desc
    | limit 50
    ```
*   **Identify token budget overflows:**
    ```sql
    fields @timestamp, session_id, error.message
    | filter event = "budget_overflow_error"
    ```

## 6. Incident Response: Context Assembly Failures
If the `POST /api/v1/context/assemble` endpoint experiences elevated 5xx errors:
1.  **Check HPA**: Is the cluster starved for resources? (`kubectl get hpa -n context-platform`).
2.  **Check Dependency Health**: View the `/health` endpoint. If DynamoDB or Redis is degraded, investigate AWS service health.
3.  **Review Audit Logs**: Look for specific error types in CloudWatch. Are failures tied to specific prompt templates or unusually large RAG payloads?
4.  **Mitigation**: If a specific template is failing, rollback the template version via the API: `PUT /api/v1/templates/{id}/rollback`.
