from typing import Dict, Any, List
from pydantic import BaseModel

class ConstraintConfig(BaseModel):
    allowed_model_hashes: List[str] = []
    max_input_length: int = 1000
    allowed_modules: List[str] = []

class ConstraintEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = ConstraintConfig(**config)

    def validate_model(self, model_hash: str):
        if self.config.allowed_model_hashes and model_hash not in self.config.allowed_model_hashes:
            raise ValueError(f"Model hash {model_hash} is not allowed by policy.")

    def validate_input(self, input_data: str):
        if len(input_data) > self.config.max_input_length:
            raise ValueError(f"Input length {len(input_data)} exceeds limit of {self.config.max_input_length}")

    def validate_execution(self, trace: Dict[str, Any]):
        # Post-execution validation rules
        pass
