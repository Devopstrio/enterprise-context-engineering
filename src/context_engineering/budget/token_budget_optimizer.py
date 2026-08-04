import tiktoken
from pydantic import BaseModel


class TokenBudgetAllocation(BaseModel):
    system_prompt_tokens: int
    memory_tokens: int
    retrieval_tokens: int
    user_input_tokens: int
    total_allocated: int
    remaining_tokens: int


class TokenBudgetOptimizer:
    """Optimizes and allocates token budgets."""

    def __init__(self, max_context_tokens: int, memory_pct: float, retrieval_pct: float) -> None:
        self.max_context_tokens = max_context_tokens
        self.memory_pct = memory_pct
        self.retrieval_pct = retrieval_pct
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(self.tokenizer.encode(text))

    def allocate_budget(
        self,
        max_tokens: int,
        system_prompt_tokens: int,
        user_input_tokens: int,
    ) -> TokenBudgetAllocation:
        effective_max = min(max_tokens, self.max_context_tokens)

        system_budget = system_prompt_tokens
        user_budget = user_input_tokens

        fixed_tokens = system_budget + user_budget
        remaining = max(0, effective_max - fixed_tokens)

        total_ratio = self.memory_pct + self.retrieval_pct
        if total_ratio > 0 and remaining > 0:
            memory_ratio = self.memory_pct / total_ratio
            retrieval_ratio = self.retrieval_pct / total_ratio

            memory_budget = int(remaining * memory_ratio)
            retrieval_budget = int(remaining * retrieval_ratio)
        else:
            memory_budget = 0
            retrieval_budget = 0

        total_allocated = system_budget + user_budget + memory_budget + retrieval_budget
        final_remaining = max(0, effective_max - total_allocated)

        return TokenBudgetAllocation(
            system_prompt_tokens=system_budget,
            memory_tokens=memory_budget,
            retrieval_tokens=retrieval_budget,
            user_input_tokens=user_budget,
            total_allocated=total_allocated,
            remaining_tokens=final_remaining,
        )
