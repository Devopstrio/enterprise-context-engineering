from __future__ import annotations

import time
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from context_engineering.assembler.context_assembler import AssembledContext, ContextAssemblyRequest
from context_engineering.budget.token_budget_optimizer import TokenBudgetAllocation
from context_engineering.compressor.context_compressor import CompressionResult
from context_engineering.templates.prompt_template_engine import RenderedTemplate

router = APIRouter()


class MemoryTurnRequest(BaseModel):
    role: str
    content: str


class CompressRequest(BaseModel):
    text: str
    target_tokens: int


class TemplateRenderRequest(BaseModel):
    template_id: str
    variables: dict[str, str]


class BudgetEstimateRequest(BaseModel):
    max_tokens: int
    system_prompt: str
    user_input: str


@router.get("/health")
def health_check() -> dict[str, Any]:
    return {
        "service": "enterprise-context-engineering",
        "version": "1.0.0",
        "status": "ok",
        "uptime": time.time(),
    }


@router.post("/api/v1/context/assemble", response_model=AssembledContext)
def assemble_context(request: ContextAssemblyRequest, req: Request) -> AssembledContext:
    assembler = req.app.state.context_assembler
    return cast(AssembledContext, assembler.assemble(request))


@router.post("/api/v1/context/compress", response_model=CompressionResult)
def compress_context(request: CompressRequest, req: Request) -> CompressionResult:
    compressor = req.app.state.compressor
    return cast(CompressionResult, compressor.compress(request.text, request.target_tokens))


@router.get("/api/v1/memory/{session_id}")
def get_memory(session_id: str, max_tokens: int = 1000, req: Request | None = None) -> list[dict[str, Any]]:
    if req is None:
        return []
    memory = req.app.state.memory_manager
    return cast(list[dict[str, Any]], memory.retrieve_memory(session_id, max_tokens))


@router.post("/api/v1/memory/{session_id}")
def store_memory(session_id: str, request: MemoryTurnRequest, req: Request) -> dict[str, str]:
    memory = req.app.state.memory_manager
    memory.store_turn(session_id, request.role, request.content)
    return {"status": "success"}


@router.delete("/api/v1/memory/{session_id}")
def clear_memory(session_id: str, req: Request) -> dict[str, str]:
    memory = req.app.state.memory_manager
    memory.clear_session(session_id)
    return {"status": "success"}


@router.post("/api/v1/templates/render", response_model=RenderedTemplate)
def render_template(request: TemplateRenderRequest, req: Request) -> RenderedTemplate:
    engine = req.app.state.template_engine
    try:
        return cast(RenderedTemplate, engine.render_template(request.template_id, request.variables))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/v1/templates")
def list_templates(req: Request) -> dict[str, str]:
    engine = req.app.state.template_engine
    return cast(dict[str, str], engine.list_templates())


@router.post("/api/v1/budget/estimate", response_model=TokenBudgetAllocation)
def estimate_budget(request: BudgetEstimateRequest, req: Request) -> TokenBudgetAllocation:
    opt = req.app.state.budget_optimizer
    sys_tokens = opt.estimate_tokens(request.system_prompt)
    user_tokens = opt.estimate_tokens(request.user_input)
    return cast(TokenBudgetAllocation, opt.allocate_budget(request.max_tokens, sys_tokens, user_tokens))


@router.get("/api/v1/audit/events")
def get_audit_events(limit: int = 100, req: Request | None = None) -> list[dict[str, Any]]:
    if req is None:
        return []
    logger = req.app.state.audit_logger
    return cast(list[dict[str, Any]], logger.get_recent_events(limit))
