# Architecture Decision Records (ADRs)

## ADR-001: Use tiktoken for Token Counting
*   **Status**: Accepted
*   **Context**: We need to accurately measure the size of context components to enforce budget limits before sending payloads to LLM providers.
*   **Decision**: We will use OpenAI's `tiktoken` library for precise token calculation rather than heuristic character counting.
*   **Consequences**: Ensures strict compliance with LLM context windows, eliminating API rejections for exceeding limits. Requires maintaining tokenizer models in the deployment environment.

## ADR-002: Extractive Compression over Abstractive
*   **Status**: Accepted
*   **Context**: When context components exceed their token budgets, they must be compressed.
*   **Decision**: We will implement extractive compression (selecting key sentences via algorithms like TF-IDF) instead of abstractive compression (using a smaller LLM to summarize).
*   **Consequences**: Extractive compression is deterministic, highly performant, and introduces no dependency on external AI services, keeping the critical path latency low. However, it may be less fluent than LLM-generated summaries.

## ADR-003: DynamoDB for Memory Store
*   **Status**: Accepted
*   **Context**: The platform must persist conversation history across stateless requests for memory management.
*   **Decision**: We will use Amazon DynamoDB as the primary data store for the `MemoryManager`.
*   **Consequences**: Provides a highly available, serverless database that scales seamlessly. We can leverage DynamoDB's native TTL feature to automatically expire old conversation turns, reducing storage costs and maintaining compliance.

## ADR-004: Redis for Context Cache
*   **Status**: Accepted
*   **Context**: Assembling complex contexts (especially involving template rendering and compression) can be CPU-intensive.
*   **Decision**: We will implement a caching layer using AWS ElastiCache Redis.
*   **Consequences**: Redis offers sub-millisecond read times. By caching fully assembled contexts using a hash of the input parameters as the key, we can significantly reduce latency and compute overhead for repeated queries.

## ADR-005: Proportional Budget Allocation
*   **Status**: Accepted
*   **Context**: The system must allocate token limits to various context sections (System, Memory, RAG, User).
*   **Decision**: We will use a proportional allocation strategy (percentages) rather than fixed token limits.
*   **Consequences**: This design is more resilient and adaptable. If we switch underlying LLMs (e.g., from an 8k to a 32k context window), the platform automatically scales the allocations without requiring configuration changes to every template.

## ADR-006: Structured Audit Logging with structlog
*   **Status**: Accepted
*   **Context**: For compliance and debugging, we need detailed records of how every context was assembled and compressed.
*   **Decision**: We will use `structlog` to emit structured JSON logs for all audit events.
*   **Consequences**: JSON logs can be easily ingested and parsed by AWS CloudWatch and downstream SIEM tools. This enables complex querying (e.g., finding all requests where compression exceeded 50%) and simplifies automated monitoring.
