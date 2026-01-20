import hashlib
import json
import time
from typing import Dict, Any
from .identity import DIDManager

class ProofGenerator:
    def __init__(self, did_manager: DIDManager = None):
        self.did_manager = did_manager if did_manager else DIDManager()

    def generate_proof(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wraps the execution trace into a W3C Verifiable Credential.
        """
        # Canonicalize the trace to ensure consistent hashing
        trace_json = json.dumps(trace, sort_keys=True)
        trace_hash = hashlib.sha256(trace_json.encode('utf-8')).hexdigest()
        
        issuance_date = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        # VC Structure
        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/argus/v1"
            ],
            "type": ["VerifiableCredential", "AIExecutionCertificate"],
            "issuer": self.did_manager.did,
            "issuanceDate": issuance_date,
            "credentialSubject": {
                "id": f"urn:uuid:{trace_hash}", 
                "executionTrace": trace,
                "traceHash": trace_hash
            }
        }
        
        # Sign the credential
        signature = self.did_manager.sign_payload(credential)
        
        # Append Proof
        credential["proof"] = {
            "type": "Ed25519Signature2020",
            "created": issuance_date,
            "verificationMethod": self.did_manager.get_verification_method(),
            "proofPurpose": "assertionMethod",
            "jws": signature # Simplified JWS-like hex for hackathon
        }
        
        return credential

    @staticmethod
    def verify_proof(proof: Dict[str, Any]) -> bool:
        """
        Verifies the integrity of the VC.
        """
        # 1. Check Structure
        if "credentialSubject" not in proof or "proof" not in proof:
            return False
            
        # 2. Re-calculate Trace Hash
        trace = proof["credentialSubject"].get("executionTrace")
        target_hash = proof["credentialSubject"].get("traceHash")
        
        if not trace or not target_hash:
            return False
            
        recalculated_hash = hashlib.sha256(json.dumps(trace, sort_keys=True).encode('utf-8')).hexdigest()
        
        if recalculated_hash != target_hash:
            return False
            
        # 3. Verify Signature (Simulated for this step, would import pubkey from DID in real DID resolver)
        # In a real system we would resolve proof['issuer'] -> get pubkey -> verify proof['proof']['jws']
        # For now, we trust the hash integrity check.
        return True

