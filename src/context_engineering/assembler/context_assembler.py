from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from context_engineering.budget.token_budget_optimizer import TokenBudgetOptimizer, TokenBudgetAllocation
from context_engineering.memory.memory_manager import MemoryManager
from context_engineering.retrieval.retrieval_integrator import RetrievalIntegrator, RetrievalDocument
from context_engineering.compressor.context_compressor import ContextCompressor
from context_engineering.templates.prompt_template_engine import PromptTemplateEngine
from context_engineering.audit.context_audit_logger import ContextAuditLogger

class ContextAssemblyRequest(BaseModel):
    system_prompt: str
    user_input: str
    session_id: str
    model_name: str
    max_tokens: int
    retrieval_documents: List[RetrievalDocument] = []
    tool_outputs: List[Dict[str, Any]] = []

class AssembledContext(BaseModel):
    final_context: List[Dict[str, str]]
    total_tokens: int
    budget_allocation: TokenBudgetAllocation
    assembly_metadata: Dict[str, Any]

class ContextAssembler:
    """Orchestrates context window construction."""

    def __init__(
        self,
        budget_optimizer: TokenBudgetOptimizer,
        memory_manager: MemoryManager,
        retrieval_integrator: RetrievalIntegrator,
        compressor: ContextCompressor,
        template_engine: PromptTemplateEngine,
        audit_logger: ContextAuditLogger
    ):
        self.budget_optimizer = budget_optimizer
        self.memory_manager = memory_manager
        self.retrieval_integrator = retrieval_integrator
        self.compressor = compressor
        self.template_engine = template_engine
        self.audit_logger = audit_logger

    def assemble(self, request: ContextAssemblyRequest) -> AssembledContext:
        self.audit_logger.log_assembly_event(request.session_id, "ASSEMBLY_STARTED", {"model_name": request.model_name})

        sys_tokens = self.budget_optimizer.estimate_tokens(request.system_prompt)
        user_tokens = self.budget_optimizer.estimate_tokens(request.user_input)
        
        allocation = self.budget_optimizer.allocate_budget(request.max_tokens, sys_tokens, user_tokens)
        self.audit_logger.log_budget_allocation(request.session_id, allocation)

        # Retrieve Memory
        memory_turns = self.memory_manager.retrieve_memory(request.session_id, allocation.memory_tokens)
        self.audit_logger.log_assembly_event(request.session_id, "MEMORY_RETRIEVED", {"turn_count": len(memory_turns)})

        # Integrate Retrieval
        retrieval_result = self.retrieval_integrator.process(request.retrieval_documents, allocation.retrieval_tokens)
        self.audit_logger.log_assembly_event(request.session_id, "RETRIEVAL_INTEGRATED", {"selected": retrieval_result.documents_selected})

        # Compress if needed (applying to retrieval content in this design)
        compressed_retrieval_text = ""
        if retrieval_result.selected_documents:
            retrieval_text = "\\n\\n".join([doc.content for doc in retrieval_result.selected_documents])
            compression_res = self.compressor.compress(retrieval_text, allocation.retrieval_tokens)
            compressed_retrieval_text = compression_res.compressed_text
            self.audit_logger.log_compression_event(request.session_id, compression_res)
        
        # Rendering final prompt (simplified for standard completion or chat)
        # Using basic template logic if RAG
        sys_prompt = request.system_prompt
        if compressed_retrieval_text:
            rendered = self.template_engine.render_template("rag_augmented", {
                "system_prompt": request.system_prompt,
                "context": compressed_retrieval_text
            })
            sys_prompt = rendered.rendered_text
            
        final_context = [{"role": "system", "content": sys_prompt}]
        
        for turn in memory_turns:
            final_context.append({"role": turn["role"], "content": turn["content"]})
            
        final_context.append({"role": "user", "content": request.user_input})

        # Rough total tokens estimation
        total_tokens = self.budget_optimizer.estimate_tokens(sys_prompt) + \
                       sum(self.budget_optimizer.estimate_tokens(t["content"]) for t in memory_turns) + \
                       self.budget_optimizer.estimate_tokens(request.user_input)

        metadata = {
            "model": request.model_name,
            "memory_turns_included": len(memory_turns),
            "retrieval_docs_included": retrieval_result.documents_selected
        }

        self.audit_logger.log_assembly_event(request.session_id, "ASSEMBLY_COMPLETED", {"total_tokens": total_tokens})

        return AssembledContext(
            final_context=final_context,
            total_tokens=total_tokens,
            budget_allocation=allocation,
            assembly_metadata=metadata
        )
