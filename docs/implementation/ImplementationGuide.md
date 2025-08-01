# Implementation Guide

## 1. Module Architecture Overview
The platform is built using Python 3.11 with FastAPI. The codebase is strictly typed and adheres to standard Clean Architecture principles to separate business logic from infrastructure concerns.
*   `assembler/`: Contains the core `ContextAssembler` service.
*   `memory/`: Interfaces for persistence. The `DynamoMemoryManager` is the primary implementation.
*   `retrieval/`: Handles parsing and scoring of inbound RAG data.
*   `budget/`: Contains the `TokenBudgetOptimizer` and allocation strategies.
*   `compressor/`: Contains abstract base classes for compression and the `TFIDFCompressor` implementation.
*   `templates/`: The `PromptTemplateEngine` powered by Jinja2.

## 2. Context Assembly Pipeline Walkthrough
To understand how to extend the platform, you must understand the primary data structure: `AssemblyRequest`.
When a request hits `POST /api/v1/context/assemble`, it is deserialized into an `AssemblyRequest`.
The pipeline executes sequentially:
1.  **Template Resolution**: The requested template ID is fetched from the DB, and variables are injected.
2.  **Memory Hydration**: `session_id` is used to pull the `List[ConversationTurn]`.
3.  **Budgeting**: The `TokenBudgetOptimizer` calculates limits based on the model specified in the `AssemblyRequest`.
4.  **Compression**: The `ContextCompressor` iterates over RAG and Memory data, applying the budget constraints.
5.  **Finalization**: The payload is formatted to the specific LLM provider's schema (e.g., OpenAI `messages` array).

## 3. Adding Custom Prompt Templates
Templates are not hardcoded; they are managed dynamically.
To add a new template during development:
1.  Navigate to `data/seed_templates.json`.
2.  Add a new entry:
    ```json
    {
      "template_id": "customer-support-v2",
      "system_prompt": "You are a helpful assistant. The customer's tier is {{ tier }}.",
      "variables": ["tier"],
      "default_model": "gpt-4-turbo"
    }
    ```
3.  Run the seed script: `python scripts/seed_db.py`.

## 4. Extending Compression Algorithms
The current `TFIDFCompressor` is effective but basic. To implement a new algorithm (e.g., a semantic density algorithm):
1.  Create a new file `compressor/semantic.py`.
2.  Inherit from the base class:
    ```python
    from compressor.base import BaseCompressor

    class SemanticCompressor(BaseCompressor):
        def compress(self, text: str, budget: int) -> str:
            # Implement custom logic here
            pass
    ```
3.  Register the new compressor in the `AssemblerFactory` located in `assembler/factory.py`.

## 5. Integrating New Retrieval Sources
Currently, the platform expects RAG data in a standard JSON format in the request body. If you need to integrate directly with a vector database (e.g., Pinecone) instead of relying on the client application to provide the data:
1.  Modify `AssemblyRequest` to accept a `query_string` instead of raw `rag_documents`.
2.  Implement a new class in `retrieval/pinecone_client.py`.
3.  Update the pipeline in `assembler/core.py` to execute the vector search *before* the budgeting phase.
