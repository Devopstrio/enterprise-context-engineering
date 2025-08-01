# Capacity Planning Guide

## 1. Token Throughput Estimation
The primary metric for the Context Engineering platform is tokens processed per second (TPS).
*   **Average Request Profile**:
    *   System Prompt: 500 tokens
    *   RAG Context: 2500 tokens
    *   Memory History: 1500 tokens
    *   User Prompt: 100 tokens
    *   **Total per request**: ~4600 tokens
*   **Peak Load Estimate**: 500 requests per second (RPS).
*   **Total Peak TPS**: 500 RPS * 4600 tokens = 2,300,000 tokens/second.
*   *Note: Token counting (`tiktoken`) is CPU bound. Profiling indicates a single CPU core can process ~1M tokens/sec. We require a minimum of 3 cores purely for tokenization at peak load.*

## 2. Memory Consumption Per Session (DynamoDB)
DynamoDB capacity planning depends on the volume and velocity of conversation turns.
*   **Average Turn Size**: 300 tokens ≈ 1.2 KB of text data.
*   **Average Session Length**: 20 turns.
*   **Total Data per Session**: ~24 KB.
*   **DynamoDB Capacity Units**:
    *   **Write Capacity Units (WCU)**: 1 WCU = 1 KB/sec. A 1.2 KB turn requires 2 WCUs. At 500 RPS (assuming 50% are new turns), we need ~500 WCUs.
    *   **Read Capacity Units (RCU)**: 1 RCU = 4 KB/sec. Fetching a 24 KB history requires 6 RCUs. At 500 RPS, we need ~3000 RCUs.
*   **Recommendation**: Use DynamoDB On-Demand capacity for the first 30 days to establish baselines, then switch to Provisioned Capacity with Auto-Scaling (Target utilization: 70%) to optimize costs.

## 3. Redis Cache Sizing
The cache stores fully assembled context strings to bypass the assembly pipeline for repeated queries.
*   **Average Assembled Payload Size**: 4600 tokens ≈ 18 KB.
*   **Cache Retention (TTL)**: 1 hour (3600 seconds).
*   **Estimated Unique Cacheable Requests per Hour**: 100,000.
*   **Total Cache Memory Required**: 100,000 * 18 KB = 1.8 GB.
*   **Recommendation**: Provision a `cache.t4g.medium` (3.09 GB memory) to allow overhead for Redis operational processes and connection management.

## 4. Kubernetes Resource Requests
Based on CPU-bound tokenization and memory-efficient stateless processing:
*   **Pod Resource Requests**:
    *   `cpu`: 500m (Half a core)
    *   `memory`: 512Mi
*   **Pod Resource Limits**:
    *   `cpu`: 1000m (Full core to handle burst tokenization)
    *   `memory`: 1024Mi

## 5. HPA Scaling Thresholds
The Horizontal Pod Autoscaler (HPA) manages the replica count based on utilization.
*   **Min Replicas**: 3 (High Availability across Availability Zones).
*   **Max Replicas**: 20 (Protects against runaway scaling costs).
*   **Target CPU Utilization**: 60%. (CPU is the primary bottleneck due to the `ContextCompressor` and `TokenBudgetOptimizer` operations).
*   **Target Memory Utilization**: 80%. (Memory footprint is generally stable; spikes indicate potential memory leaks rather than standard load).
