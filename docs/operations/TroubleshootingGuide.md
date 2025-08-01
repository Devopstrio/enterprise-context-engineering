# Troubleshooting Guide

## 1. Context Assembly Timeouts
*   **Symptom**: The `/api/v1/context/assemble` endpoint returns 504 Gateway Timeout or takes longer than the configured client SLA (e.g., 2000ms).
*   **Diagnosis**:
    *   Check the Cache Hit Rate. A sudden drop means all requests are falling through to the compute-heavy assembly pipeline.
    *   Review `ContextCompressor` metrics. Extremely large RAG payloads require significant CPU time to compress using TF-IDF.
*   **Resolution**: Increase the `maxSurge` in HPA to scale pods faster. If caused by RAG payloads, implement a hard limit on inbound RAG document size before compression begins.

## 2. Memory Retrieval Failures
*   **Symptom**: The assembled context is missing historical conversation turns, making the LLM "forgetful."
*   **Diagnosis**:
    *   Query DynamoDB for the specific `session_id`. Check if the items exist and if their TTL (`expires_at`) has passed.
    *   Check CloudWatch for `MemoryManager` errors related to DynamoDB provisioned throughput exceptions (ThrottlingException).
*   **Resolution**: If throttled, temporarily increase DynamoDB Read Capacity Units (RCUs). If data is missing prematurely, verify the TTL configuration logic in the `add_turn` method.

## 3. Cache Miss Storms
*   **Symptom**: High CPU load on the cluster and elevated API latency, accompanied by a near 0% cache hit rate in Redis.
*   **Diagnosis**:
    *   Examine the incoming requests. Are clients injecting dynamic, non-cacheable data (like current timestamps) directly into the raw prompts instead of using template variables?
    *   Check if the Redis eviction policy (LRU) is aggressively purging data due to memory limits.
*   **Resolution**: Educate client teams to separate dynamic variables from static templates. If Redis is full, increase the instance size or decrease the cache TTL.

## 4. Token Budget Overflows
*   **Symptom**: The platform returns a 400 error indicating it cannot assemble the context within the specified bounds.
*   **Diagnosis**:
    *   Review the `TokenBudgetAllocation` logs. This occurs when the `System Prompt` + `User Prompt` (which have guaranteed minimum budgets) exceed the *total* available context window.
*   **Resolution**: The client application must provide shorter prompts, or the platform configuration must be updated to target an LLM with a larger context window.

## 5. Compression Quality Degradation
*   **Symptom**: Context fits the budget, but the LLM provides poor answers because vital information was stripped out during compression.
*   **Diagnosis**:
    *   Review the `compression_ratio` metric. Ratios below 0.3 (removing 70% of text) often result in coherence loss.
    *   Analyze the TF-IDF scoring logs to see which sentences were discarded.
*   **Resolution**: Adjust the Proportional Budget Allocation to give RAG documents a higher priority percentage. Consider switching to a less aggressive compression algorithm if CPU overhead allows.

## 6. Template Rendering Errors
*   **Symptom**: API returns 500 errors during the template rendering phase.
*   **Diagnosis**:
    *   Check logs for `KeyError` or `ValueError` in the `PromptTemplateEngine`. This happens when a template expects a variable (e.g., `{{ user_name }}`) that is missing from the request payload.
*   **Resolution**: Ensure client applications are passing all required variables. Validate template schemas upon deployment to catch missing variable definitions early.
