from pydantic_settings import BaseSettings, SettingsConfigDict

class ContextEngineSettings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    port: int = 8080
    max_context_tokens: int = 128000
    default_model_context_window: int = 128000
    system_prompt_budget_pct: float = 0.15
    memory_budget_pct: float = 0.30
    retrieval_budget_pct: float = 0.35
    user_input_budget_pct: float = 0.20
    memory_max_turns: int = 50
    memory_sliding_window_size: int = 20
    compression_target_ratio: float = 0.5
    cache_ttl_seconds: int = 300
    redis_url: str = "redis://localhost:6379/0"
    enable_audit_logging: bool = True
    service_name: str = "enterprise-context-engineering"

    model_config = SettingsConfigDict(env_prefix="CTX_ENG_", env_file=".env")
