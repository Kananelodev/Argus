from pathlib import Path
from typing import Optional, Dict, Any
from .hasher import ModelHasher
from .constraints import ConstraintEngine, PrivacyEngine
from .proof import ProofGenerator
import time

class SecureRuntime:
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        # Calculate model hash on initialization to "lock" it
        self.model_hash = ModelHasher.hash_file(self.model_path)
        self.proof_generator = ProofGenerator()
        
    def execute(self, input_data: str, constraints: Dict[str, Any] = {}, metadata: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Executes the model with the given input and constraints.
        Returns a Cryptographic Proof of execution.
        """
        start_time = time.time()
        
        # 1. Input Hashing (Hash the ORIGINAL input to bind the proof to it privately)
        input_hash = ModelHasher.hash_string(input_data)
        
        # 2. Constraint & Privacy Checking
        constraint_engine = ConstraintEngine(constraints)
        constraint_engine.validate_model(self.model_hash)
        constraint_engine.validate_input(input_data)
        
        # Privacy: Redact sensitive data if privacy rules exist
        redacted_input = input_data
        zkp_proofs = []
        if "privacy" in constraints:
            redacted_input, zkp_proofs = PrivacyEngine.apply_privacy_rules(input_data, constraints["privacy"])
        
        # 3. Execution (Simulated for MVP)
        # We use ORIGINAL input for execution (the model sees the data), 
        # but the PROOF will only see redacted data.
        time.sleep(0.1) 
        
        # SMART SIMULATION FOR DEMO SCENARIOS
        if "Credit Score" in input_data or "score" in input_data:
            output = "SYS: LOAN_APPROVED | SCORE: Verified > Threshold | REASON: Strong Credit History"
        elif "Chest Pain" in input_data:
            output = "TRIAGE: PRIORITY_1_RED | ACTION: IMMEDIATE_ER_ADMISSION | SUSPICION: ACUTE_CORONARY_SYNDROME"
        else:
            output = f"Processed request by model [{self.model_hash[:8]}...]"
        
        execution_time = time.time() - start_time
        
        # 4. Generate Trace
        trace = {
            "model_hash": self.model_hash,
            "input_hash": input_hash, # Helper: can verify if you have original data
            "public_input": redacted_input, # Safe to share
            "zkp_proofs": zkp_proofs,
            "constraints": constraints,
            "output": output,
            "execution_time_ms": int(execution_time * 1000),
            "executed_at": time.time()
        }
        
        # Merge metadata (e.g. model_name)
        trace.update(metadata)
        
        # 5. Generate Proof
        proof = self.proof_generator.generate_proof(trace)
        
        return proof
