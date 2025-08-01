# Getting Started with Context Engineering

Welcome to the Enterprise Context Engineering Platform. This guide will help you run the service locally and execute your first context assembly request.

## 1. Prerequisites
Before beginning, ensure your local development environment has the following installed:
*   Python 3.11+
*   Poetry (Dependency Management)
*   Docker Desktop (for running local Redis and DynamoDB instances)
*   AWS CLI (configured with dummy credentials for local DynamoDB)

## 2. Local Installation
1.  **Clone the repository:**
    ```bash
    git clone git@github.com:enterprise/context-engineering.git
    cd context-engineering
    ```
2.  **Install dependencies:**
    ```bash
    poetry install
    ```
3.  **Start local infrastructure:**
    We provide a `docker-compose.yaml` file that spins up Redis and a local DynamoDB instance.
    ```bash
    docker-compose up -d
    ```
4.  **Initialize the database:**
    Run the setup script to create the necessary DynamoDB tables locally.
    ```bash
    poetry run python scripts/setup_local_dynamo.py
    ```

## 3. Running the Service
Start the FastAPI development server:
```bash
poetry run uvicorn assembler.main:app --reload --port 8080
```
The API is now available at `http://localhost:8080`. You can view the Swagger UI documentation at `http://localhost:8080/docs`.

## 4. Your First Context Assembly
Let's assemble a context payload. We will provide a simple user prompt, some mock RAG data, and assign a small token budget to force compression.

Execute the following `curl` command:
```bash
curl -X POST http://localhost:8080/api/v1/context/assemble \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "template_id": "default-chat",
    "target_model_limit": 100,
    "user_prompt": "What are the key features of the product?",
    "rag_documents": [
      {
        "content": "The product is incredibly fast. It features a completely redesigned user interface. We also added support for multi-tenant deployments. The API is RESTful and uses JSON. Security is handled via OAuth2.",
        "relevance_score": 0.95
      }
    ]
  }'
```

**Expected Result**:
You should receive a JSON response containing the `assembled_context`. Because the `target_model_limit` was artificially low (100 tokens), you should see in the `allocation_metadata` that the `ContextCompressor` activated and reduced the size of the `rag_documents` to fit the budget.

## 5. Running the Test Suite
To ensure your local environment is correctly configured, run the unit and integration tests:
```bash
poetry run pytest tests/
```
All tests should pass. You are now ready to begin development!
