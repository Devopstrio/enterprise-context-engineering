<p align="center">
  <img src="images/architecture_drawio.png" alt="Enterprise Context Engineering — Architecture" width="900"/>
</p>

<h1 align="center">Enterprise Context Engineering</h1>

<p align="center">
  <strong>Production-grade context window assembly, conversation memory management, token budget optimization, context compression, prompt template rendering, and context audit logging for enterprise LLM applications.</strong>
</p>

<p align="center">
  <a href="https://github.com/Devopstrio/enterprise-context-engineering/actions/workflows/ci.yaml"><img src="https://github.com/Devopstrio/enterprise-context-engineering/actions/workflows/ci.yaml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Devopstrio/enterprise-context-engineering/actions/workflows/release.yaml"><img src="https://github.com/Devopstrio/enterprise-context-engineering/actions/workflows/release.yaml/badge.svg" alt="Release"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/terraform-%3E%3D1.6-purple" alt="Terraform >=1.6">
  <img src="https://img.shields.io/badge/kubernetes-1.28%2B-326CE5" alt="Kubernetes 1.28+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT">
</p>

---

## Overview

**Enterprise Context Engineering** is the specialized platform layer that manages how context windows are assembled, optimized, compressed, cached, and delivered to LLM inference endpoints. It sits between your application logic and the LLM provider, ensuring every inference call receives a maximally effective context window within the model's token limits.

This platform solves critical enterprise challenges:

| Challenge | Solution |
|-----------|----------|
| **Token budget waste** | Proportional budget allocation across system prompts, memory, RAG documents, and user input |
| **Context window overflow** | Extractive compression that preserves semantic density while reducing token count |
| **Memory management at scale** | Sliding window conversation memory with token-bounded retrieval per session |
| **RAG document ranking** | Relevance-scored document selection with deduplication and budget-aware truncation |
| **Prompt consistency** | Versioned prompt templates with variable injection and audit trails |
| **Repeated context assembly** | TTL-based context caching with LRU eviction for high-throughput workloads |
| **Compliance & observability** | Structured audit logging of every assembly decision for regulatory review |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Client Applications                              │
│              (Chat UI · Agent Orchestrator · Batch Inference)            │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │ POST /api/v1/context/assemble
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                               │
│                  Health · Assembly · Memory · Templates                   │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────┐  ┌────────────────┐  ┌──────────────┐
│   Context   │  │    Context     │  │   Prompt     │
│   Cache     │  │   Assembler    │  │  Template    │
│  (Redis)    │  │  (Orchestrator)│  │   Engine     │
└──────┬──────┘  └───────┬────────┘  └──────────────┘
       │                 │
       │     ┌───────────┼───────────┬──────────────┐
       │     ▼           ▼           ▼              ▼
       │ ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ │ Token  │ │ Memory   │ │Retrieval │ │ Context  │
       │ │ Budget │ │ Manager  │ │Integrator│ │Compressor│
       │ │Optimizer│ │(DynamoDB)│ │  (RAG)   │ │          │
       │ └────────┘ └──────────┘ └──────────┘ └──────────┘
       │                                          │
       └──────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Context Audit Logger │
              │    (CloudWatch)       │
              └───────────────────────┘
```

---

## Core Components

### Context Assembler (`src/context_engineering/assembler/`)
The orchestration engine that constructs optimized context windows by coordinating all sub-components. Accepts a `ContextAssemblyRequest` containing system prompt, user input, session ID, model configuration, retrieval documents, and tool outputs. Returns a fully assembled context with metadata including token counts, budget allocation, and assembly decisions.

### Memory Manager (`src/context_engineering/memory/`)
Manages per-session conversation history with sliding window eviction and token-bounded retrieval. Stores conversation turns (role, content, timestamp, token count) and retrieves the most recent turns that fit within the allocated memory token budget.

### Token Budget Optimizer (`src/context_engineering/budget/`)
Allocates the model's context window across competing sections (system prompt, conversation memory, RAG documents, user input) using proportional distribution. Fixed allocations (system prompt, user input) are reserved first, then remaining tokens are distributed between memory and retrieval based on configurable ratios.

### Context Compressor (`src/context_engineering/compressor/`)
Implements extractive compression when assembled context exceeds the token budget. Scores sentences by position, length, and keyword density, then selects top-scored sentences until the target token count is reached.

### Prompt Template Engine (`src/context_engineering/templates/`)
Manages versioned prompt templates with `{{variable_name}}` placeholder syntax. Ships with built-in templates (`default_system`, `rag_augmented`, `conversational`) and supports custom template registration.

### Context Cache (`src/context_engineering/cache/`)
TTL-based caching layer for assembled context windows. Generates cache keys from content hashes and serves cached results for repeated or similar queries, reducing latency and compute cost.

### Context Audit Logger (`src/context_engineering/audit/`)
Structured JSON logging of all context assembly decisions using `structlog`. Records budget allocations, memory retrievals, compression events, and cache interactions for compliance and debugging.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check (name, version, status, uptime) |
| `POST` | `/api/v1/context/assemble` | Assemble a complete context window from multi-source inputs |
| `POST` | `/api/v1/context/compress` | Compress text to fit within a target token count |
| `GET` | `/api/v1/memory/{session_id}` | Retrieve conversation memory for a session |
| `POST` | `/api/v1/memory/{session_id}` | Store a new conversation turn |
| `DELETE` | `/api/v1/memory/{session_id}` | Clear all memory for a session |
| `POST` | `/api/v1/templates/render` | Render a prompt template with variable substitution |
| `GET` | `/api/v1/templates` | List all registered prompt templates |
| `GET` | `/api/v1/budget/estimate` | Estimate token budget allocation for given inputs |
| `GET` | `/api/v1/audit/events` | Retrieve recent context audit events |

### Example: Assemble Context

```bash
curl -X POST http://localhost:8080/api/v1/context/assemble \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt": "You are a helpful enterprise assistant.",
    "user_input": "Summarize Q3 revenue trends from the uploaded reports.",
    "session_id": "sess-abc-123",
    "model_name": "gpt-4-turbo",
    "max_tokens": 128000,
    "retrieval_documents": [
      {
        "content": "Q3 revenue reached $4.2B, a 12% increase over Q2...",
        "source": "financial-reports/q3-2024.pdf",
        "relevance_score": 0.94
      }
    ]
  }'
```

### Example: Token Budget Estimation

```bash
curl "http://localhost:8080/api/v1/budget/estimate?max_tokens=128000&system_prompt_tokens=500&user_input_tokens=200"
```

---

## Project Structure

```
enterprise-context-engineering/
├── src/context_engineering/       # Python application source
│   ├── api/                       # FastAPI routes and request/response models
│   ├── assembler/                 # Context window assembly orchestration
│   ├── audit/                     # Structured context audit logging
│   ├── budget/                    # Token budget optimization and allocation
│   ├── cache/                     # TTL-based context caching (Redis)
│   ├── compressor/                # Extractive context compression
│   ├── config/                    # Pydantic Settings configuration
│   ├── memory/                    # Conversation memory management
│   ├── retrieval/                 # RAG document ranking and integration
│   ├── templates/                 # Versioned prompt template engine
│   └── main.py                    # FastAPI application entry point
├── tests/                         # Comprehensive test suite
│   ├── unit/                      # Unit tests for each component
│   ├── integration/               # Integration tests for assembly pipeline
│   └── api/                       # API endpoint tests
├── terraform/                     # OpenTofu/Terraform IaC
│   └── modules/                   # DynamoDB, ElastiCache, CloudWatch, VPC
├── deployment/kubernetes/         # Kustomize-based Kubernetes manifests
│   ├── base/                      # Base deployment, service, HPA, PDB, NetworkPolicy
│   └── overlays/                  # Environment-specific patches (dev/staging/prod)
├── .github/workflows/             # CI/CD pipelines (lint, test, security, deploy)
├── docs/                          # Enterprise documentation suite
│   ├── architecture/              # HLD, LLD, SDD, ADRs
│   ├── deployment/                # Deployment, Capacity Planning, DR guides
│   ├── operations/                # Runbook, Support Handover, Troubleshooting
│   ├── security/                  # Security Hardening, Production Checklist
│   ├── implementation/            # Implementation Guide
│   ├── governance/                # Repository Governance Guide
│   ├── getting-started/           # Getting Started, FAQ
│   └── roadmap/                   # Product Roadmap
├── architecture/                  # Mermaid architecture diagrams (.mmd)
├── examples/                      # Example API payloads
├── Dockerfile                     # Multi-stage production Docker build
├── docker-compose.yml             # Local development stack
└── pyproject.toml                 # PEP 621 project configuration
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for local development)
- OpenTofu/Terraform >= 1.6 (for infrastructure provisioning)
- kubectl & Kustomize (for Kubernetes deployment)

### Local Development

```bash
# Clone the repository
git clone https://github.com/Devopstrio/enterprise-context-engineering.git
cd enterprise-context-engineering

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Run the development server
uvicorn src.context_engineering.main:app --host 0.0.0.0 --port 8080 --reload

# Run the test suite
pytest --cov=src/context_engineering --cov-report=term-missing

# Run with Docker Compose (includes Redis)
docker-compose up --build
```

### Infrastructure Deployment

```bash
# Initialize and deploy infrastructure
cd terraform
tofu init
tofu plan -var="environment=staging" -out=tfplan
tofu apply tfplan

# Deploy to Kubernetes
cd ../deployment/kubernetes
kubectl apply -k overlays/staging/
```

---

## Configuration

All configuration is managed via environment variables with the `CTX_ENG_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `CTX_ENG_ENVIRONMENT` | `development` | Deployment environment |
| `CTX_ENG_LOG_LEVEL` | `INFO` | Logging level |
| `CTX_ENG_PORT` | `8080` | API server port |
| `CTX_ENG_MAX_CONTEXT_TOKENS` | `128000` | Maximum context window size |
| `CTX_ENG_SYSTEM_PROMPT_BUDGET_PCT` | `0.15` | System prompt token budget percentage |
| `CTX_ENG_MEMORY_BUDGET_PCT` | `0.30` | Conversation memory token budget percentage |
| `CTX_ENG_RETRIEVAL_BUDGET_PCT` | `0.35` | RAG retrieval token budget percentage |
| `CTX_ENG_USER_INPUT_BUDGET_PCT` | `0.20` | User input token budget percentage |
| `CTX_ENG_MEMORY_MAX_TURNS` | `50` | Maximum conversation turns to store |
| `CTX_ENG_COMPRESSION_TARGET_RATIO` | `0.5` | Target compression ratio |
| `CTX_ENG_CACHE_TTL_SECONDS` | `300` | Context cache TTL in seconds |
| `CTX_ENG_REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `CTX_ENG_ENABLE_AUDIT_LOGGING` | `true` | Enable context audit logging |

---

## Infrastructure

### AWS Resources (OpenTofu)

| Resource | Module | Purpose |
|----------|--------|---------|
| DynamoDB Table | `terraform/modules/context_store` | Conversation memory persistence with TTL and GSI |
| ElastiCache Redis | `terraform/modules/vector_cache` | Sub-millisecond context cache with replication |
| CloudWatch Log Group | `terraform/modules/audit_logs` | Context audit log export with KMS encryption |
| VPC + Subnets | `terraform/modules/network` | Private networking with VPC endpoints |

### Kubernetes Resources

| Resource | Description |
|----------|-------------|
| Deployment | 3 replicas, security-hardened (non-root, read-only rootfs) |
| HPA | Auto-scale 3–20 pods (CPU 70%, Memory 80%) |
| PDB | Minimum 2 pods available during disruptions |
| NetworkPolicy | Ingress restricted to gateway namespace |
| Service | ClusterIP on port 8080 |

---

## Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# API tests
pytest tests/api/ -v

# Full suite with coverage
pytest --cov=src/context_engineering --cov-report=html

# Type checking
mypy src/context_engineering/

# Linting
ruff check src/ tests/
```

---

## Documentation

| Document | Location |
|----------|----------|
| High-Level Design | [`docs/architecture/HighLevelDesign.md`](docs/architecture/HighLevelDesign.md) |
| Low-Level Design | [`docs/architecture/LowLevelDesign.md`](docs/architecture/LowLevelDesign.md) |
| Solution Design Document | [`docs/architecture/SolutionDesignDocument.md`](docs/architecture/SolutionDesignDocument.md) |
| Architecture Decision Records | [`docs/architecture/ArchitectureDecisionRecords.md`](docs/architecture/ArchitectureDecisionRecords.md) |
| Deployment Guide | [`docs/deployment/DeploymentGuide.md`](docs/deployment/DeploymentGuide.md) |
| Capacity Planning | [`docs/deployment/CapacityPlanningGuide.md`](docs/deployment/CapacityPlanningGuide.md) |
| Disaster Recovery | [`docs/deployment/DisasterRecoveryGuide.md`](docs/deployment/DisasterRecoveryGuide.md) |
| Operational Runbook | [`docs/operations/OperationalRunbook.md`](docs/operations/OperationalRunbook.md) |
| Troubleshooting Guide | [`docs/operations/TroubleshootingGuide.md`](docs/operations/TroubleshootingGuide.md) |
| Security Hardening | [`docs/security/SecurityHardeningGuide.md`](docs/security/SecurityHardeningGuide.md) |
| Production Checklist | [`docs/security/ProductionChecklist.md`](docs/security/ProductionChecklist.md) |
| Getting Started | [`docs/getting-started/GettingStarted.md`](docs/getting-started/GettingStarted.md) |
| FAQ | [`docs/getting-started/FAQ.md`](docs/getting-started/FAQ.md) |

---

## Ecosystem Integration

This repository is part of the **Devopstrio Enterprise AI & Multi-Cloud Landing Zone** ecosystem:

| Repository | Integration |
|-----------|-------------|
| [`prompt-router`](https://github.com/Devopstrio/prompt-router) | Routes prompts to this service for context assembly before LLM inference |
| [`gateway-observability`](https://github.com/Devopstrio/gateway-observability) | Collects context assembly metrics and traces |
| [`gateway-security`](https://github.com/Devopstrio/gateway-security) | Enforces authentication and authorization on context assembly endpoints |

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <sub>Built with precision by <a href="https://github.com/Devopstrio">Devopstrio</a> — Enterprise AI Platform Engineering</sub>
</p>
