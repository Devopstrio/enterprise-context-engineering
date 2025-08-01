# Context Engineering Architecture Diagrams

This directory contains Mermaid (`.mmd`) diagrams illustrating the core architecture, data flows, and deployment topology of the Enterprise Context Engineering Platform.

## Diagram Index

1.  **[High-Level Architecture](high-level.mmd)**: Illustrates the system context. Shows how client applications interface with the API Gateway, and how the Context Assembler orchestrates the internal microservices (Memory, Budget, Compressor, Template) before sending the optimized payload to external LLM Providers.
2.  **[Assembly Flow Sequence](assembly-flow.mmd)**: A detailed sequence diagram mapping the step-by-step execution of the `POST /api/v1/context/assemble` endpoint. Highlights the critical caching layer, database hydration, budget allocation, conditional compression, and audit logging.
3.  **[Token Budget Allocation](budget-allocation.mmd)**: A pie chart demonstrating the Proportional Budget Allocation strategy. Provides a visual example of how an 8,000 token limit is dynamically distributed across System Prompts, User Prompts, RAG Context, and Conversation Memory.
4.  **[Deployment Topology](deployment-topology.mmd)**: Maps the physical infrastructure layout within the AWS Cloud. Details the ingress flow through the ALB to the Kubernetes EKS cluster, the horizontal scaling of API pods, and their connections to managed AWS services (ElastiCache Redis, DynamoDB, CloudWatch).

## Viewing Diagrams

These diagrams are written using [Mermaid syntax](https://mermaid.js.org/).
They can be rendered natively in GitHub, GitLab, or using local IDE plugins (e.g., Markdown Preview Mermaid Support for VS Code).
