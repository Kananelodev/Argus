from pathlib import Path
from typing import Optional, Dict, Any
from .hasher import ModelHasher
from .constraints import ConstraintEngine
from .proof import ProofGenerator
import time

class SecureRuntime:
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        # Calculate model hash on initialization to "lock" it
        self.model_hash = ModelHasher.hash_file(self.model_path)
        
    def execute(self, input_data: str, constraints: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Executes the model with the given input and constraints.
        Returns a Cryptographic Proof of execution.
        """
        start_time = time.time()
        
        # 1. Input Hashing
        input_hash = ModelHasher.hash_string(input_data)
        
        # 2. Constraint Checking
        constraint_engine = ConstraintEngine(constraints)
        # Validate model is allowed (if policy exists)
        constraint_engine.validate_model(self.model_hash)
        # Validate input
        constraint_engine.validate_input(input_data)
        
        # 3. Execution (Simulated for MVP)
        # In a real scenario, this would call the actual model inference
        # For now, we simulate work
        time.sleep(0.1) 
        
        # SMART SIMULATION FOR DEMO SCENARIOS
        if "Credit Score" in input_data:
            output = "SYS: LOAN_APPROVED | SCORE: 98.2 | REASON: Strong Credit History & Income Ratio | LIMIT: $25,000"
        elif "Chest Pain" in input_data:
            output = "TRIAGE: PRIORITY_1_RED | ACTION: IMMEDIATE_ER_ADMISSION | SUSPICION: ACUTE_CORONARY_SYNDROME"
        else:
            output = f"Processed [{input_data}] by model [{self.model_hash[:8]}...]"
        
        execution_time = time.time() - start_time
        
        # 4. Generate Trace
        trace = {
            "model_hash": self.model_hash,
            "input_hash": input_hash,
            "constraints": constraints,
            "output": output,
            "execution_time_ms": int(execution_time * 1000),
            "executed_at": time.time()
        }
        
        # 5. Generate Proof
        proof = ProofGenerator.generate_proof(trace)
        
        return proof
