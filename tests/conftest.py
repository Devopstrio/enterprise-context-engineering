import pytest
from fastapi.testclient import TestClient
from context_engineering.config.settings import ContextEngineSettings
from context_engineering.memory.memory_manager import MemoryManager
from context_engineering.budget.token_budget_optimizer import TokenBudgetOptimizer
from context_engineering.compressor.context_compressor import ContextCompressor
from context_engineering.templates.prompt_template_engine import PromptTemplateEngine
from context_engineering.cache.context_cache import ContextCache
from context_engineering.audit.context_audit_logger import ContextAuditLogger
from context_engineering.assembler.context_assembler import ContextAssembler
from context_engineering.retrieval.retrieval_integrator import RetrievalIntegrator
from context_engineering.main import app

@pytest.fixture
def settings():
    return ContextEngineSettings(environment="test")

@pytest.fixture
def memory_manager(settings):
    return MemoryManager(settings.memory_max_turns, settings.memory_sliding_window_size)

@pytest.fixture
def budget_optimizer(settings):
    return TokenBudgetOptimizer(settings.max_context_tokens, settings.memory_budget_pct, settings.retrieval_budget_pct)

@pytest.fixture
def compressor():
    return ContextCompressor()

@pytest.fixture
def template_engine():
    engine = PromptTemplateEngine()
    engine.register_template("default_system", "1.0", "{{system_prompt}}", ["system_prompt"])
    engine.register_template("rag_augmented", "1.0", "{{system_prompt}}\n\nContext Information:\n{{context}}", ["system_prompt", "context"])
    return engine

@pytest.fixture
def cache(settings):
    return ContextCache(settings.cache_ttl_seconds)

@pytest.fixture
def audit_logger():
    return ContextAuditLogger()

@pytest.fixture
def retrieval_integrator():
    return RetrievalIntegrator()

@pytest.fixture
def assembler(budget_optimizer, memory_manager, retrieval_integrator, compressor, template_engine, audit_logger):
    return ContextAssembler(
        budget_optimizer, memory_manager, retrieval_integrator, compressor, template_engine, audit_logger
    )

@pytest.fixture
def client():
    return TestClient(app)
