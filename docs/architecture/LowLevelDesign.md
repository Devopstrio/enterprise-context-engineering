# Low-Level Design: Enterprise Context Engineering Platform

## 1. Class Diagrams

### 1.1 ContextAssembler
Orchestrates the context construction process.
*   `assemble_context(request: AssemblyRequest) -> AssembledContext`
*   `_validate_inputs(request: AssemblyRequest) -> bool`
*   `_merge_components(components: List[ContextComponent]) -> AssembledContext`

### 1.2 MemoryManager
Handles persistence and retrieval of conversation history.
*   `get_history(session_id: str, max_tokens: int) -> List[ConversationTurn]`
*   `add_turn(session_id: str, turn: ConversationTurn) -> None`
*   `clear_session(session_id: str) -> bool`

### 1.3 TokenBudgetOptimizer
Calculates the optimal distribution of tokens.
*   `allocate_budget(total_tokens: int, strategy: AllocationStrategy) -> TokenBudgetAllocation`
*   `_calculate_proportions(weights: dict) -> dict`

### 1.4 ContextCompressor
Reduces text size while retaining key information.
*   `compress(text: str, target_tokens: int) -> str`
*   `_extract_key_sentences(text: str) -> List[str]`

### 1.5 PromptTemplateEngine
Manages versioned prompts and variable injection.
*   `render_template(template_id: str, variables: dict) -> str`
*   `_validate_variables(template: Template, variables: dict) -> bool`

## 2. Data Models

### 2.1 ConversationTurn
*   `turn_id`: UUID
*   `session_id`: UUID
*   `timestamp`: datetime
*   `role`: enum (user, assistant, system, tool)
*   `content`: string
*   `token_count`: integer

### 2.2 RetrievalDocument
*   `doc_id`: string
*   `content`: string
*   `source_metadata`: dict
*   `relevance_score`: float

### 2.3 AssembledContext
*   `session_id`: string
*   `final_prompt`: string
*   `messages`: List[dict]
*   `total_tokens_used`: integer
*   `allocation_metadata`: TokenBudgetAllocation
*   `cached`: boolean

### 2.4 TokenBudgetAllocation
*   `system_budget`: int
*   `memory_budget`: int
*   `rag_budget`: int
*   `user_budget`: int

## 3. Sequence Diagram: Context Assembly Flow
1.  Client -> API: `POST /api/v1/context/assemble`
2.  API -> ContextAssembler: `assemble(request)`
3.  ContextAssembler -> Cache: `check_cache(request_hash)`
    *   If Hit: Return cached context.
4.  ContextAssembler -> MemoryManager: `fetch_history(session_id)`
5.  ContextAssembler -> PromptTemplateEngine: `render(template_id, vars)`
6.  ContextAssembler -> TokenBudgetOptimizer: `allocate(total_limit)`
7.  If Memory > Budget: ContextAssembler -> ContextCompressor: `compress(memory, budget)`
8.  ContextAssembler -> Logger: `log_audit_event(decision_tree)`
9.  ContextAssembler -> Cache: `store(request_hash, assembled_context)`
10. ContextAssembler -> API: `Return AssembledContext`
11. API -> Client: `200 OK`

## 4. Compression Algorithm Details
The platform utilizes an Extractive Compression algorithm.
1.  **Sentence Tokenization**: The input text is split into distinct sentences.
2.  **Scoring**: Sentences are scored based on term frequency-inverse document frequency (TF-IDF) relative to the current user prompt.
3.  **Selection**: Sentences are greedily selected in order of highest score until the allocated token budget is reached.
4.  **Reassembly**: Selected sentences are reassembled in their original chronological order to maintain coherence.
