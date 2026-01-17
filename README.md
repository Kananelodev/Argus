Argus // Technical Manual
Version: 1.1.0-Argus Status: Active/Hackathon

This document provides the deep technical specifications for the Argus infrastructure. It is intended for developers, security auditors, and system architects.

1. Security Architecture
1.1 The Trust Model
Argus operates on a "Trust but Verify" model, shifting to "Verify then Trust".

Traditional AI: User -> API (Black Box) -> Result. (Trusts the API provider completely).
Argus: User -> Argus Node -> Proof -> Result. (Trusts the cryptographic proof).
1.2 Verification Flow
Pre-Execution State:
Model_Hash: SHA-256 hash of the binary weights file.
Input_Hash: SHA-256 hash of the prompt/input data.
Execution (The "Black Box"):
The Runtime isolates the process.
Outputs are captured via stdout interception.
Proof Generation:
A JSON object is constructed: { model_hash, input_hash, output, timestamp }.
A Digital Signature is appended. (MVP: Simulated Signature sig_hash).
Verification:
Verification function V(proof):
Recomputes 
H(proof.trace)
.
Asserts 
H(proof.trace) == proof.trace_hash
.
Asserts VerifySignature(proof.signature, proof.trace_hash, Public_Key).
2. Component Reference
2.1 Secure Runtime (sentinel.core.runtime)
The 
SecureRuntime
 class is the core execution wrapper.

runtime = SecureRuntime(model_path="path/to/model.bin")
result = runtime.execute(input_data="prompt", constraints={...})
Initialization: Calculates SHA-256 of model_path immediately. If the file changes on disk after init, the runtime must be restarted or it will continue using the loaded hash (or fail if checking per-run).
Constraints: max_input_length, allowed_model_hashes.
2.2 Storage Layer (sentinel.storage.ipfs)
Handles persistence to the decentralized web.

Driver: 
IPFSStorage
.
Method: 
save_proof(proof_dict) -> CID (str)
.
Fallback: If a local IPFS daemon (127.0.0.1:5001) is unreachable, it falls back to Local Mock Storage (sentinel_storage/) to ensure the demo continues.
3. API Reference
The Sentinel Node exposes a REST API for the Dashboard and remote clients.

POST /api/broadcast
Broadcasts a newly generated proof to the live feed.

Payload: { "cid": "Qm...", "model_hash": "...", "type": "execution_proof" }
Response: { "status": "broadcasted" }
GET /api/feed
Retrieves the list of recent execution events (in-memory buffer of last 10).

Response: [ { "cid": "...", "server_time": 12345.67 }, ... ]
GET /api/proof/{cid}
Fetches and verifies a proof by CID.

Response:
{
  "proof": { ...full_proof_json... },
  "is_valid": true/false
}
Note: The API performs server-side verification logic before returning.
4. CLI Reference
run
Execute a model and generate a proof.

python -m sentinel.cli run [OPTIONS] MODEL_PATH INPUT_DATA
--store / --no-store: Upload proof to IPFS (Default: True).
--simulate-tamper: DEMO ONLY. Intentionally corrupts the output to fail verification.
verify
Verify the integrity of a proof.

python -m sentinel.cli verify [OPTIONS] CID
CID
: The IPFS Content Identifier OR a local file path to a JSON proof.
Output: Returns a PASS/FAIL table and exit code.
5. Development Setup
Requirements: Python 3.8+, IPFS Node (Optional).
Test Suite: 
verify_test.py
 covers the end-to-end lifecycle (Run -> Store -> Fetch -> Verify -> Tamper).
