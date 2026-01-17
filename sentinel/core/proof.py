import hashlib
import json
import time
from typing import Dict, Any

class ProofGenerator:
    @staticmethod
    def generate_proof(trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wraps the execution trace into a cryptographically verifiable proof.
        """
        # Canonicalize the trace to ensure consistent hashing
        trace_json = json.dumps(trace, sort_keys=True)
        trace_hash = hashlib.sha256(trace_json.encode('utf-8')).hexdigest()
        
        proof = {
            "version": "1.0",
            "timestamp": time.time(),
            "trace": trace,
            "trace_hash": trace_hash,
            # In a real system, we would sign this hash with a private key
            "signature_mock": f"sig_{trace_hash[:16]}" 
        }
        
        return proof

    @staticmethod
    def verify_proof(proof: Dict[str, Any]) -> bool:
        """
        Verifies the integrity of the proof.
        """
        trace = proof.get("trace")
        target_hash = proof.get("trace_hash")
        
        if not trace or not target_hash:
            return False
            
        recalculated_hash = hashlib.sha256(json.dumps(trace, sort_keys=True).encode('utf-8')).hexdigest()
        
        return recalculated_hash == target_hash
