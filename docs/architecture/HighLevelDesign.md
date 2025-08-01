# High-Level Design: Enterprise Context Engineering Platform

## 1. System Context
The Enterprise Context Engineering Platform acts as the critical intermediary between upstream client applications and downstream Large Language Model (LLM) providers. Its primary responsibility is the dynamic construction, optimization, and management of context windows.

### 1.1 Actors
*   **Client Applications**: Enterprise applications (chatbots, agents, co-pilots) that submit prompts and conversational context.
*   **LLM Providers**: External AI services (e.g., OpenAI, Anthropic, Gemini) or self-hosted models that consume the assembled context.
*   **RAG Systems**: Enterprise document retrieval systems providing grounded knowledge context.

## 2. Container Architecture
The platform is composed of several specialized microservices and data stores:

### 2.1 Microservices
*   **API Gateway**: Exposes endpoints for context assembly and memory management.
*   **Context Assembler**: The orchestration engine coordinating the assembly pipeline.
*   **Memory Manager**: Interfaces with DynamoDB to retrieve and persist conversation history.
*   **Retrieval Integrator**: Merges RAG documents into the context window.
*   **Token Budget Optimizer**: Calculates and enforces token allocations.
*   **Context Compressor**: Reduces context size using extractive summarization techniques.
*   **Prompt Template Engine**: Injects dynamic variables into versioned prompt templates.

### 2.2 Data Stores
*   **DynamoDB**: Primary persistent store for conversation memory, offering sliding window history.
*   **ElastiCache Redis**: Fast TTL-based cache for frequently assembled contexts to minimize redundant processing.

## 3. Context Assembly Pipeline Flow
1.  **Ingestion**: Receive raw prompt, session ID, and RAG documents.
2.  **Memory Retrieval**: Fetch historical conversation turns via Memory Manager.
3.  **Template Rendering**: Evaluate prompt templates.
4.  **Budget Allocation**: Token Budget Optimizer assigns strict token limits to System Prompt, Memory, RAG Data, and User Prompt.
5.  **Compression (Conditional)**: If any segment exceeds its budget, Context Compressor applies extractive summarization.
6.  **Assembly**: The final payload is constructed.
7.  **Caching**: The assembled context is cached (Redis).
8.  **Audit Logging**: The assembly decision tree and token usage are logged to CloudWatch.

## 4. Token Budget Allocation Strategy
The platform employs a Proportional Budget Allocation strategy. Unlike fixed limits, this allows dynamic resizing based on the specific LLM's context window.
*   **System Prompt**: High priority, fixed budget.
*   **User Prompt**: Highest priority, dynamic but guaranteed minimum budget.
*   **RAG Documents**: Medium priority, proportional up to a cap.
*   **Conversation Memory**: Lowest priority, consumes the remaining budget (Sliding Window).

## 5. Integration Points
*   **Upstream**: Integrates via RESTful APIs (`POST /api/v1/context/assemble`).
*   **Downstream (LLM)**: Prepares payloads compliant with major LLM provider schemas (e.g., OpenAI Chat Completion format).
*   **Downstream (RAG)**: Accepts standard JSON structures representing retrieved chunks with relevance scores.
