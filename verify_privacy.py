from sentinel.core.runtime import SecureRuntime
from sentinel.core.proof import ProofGenerator
import json
import os

# Create dummy model
if not os.path.exists("privacy_model.bin"):
    with open("privacy_model.bin", "w") as f:
        f.write("privacy model content")

print("--- STARTING PRIVACY ZKP TEST ---")

# 1. Define Privacy Rules
constraints = {
    "privacy": {
        "min_score": 700,
        "min_income": 40000
    }
}

# 2. Input Data (Sensitive)
sensitive_input = json.dumps({
    "score": 750,
    "income": 50000,
    "name": "Jane Doe"
})

print(f"Original Input: {sensitive_input}")

# 3. Execute
runtime = SecureRuntime("privacy_model.bin")
proof = runtime.execute(sensitive_input, constraints)

# 4. Inspect Proof
trace = proof['credentialSubject']['executionTrace']
public_input = trace['public_input']
zkps = trace['zkp_proofs']

print("\n[INSPECTING TRACE]")
print(f"Public Input in Trace: {public_input}")
print(f"ZKP Proofs: {zkps}")

# 5. Assertions
input_obj = json.loads(public_input)
if input_obj['score'] == "REDACTED_ZKP_VERIFIED":
    print("   [PASS] Score was redacted")
else:
    print(f"   [FAIL] Score was NOT redacted: {input_obj['score']}")

if "ZKP: Score >= 700 Verified" in zkps[0]:
    print("   [PASS] Score ZKP Present")
else:
    print("   [FAIL] Score ZKP Missing")

if ProofGenerator.verify_proof(proof):
    print("   [PASS] VC Signature Verified")
else:
    print("   [FAIL] VC Signature Failed")

print("--- END TEST ---")
