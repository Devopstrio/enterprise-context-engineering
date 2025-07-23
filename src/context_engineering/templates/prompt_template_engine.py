from typing import Dict, Any, List
from pydantic import BaseModel
import re
import tiktoken

class RenderedTemplate(BaseModel):
    rendered_text: str
    template_id: str
    version: str
    variables_used: List[str]
    token_count: int

class PromptTemplateEngine:
    """Manages versioned prompt templates with variable placeholders."""

    def __init__(self):
        self._templates: Dict[str, Dict[str, Any]] = {}
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def register_template(self, template_id: str, version: str, template_text: str, variables: List[str]) -> None:
        self._templates[template_id] = {
            "version": version,
            "text": template_text,
            "variables": variables
        }

    def render_template(self, template_id: str, variables_dict: Dict[str, str]) -> RenderedTemplate:
        if template_id not in self._templates:
            raise ValueError(f"Template {template_id} not found.")

        template = self._templates[template_id]
        text = template["text"]
        used_vars = []

        for var in template["variables"]:
            placeholder = f"{{{{{var}}}}}"
            if placeholder in text:
                val = variables_dict.get(var, "")
                text = text.replace(placeholder, str(val))
                used_vars.append(var)
                
        token_count = len(self.tokenizer.encode(text))
        
        return RenderedTemplate(
            rendered_text=text,
            template_id=template_id,
            version=template["version"],
            variables_used=used_vars,
            token_count=token_count
        )

    def list_templates(self) -> Dict[str, str]:
        return {k: v["version"] for k, v in self._templates.items()}

    def get_template(self, template_id: str) -> Dict[str, Any]:
        if template_id not in self._templates:
            raise ValueError(f"Template {template_id} not found.")
        return self._templates[template_id]
