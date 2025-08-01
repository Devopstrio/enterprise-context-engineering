# Frequently Asked Questions (FAQ)

## What is Context Engineering?
Context Engineering is the specialized discipline of managing, assembling, and optimizing the information (context) sent to a Large Language Model (LLM). As enterprise applications use larger prompts, longer conversation histories, and more extensive RAG (Retrieval-Augmented Generation) data, they frequently hit the maximum token limits of the LLMs. The Context Engineering Platform acts as an intelligent intermediary to prioritize and compress this data, ensuring successful and accurate AI responses.

## How does the Token Budget Allocation work?
We use a **Proportional Budget Allocation** strategy. Instead of setting hard limits (e.g., "Memory is always 1000 tokens"), we assign percentages based on the total capacity of the target LLM.
For example, if the LLM allows 8,000 tokens, the budget might be configured as:
*   User Prompt: 20% (1,600 tokens)
*   System Prompt: 10% (800 tokens)
*   RAG Data: 40% (3,200 tokens)
*   Memory: 30% (2,400 tokens)
If an application switches to a model with a 32,000 token limit, the platform automatically scales these allocations proportionally.

## What happens if the context is still too large after allocation?
This triggers the **Context Compressor**. If the conversation memory or RAG data exceeds its assigned budget, the platform applies an extractive compression algorithm (TF-IDF). It scores every sentence based on its relevance to the current user query and selectively removes the least relevant sentences until the text fits perfectly within its allocated token budget.

## How is compression quality measured?
Compression quality is monitored via the `compression_ratio` metric, which is logged for every request. It represents `(final_tokens / original_tokens)`.
*   A ratio of `1.0` means no compression occurred.
*   A ratio of `0.8` is generally safe and retains high fidelity.
*   A ratio below `0.3` indicates aggressive compression. If we see consistently low ratios in production, it usually signals that the upstream RAG system is retrieving too many irrelevant documents, or the application needs to transition to an LLM with a larger native context window.

## What is the Cache Hit Rate, and why does it matter?
Context assembly, particularly the token counting (`tiktoken`) and compression phases, is computationally expensive. We cache fully assembled contexts in Redis. If a user repeats a query (e.g., clicking "Regenerate Response" in a UI), the platform can serve the cached context in milliseconds, bypassing the CPU-heavy pipeline. Our target Cache Hit Rate in production is > 15%.

## How do I add custom prompt templates?
Templates are managed via the `PromptTemplateEngine`. You do not need to modify the codebase to add a template. You can use the administrative API endpoint `POST /api/v1/templates` to register a new Jinja2 formatted template.
Example payload:
```json
{
  "template_id": "financial-analyst",
  "content": "You are a financial analyst. Analyze the following data: {{ financial_data }}. The user asks: {{ user_query }}",
  "variables": ["financial_data", "user_query"]
}
```
Client applications then specify `"template_id": "financial-analyst"` in their assembly requests.
