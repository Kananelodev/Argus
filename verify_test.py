from sentinel.core.runtime import SecureRuntime
from sentinel.core.proof import ProofGenerator
from sentinel.storage.ipfs import IPFSStorage
import json
import os

# Create dummy model if not exists
if not os.path.exists("dummy_model.bin"):
    with open("dummy_model.bin", "w") as f:
        f.write("dummy model content")

print("--- STARTING VERIFICATION TEST ---")

# 1. Run
print("1. Executing Runtime...")
runtime = SecureRuntime("dummy_model.bin")
proof = runtime.execute("Test Input 123")
# print(json.dumps(proof, indent=2))

# 2. Store
print("2. Storing Proof...")
storage = IPFSStorage()
cid = storage.save_proof(proof)
print(f"   CID: {cid}")

# 3. Verify via CID
print("3. Verifying Authentic Proof...")
fetched_proof = storage.get_proof(cid)
if ProofGenerator.verify_proof(fetched_proof):
    print("   [PASS] Verification Successful")
else:
    print("   [FAIL] Verification Failed")

# 4. Tamper
print("4. Testing Tamper Detection...")
proof['trace']['output'] = "HACKED output that doesn't match hash"
# We save this tampered proof. The 'trace_hash' in the proof object 
# still matches the OLD trace, but the 'trace' content is new.
tampered_cid = storage.save_proof(proof)
fetched_tampered = storage.get_proof(tampered_cid)

if not ProofGenerator.verify_proof(fetched_tampered):
    print("   [PASS] Tamper Detection Successful (Verification correctly failed)")
else:
    print("   [FAIL] Tamper Detection Failed (Verification passed inappropriately)")

print("--- END TEST ---")
