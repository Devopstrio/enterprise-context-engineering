# Support Handover Guide

## 1. Team Contacts
The Context Engineering Platform is maintained by the AI Infrastructure team.
*   **Primary Slack Channel**: `#ai-infra-support`
*   **Escalation PagerDuty Service**: `context-engineering-critical`
*   **Platform Lead**: engineering-lead@example.com
*   **Product Manager**: pm-ai@example.com

## 2. Escalation Matrix
Follow this path for unresolved issues:
1.  **L1 Support (NOC)**: Initial triage, monitor dashboards, execute basic runbook commands (restarts, cache flushes).
2.  **L2 Support (On-Call Engineer)**: Deep dive into logs, debug specific `session_id` failures, manage infrastructure issues (Redis/DynamoDB).
3.  **L3 Support (Platform Dev Team)**: Architectural issues, compression algorithm bugs, complex token allocation logic failures.

## 3. Monitoring Dashboards
Access the primary Grafana dashboards via the internal portal:
*   **Context Assembly Overview**: Displays high-level metrics: Assembly Latency (p50, p95, p99), Request Volume, Error Rates.
*   **Token Budget Utilization**: Visualizes how budgets are allocated across System, Memory, and RAG components. Look here to see if RAG is starving the User Prompt.
*   **Infrastructure Health**: Monitors Redis hit rates, DynamoDB read/write capacity consumption, and Kubernetes pod resource utilization.

## 4. Common Issues and Resolutions

### Issue: "Context Window Exceeded" errors from upstream clients.
*   **Symptom**: Clients report 400 errors indicating the assembled context is too large.
*   **Probable Cause**: The `TokenBudgetOptimizer` is misconfigured for the target model, or the `ContextCompressor` is failing to aggressively reduce RAG data.
*   **Resolution**: Check the specific LLM model profile configuration in the database. Ensure the `max_tokens` setting matches the provider's limits.

### Issue: High Assembly Latency (> 1000ms)
*   **Symptom**: API response times spike, causing downstream client timeouts.
*   **Probable Cause**: Cache hit rate has dropped significantly, forcing full pipeline re-assembly. Alternatively, CPU starvation on the cluster.
*   **Resolution**: Check the Redis Cache hit rate dashboard. If low, investigate if client applications are generating non-deterministic prompt inputs that defeat caching. Check HPA metrics to see if scaling is required.

## 5. On-Call Procedures
When receiving a PagerDuty alert:
1.  **Acknowledge** the alert within 5 minutes.
2.  **Join the incident bridge** if it is a Sev-1 or Sev-2.
3.  **Review the runbook** linked directly in the alert description.
4.  **Post updates** to the `#ai-infra-incidents` Slack channel every 30 minutes during active mitigation.
5.  **Complete a Post-Incident Report (PIR)** within 48 hours for any Sev-1/Sev-2 event.
