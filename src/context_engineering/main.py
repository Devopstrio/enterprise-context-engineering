import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from context_engineering.api.routes import router as api_router
from context_engineering.assembler.context_assembler import ContextAssembler
from context_engineering.audit.context_audit_logger import ContextAuditLogger
from context_engineering.budget.token_budget_optimizer import TokenBudgetOptimizer
from context_engineering.cache.context_cache import ContextCache
from context_engineering.compressor.context_compressor import ContextCompressor
from context_engineering.config.settings import ContextEngineSettings
from context_engineering.memory.memory_manager import MemoryManager
from context_engineering.retrieval.retrieval_integrator import RetrievalIntegrator
from context_engineering.templates.prompt_template_engine import PromptTemplateEngine

settings = ContextEngineSettings()

app = FastAPI(
    title=settings.service_name,
    description="Enterprise Context Engineering Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
memory_manager = MemoryManager(settings.memory_max_turns, settings.memory_sliding_window_size)
retrieval_integrator = RetrievalIntegrator()
budget_optimizer = TokenBudgetOptimizer(
    settings.max_context_tokens,
    settings.memory_budget_pct,
    settings.retrieval_budget_pct,
)
compressor = ContextCompressor()
template_engine = PromptTemplateEngine()
context_cache = ContextCache(settings.cache_ttl_seconds)
audit_logger = ContextAuditLogger()

context_assembler = ContextAssembler(
    budget_optimizer=budget_optimizer,
    memory_manager=memory_manager,
    retrieval_integrator=retrieval_integrator,
    compressor=compressor,
    template_engine=template_engine,
    audit_logger=audit_logger,
)

# Attach to app state
app.state.memory_manager = memory_manager
app.state.retrieval_integrator = retrieval_integrator
app.state.budget_optimizer = budget_optimizer
app.state.compressor = compressor
app.state.template_engine = template_engine
app.state.context_cache = context_cache
app.state.audit_logger = audit_logger
app.state.context_assembler = context_assembler


@app.on_event("startup")
async def startup_event() -> None:
    template_engine.register_template("default_system", "1.0", "{{system_prompt}}", ["system_prompt"])
    template_engine.register_template(
        "rag_augmented", "1.0", "{{system_prompt}}\n\nContext Information:\n{{context}}", ["system_prompt", "context"]
    )
    template_engine.register_template("conversational", "1.0", "You are a helpful assistant.\n{{system_prompt}}", ["system_prompt"])


app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("context_engineering.main:app", host="0.0.0.0", port=settings.port, reload=True)
