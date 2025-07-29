import pytest

def test_budget_allocation_default(budget_optimizer):
    alloc = budget_optimizer.allocate_budget(1000, 100, 100)
    assert alloc.system_prompt_tokens == 100
    assert alloc.user_input_tokens == 100
    assert alloc.total_allocated <= 1000

def test_budget_allocation_large_system_prompt(budget_optimizer):
    alloc = budget_optimizer.allocate_budget(1000, 800, 100)
    assert alloc.system_prompt_tokens == 800
    assert alloc.memory_tokens + alloc.retrieval_tokens <= 100

def test_budget_allocation_small_window(budget_optimizer):
    alloc = budget_optimizer.allocate_budget(100, 100, 50)
    assert alloc.total_allocated == 150 # Exceeds budget, but they are fixed

def test_estimate_tokens(budget_optimizer):
    tokens = budget_optimizer.estimate_tokens("hello world")
    assert tokens == 2

def test_budget_does_not_exceed_max(budget_optimizer):
    alloc = budget_optimizer.allocate_budget(200000, 100, 100)
    assert alloc.total_allocated <= budget_optimizer.max_context_tokens
